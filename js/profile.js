/**
 * 玄机算命网 - 个人中心模块 (v1.5.1)
 * 重构：VIP 代码已提取到 js/vip.js → window.VipModule
 * 保留：Profile / Avatar / Realname / Edit / Logout
 */
window.Profile = (function() {
    'use strict';

    // ═══════════════════════════════════════════
    //  SECTION: State
    // ═══════════════════════════════════════════
    var state = {
        profile: null,    // GET /api/profile 返回的完整用户对象
        realname: null,   // GET /api/profile/realname-status 返回的实名状态
        loading: false,
        rnIdcardBase64: '',  // 身份证照片临时存储
        rnUploadOnly: false  // 已认证用户补传模式
    };

    // ═══════════════════════════════════════════
    //  SECTION: DOM Cache
    // ═══════════════════════════════════════════
    var dom = {};

    function cacheDom() {
        // Profile header
        dom.profileName     = document.getElementById('profileName');
        dom.profileInfo     = document.getElementById('profileInfo');
        dom.profileUid      = document.getElementById('profileUid');
        dom.sidebarUserName = document.getElementById('sidebarUserName');

        // Tags
        dom.tagVerified     = document.getElementById('tagVerified');
        dom.tagIdcard       = document.getElementById('tagIdcard');

        // Stats
        dom.divinationCount = document.getElementById('divinationCount');
        dom.favoriteCount   = document.getElementById('favoriteCount');
        dom.daysCount       = document.getElementById('daysCount');

        // Profile edit
        dom.editProfileModal  = document.getElementById('editProfileModal');
        dom.editNickname    = document.getElementById('editNickname');
        dom.editUsername    = document.getElementById('editUsername');
        dom.editPhone       = document.getElementById('editPhone');
        dom.editEmail       = document.getElementById('editEmail');
        dom.editBirthday    = document.getElementById('editBirthday');
        dom.editGender      = document.getElementById('editGender');
        dom.editProfileForm = document.getElementById('editProfileForm');

        // Avatar
        dom.avatarPickerModal = document.getElementById('avatarPickerModal');
        dom.avatarImg       = document.getElementById('avatarImg');
        dom.avatarDefault   = document.getElementById('avatarDefault');
        dom.avatarInput     = document.getElementById('avatarInput');

        // Realname
        dom.realnameModal       = document.getElementById('realnameModal');
        dom.rnVerifiedContent   = document.getElementById('realnameVerifiedContent');
        dom.rnFormContent       = document.getElementById('realnameFormContent');
        dom.rnName              = document.getElementById('rnName');
        dom.rnId                = document.getElementById('rnId');
        dom.rnRegion            = document.getElementById('rnRegion');
        dom.rnTime              = document.getElementById('rnTime');
        dom.rnIdcardStatus      = document.getElementById('rnIdcardStatus');
        dom.rnIdcardUploadBtn   = document.getElementById('rnIdcardUploadBtn');
        dom.rnInputName         = document.getElementById('rnInputName');
        dom.rnInputId           = document.getElementById('rnInputId');
        dom.rnSubmitBtn         = document.getElementById('rnSubmitBtn');
        dom.rnError             = document.getElementById('rnError');
        dom.rnIdcardUpload      = document.getElementById('rnIdcardUpload');
        dom.rnIdcardFile        = document.getElementById('rnIdcardFile');
        dom.rnIdcardImg         = document.getElementById('rnIdcardImg');
        dom.rnIdcardPlaceholder = document.getElementById('rnIdcardPlaceholder');
        dom.rnIdcardPreview     = document.getElementById('rnIdcardPreview');
        dom.rnTipText           = document.getElementById('rnTipText');
        dom.rnPrivacyNotice     = document.getElementById('rnPrivacyNotice');

        // Logout
        dom.logoutBtn = document.getElementById('logoutBtn');
    }

    // ═══════════════════════════════════════════
    //  SECTION: API Layer (Auth.request 已自动解析 JSON + stringify body)
    // ═══════════════════════════════════════════
    var api = {};

    api.getProfile = function() {
        return Auth.request('/api/profile', { method: 'GET' });
    };

    api.updateProfile = function(body) {
        return Auth.request('/api/profile', { method: 'PUT', body: body });
    };

    api.getRealnameStatus = function() {
        return Auth.request('/api/profile/realname-status', { method: 'GET' });
    };

    api.verifyRealname = function(body) {
        return Auth.request('/api/profile/verify-realname', { method: 'POST', body: body });
    };

    api.uploadIdcard = function(body) {
        return Auth.request('/api/profile/upload-idcard', { method: 'POST', body: body });
    };

    api.setPresetAvatar = function(body) {
        return Auth.request('/api/avatar/set-preset', { method: 'POST', body: body });
    };

    api.uploadAvatar = function(body) {
        return Auth.request('/api/avatar/upload', { method: 'POST', body: body });
    };

    // ═══════════════════════════════════════════
    //  SECTION: Init & Page Load
    // ═══════════════════════════════════════════
    function init() {
        if (!Auth.requireAuth()) return;
        createStars();
        cacheDom();
        // Init VipModule (does its own dom cache + events + wheel draw)
        if (typeof VipModule !== 'undefined') VipModule.init();
        bindEvents();
        showLoading();
        loadPageData();
    }

    function showLoading() {
        var skeletons = document.querySelectorAll('.skeleton-text');
        for (var i = 0; i < skeletons.length; i++) {
            skeletons[i].classList.add('skeleton');
        }
        dom.profileName.textContent = '加载中...';
    }

    function hideLoading() {
        var skeletons = document.querySelectorAll('.skeleton-text');
        for (var i = 0; i < skeletons.length; i++) {
            skeletons[i].classList.remove('skeleton');
        }
    }

    async function loadPageData() {
        try {
            // Phase 1: Parallel — profile + VIP status
            var results = await Promise.all([
                api.getProfile(),
                VipModule ? VipModule.fetchVipStatus() : Promise.resolve(null)
            ]);

            var profileData = results[0];
            var vipData = results[1];

            if (!profileData.success) throw new Error(profileData.message);

            state.profile = profileData.user;

            // Pass VIP data to VipModule
            if (VipModule && vipData && vipData.success) {
                VipModule.setVipData(vipData);
            }

            // Render from state
            renderProfile();
            renderStats();
            renderAvatar();
            saveToLocalCache();

            // Phase 2: Realname (non-blocking, profile already has verification bool)
            loadRealnameStatus();

            // Fill edit form
            fillEditForm();

            hideLoading();

        } catch (error) {
            console.error('加载用户数据失败:', error);
            loadFromLocalCache();
            hideLoading();
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Event Binding (event delegation)
    // ═══════════════════════════════════════════
    function bindEvents() {
        // ── Profile container delegation ──
        var container = document.querySelector('.profile-container');
        if (container) {
            container.addEventListener('click', function(e) {
                var target = e.target.closest('[data-action]');
                if (!target) return;
                var action = target.getAttribute('data-action');
                switch (action) {
                    // ── Delegated to Profile ──
                    case 'open-avatar-picker':
                        openAvatarPicker();
                        break;
                    case 'toggle-section':
                        var hd = target.closest('.section-hd');
                        if (hd && hd.nextElementSibling) toggleSection(hd.nextElementSibling.id);
                        break;
                    case 'logout':
                        handleLogout();
                        break;
                    case 'open-realname':
                        openRealnameModal();
                        break;
                    case 'navigate':
                        var hr = target.getAttribute('data-href');
                        if (hr) window.location.href = hr;
                        break;
                    // ── Delegated to VipModule ──
                    case 'watch-ad':
                        if (VipModule) VipModule.watchVipAd();
                        break;
                    case 'claim-ad-reward':
                        if (VipModule) VipModule.claimVipAdReward();
                        break;
                    case 'do-checkin':
                        if (VipModule) VipModule.doCheckin();
                        break;
                    case 'open-redeem':
                        if (VipModule) VipModule.openRedeem();
                        break;
                    case 'spin-wheel':
                        if (VipModule) VipModule.spinWheel();
                        break;
                }
            });
        }

        // ── Modal backdrop clicks ──
        var modals = [dom.editProfileModal, dom.avatarPickerModal, dom.realnameModal];
        modals.forEach(function(modal) {
            if (!modal) return;
            modal.addEventListener('click', function(e) {
                if (e.target === this) this.classList.remove('show');
            });
        });

        // ── Modal close buttons ──
        var closeBtns = {
            'modalCloseEdit': closeEditProfile,
            'modalCloseAvatar': closeAvatarPicker,
            'modalCloseRealname': closeRealnameModal
        };
        Object.keys(closeBtns).forEach(function(id) {
            var el = document.getElementById(id);
            if (el) el.addEventListener('click', closeBtns[id]);
        });

        // ── Avatar picker delegation ──
        if (dom.avatarPickerModal) {
            dom.avatarPickerModal.addEventListener('click', function(e) {
                var avOpt = e.target.closest('.avatar-option');
                if (avOpt) {
                    selectPresetAvatar(avOpt.textContent.trim());
                    return;
                }
            });
        }

        // ── Avatar upload label（for属性已原生绑定，无需JS click）──

        // ── Avatar input change ──
        if (dom.avatarInput) {
            dom.avatarInput.addEventListener('change', uploadAvatar);
        }

        // ── Realname modal: idcard upload area click → trigger file input ──
        if (dom.rnIdcardUpload) {
            dom.rnIdcardUpload.addEventListener('click', function(e) {
                if (e.target.closest('#rnIdcardClearBtn')) return;
                if (dom.rnIdcardFile) dom.rnIdcardFile.click();
            });
        }

        // ── Realname: upload for verified button ──
        var rnUploadBtn = document.getElementById('rnUploadBtnForVerified');
        if (rnUploadBtn) {
            rnUploadBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                startIdcardUploadForVerified();
            });
        }

        // ── Realname: clear idcard image ──
        var rnClearBtn = document.getElementById('rnIdcardClearBtn');
        if (rnClearBtn) {
            rnClearBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                clearIdcardImage();
            });
        }

        // ── Realname: submit button ──
        if (dom.rnSubmitBtn) {
            dom.rnSubmitBtn.addEventListener('click', submitRealname);
        }

        // ── ID card file input ──
        if (dom.rnIdcardFile) {
            dom.rnIdcardFile.addEventListener('change', handleIdcardFile);
        }

        // ── ID card drag & drop ──
        if (dom.rnIdcardUpload) {
            dom.rnIdcardUpload.addEventListener('drop', handleIdcardDrop);
            dom.rnIdcardUpload.addEventListener('dragover', handleIdcardDragOver);
            dom.rnIdcardUpload.addEventListener('dragleave', handleIdcardDragLeave);
        }

        // ── Edit profile form submit ──
        if (dom.editProfileForm) {
            dom.editProfileForm.addEventListener('submit', saveProfile);
        }

        // ── Back button ──
        var backBtn = document.querySelector('.back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', function(e) {
                e.preventDefault();
                window.location.href = '/';
            });
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Render Functions
    // ═══════════════════════════════════════════

    function renderProfile() {
        var p = state.profile;
        if (!p) return;

        var displayName = p.nickname || p.username || '未设置昵称';
        dom.profileName.textContent = displayName;

        if (dom.sidebarUserName) dom.sidebarUserName.textContent = displayName;

        var infoText = '';
        if (p.phone) infoText += p.phone;
        if (p.email) infoText += (infoText ? ' · ' : '') + p.email;
        dom.profileInfo.textContent = infoText || '暂无联系方式';

        if (p.username && p.username !== p.nickname) {
            dom.profileUid.textContent = '@' + p.username;
        } else {
            dom.profileUid.textContent = '';
        }
    }

    function renderStats() {
        var userId = state.profile ? (state.profile.id || state.profile.username) : null;
        var statsKey = userId ? ('userStats_' + userId) : null;
        var stats = null;
        if (statsKey) {
            try {
                stats = JSON.parse(localStorage.getItem(statsKey));
            } catch(e) {}
        }
        dom.divinationCount.textContent = stats ? (stats.divinations || 0) : 0;
        dom.favoriteCount.textContent = stats ? (stats.favorites || 0) : 0;

        var days = 0;
        if (state.profile && state.profile.create_time) {
            var created = new Date(state.profile.create_time);
            days = Math.max(1, Math.floor((Date.now() - created.getTime()) / 86400000));
        }
        dom.daysCount.textContent = days;
    }

    function renderAvatar() {
        var p = state.profile;
        if (!p) return;

        if (p.avatar_type === 'emoji' && p.avatar_preset) {
            dom.avatarImg.style.display = 'none';
            dom.avatarDefault.style.display = 'flex';
            dom.avatarDefault.textContent = p.avatar_preset;
        } else if (p.avatar) {
            dom.avatarImg.src = p.avatar + '?t=' + Date.now();
            dom.avatarImg.style.display = 'block';
            dom.avatarDefault.style.display = 'none';
        }
    }

    function renderRealnameTags() {
        var rn = state.realname;
        if (!rn || !rn.success) {
            if (dom.tagVerified) {
                dom.tagVerified.style.display = 'inline-block';
                dom.tagVerified.textContent = '未认证';
                dom.tagVerified.style.cursor = 'pointer';
            }
            if (dom.tagIdcard) dom.tagIdcard.style.display = 'none';
            return;
        }

        if (rn.verified) {
            if (dom.tagVerified) {
                dom.tagVerified.style.display = 'inline-block';
                dom.tagVerified.textContent = '✅ ' + (rn.data && rn.data.region || '已认证');
                dom.tagVerified.style.cursor = 'pointer';
            }
            if (dom.tagIdcard) {
                dom.tagIdcard.style.display = (rn.data && rn.data.idcard_image) ? 'inline-block' : 'none';
            }
        } else {
            if (dom.tagVerified) {
                dom.tagVerified.style.display = 'inline-block';
                dom.tagVerified.textContent = '未认证';
                dom.tagVerified.style.cursor = 'pointer';
            }
            if (dom.tagIdcard) dom.tagIdcard.style.display = 'none';
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Profile Edit
    // ═══════════════════════════════════════════
    function fillEditForm() {
        var p = state.profile;
        if (!p) return;
        if (dom.editNickname) dom.editNickname.value = p.nickname || '';
        if (dom.editUsername) dom.editUsername.value = p.username || '';
        if (dom.editPhone) dom.editPhone.value = p.phone || '';
        if (dom.editEmail) dom.editEmail.value = p.email || '';
        if (dom.editBirthday) dom.editBirthday.value = p.birthday || '';
        if (dom.editGender) dom.editGender.value = p.gender || '';
    }

    function openEditProfile() {
        if (dom.editProfileModal) dom.editProfileModal.classList.add('show');
    }

    function closeEditProfile() {
        if (dom.editProfileModal) dom.editProfileModal.classList.remove('show');
    }

    async function saveProfile(event) {
        event.preventDefault();
        var nickname = dom.editNickname.value.trim();
        var phone = dom.editPhone.value.trim();
        var email = dom.editEmail.value.trim();
        var birthday = dom.editBirthday.value;
        var gender = dom.editGender.value;

        var body = { phone: phone, email: email, birthday: birthday, gender: gender };
        if (nickname) body.nickname = nickname;

        try {
            var data = await api.updateProfile(body);
            if (data.success) {
                var u = data.user;
                if (u) {
                    if (u.nickname !== undefined) state.profile.nickname = u.nickname;
                    if (u.phone !== undefined) state.profile.phone = u.phone;
                    if (u.email !== undefined) state.profile.email = u.email;
                    if (u.birthday !== undefined) state.profile.birthday = u.birthday;
                    if (u.gender !== undefined) state.profile.gender = u.gender;
                }
                renderProfile();
                saveToLocalCache();
                showToast(data.message || '资料更新成功');
                closeEditProfile();
            } else {
                showToast('⚠️ ' + (data.message || '保存失败'));
            }
        } catch (e) {
            showToast('网络错误，请重试');
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Avatar
    // ═══════════════════════════════════════════
    function openAvatarPicker() {
        var allOptions = document.querySelectorAll('.avatar-option.selected');
        for (var i = 0; i < allOptions.length; i++) {
            allOptions[i].classList.remove('selected');
        }
        if (dom.avatarPickerModal) dom.avatarPickerModal.classList.add('show');
    }

    function closeAvatarPicker() {
        if (dom.avatarPickerModal) dom.avatarPickerModal.classList.remove('show');
    }

    async function selectPresetAvatar(emoji) {
        var allOptions = document.querySelectorAll('.avatar-option');
        for (var i = 0; i < allOptions.length; i++) {
            allOptions[i].classList.remove('selected');
            if (allOptions[i].textContent.trim() === emoji) {
                allOptions[i].classList.add('selected');
            }
        }

        try {
            var data = await api.setPresetAvatar({ type: 'emoji', value: emoji });
            if (data.success) {
                state.profile.avatar_type = 'emoji';
                state.profile.avatar_preset = emoji;
                state.profile.avatar = '';
                renderAvatar();
                saveToLocalCache();
                closeAvatarPicker();
                showToast('头像已更新');
            } else {
                showToast('⚠️ ' + (data.message || '设置失败'));
            }
        } catch (e) {
            showToast('网络错误，请重试');
        }
    }

    async function uploadAvatar() {
        var input = dom.avatarInput;
        var file = input.files[0];
        if (!file) return;

        if (!file.type || !file.type.startsWith('image/')) {
            showToast('⚠️ 请选择图片文件');
            input.value = '';
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            showToast('⚠️ 图片大小不能超过10MB');
            input.value = '';
            return;
        }

        showToast('⏳ 正在压缩并上传头像...');

        // 先用canvas压缩图片（手机照片太大，base64传输极易失败）
        compressImage(file, 400, 400, 0.75).then(async function(compressedBase64) {
            try {
                var data = await api.uploadAvatar({ image: compressedBase64 });
                if (data.success) {
                    state.profile.avatar_type = 'custom';
                    state.profile.avatar_preset = '';
                    state.profile.avatar = data.avatar_url;
                    renderAvatar();
                    saveToLocalCache();
                    showToast('✅ 头像已更新');
                    closeAvatarPicker();
                } else {
                    showToast('❌ ' + (data.message || '上传失败'));
                }
            } catch (err) {
                console.error('头像上传失败:', err);
                showToast('❌ 上传失败，请重试');
            }
        }).catch(function(err) {
            console.error('图片压缩失败:', err);
            showToast('❌ 图片处理失败，请换一张试试');
        });
        input.value = '';
    }

    // 图片压缩：canvas缩放+JPEG导出
    function compressImage(file, maxW, maxH, quality) {
        return new Promise(function(resolve, reject) {
            var img = new Image();
            var url = URL.createObjectURL(file);
            img.onload = function() {
                URL.revokeObjectURL(url);
                var w = img.width, h = img.height;
                // 仅当图片大于目标尺寸时才缩放
                if (w > maxW || h > maxH) {
                    var ratio = Math.min(maxW / w, maxH / h);
                    w = Math.round(w * ratio);
                    h = Math.round(h * ratio);
                }
                var canvas = document.createElement('canvas');
                canvas.width = w;
                canvas.height = h;
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, w, h);
                resolve(canvas.toDataURL('image/jpeg', quality));
            };
            img.onerror = function() {
                URL.revokeObjectURL(url);
                reject(new Error('图片加载失败'));
            };
            img.src = url;
        });
    }

    // ═══════════════════════════════════════════
    //  SECTION: Realname
    // ═══════════════════════════════════════════
    async function loadRealnameStatus() {
        try {
            var data = await api.getRealnameStatus();
            state.realname = data;
            renderRealnameTags();
        } catch (e) {
            // Silent fail — tags already show default state
        }
    }

    async function openRealnameModal() {
        state.rnUploadOnly = false;
        if (dom.rnVerifiedContent) dom.rnVerifiedContent.style.display = 'none';
        if (dom.rnFormContent) dom.rnFormContent.style.display = 'block';
        if (dom.rnError) dom.rnError.style.display = 'none';
        if (dom.rnSubmitBtn) {
            dom.rnSubmitBtn.textContent = '提交认证';
            dom.rnSubmitBtn.removeAttribute('data-mode');
        }
        if (dom.rnTipText) dom.rnTipText.style.display = 'block';
        if (dom.rnPrivacyNotice) dom.rnPrivacyNotice.style.display = 'block';
        if (dom.rnInputName && dom.rnInputName.parentElement) dom.rnInputName.parentElement.style.display = 'block';
        if (dom.rnInputId && dom.rnInputId.parentElement) dom.rnInputId.parentElement.style.display = 'block';

        try {
            var data = await api.getRealnameStatus();
            state.realname = data;

            if (data.success && data.verified) {
                if (dom.rnVerifiedContent) dom.rnVerifiedContent.style.display = 'block';
                if (dom.rnFormContent) dom.rnFormContent.style.display = 'none';
                if (dom.rnName) dom.rnName.textContent = (data.data && data.data.real_name_masked) || '***';
                if (dom.rnId) dom.rnId.textContent = (data.data && data.data.id_masked) || '****';
                if (dom.rnRegion) dom.rnRegion.textContent = (data.data && data.data.region) || '未知';
                if (dom.rnTime) dom.rnTime.textContent = (data.data && data.data.verify_time) || '';
                if (dom.rnIdcardStatus) {
                    dom.rnIdcardStatus.textContent = (data.data && data.data.idcard_image) ? '📷 已上传证件照' : '📷 未上传证件照';
                }
                if (dom.rnIdcardUploadBtn) {
                    dom.rnIdcardUploadBtn.style.display = (data.data && data.data.idcard_image) ? 'none' : 'block';
                }
            }
        } catch(e) {
            // Proceed with empty form
        }

        if (dom.realnameModal) dom.realnameModal.classList.add('show');
    }

    function closeRealnameModal() {
        if (dom.realnameModal) dom.realnameModal.classList.remove('show');
    }

    function startIdcardUploadForVerified() {
        if (dom.rnVerifiedContent) dom.rnVerifiedContent.style.display = 'none';
        if (dom.rnFormContent) dom.rnFormContent.style.display = 'block';
        if (dom.rnInputName && dom.rnInputName.parentElement) dom.rnInputName.parentElement.style.display = 'none';
        if (dom.rnInputId && dom.rnInputId.parentElement) dom.rnInputId.parentElement.style.display = 'none';
        if (dom.rnTipText) dom.rnTipText.style.display = 'none';
        if (dom.rnPrivacyNotice) dom.rnPrivacyNotice.style.display = 'none';
        dom.rnSubmitBtn.textContent = '上传证件照';
        dom.rnSubmitBtn.setAttribute('data-mode', 'upload-only');
        state.rnUploadOnly = true;
    }

    function handleIdcardFile(e) {
        var file = e.target.files[0];
        if (!file) return;
        if (file.size > 5 * 1024 * 1024) { showToast('图片大小不能超过5MB'); return; }
        var reader = new FileReader();
        reader.onload = function(ev) {
            state.rnIdcardBase64 = ev.target.result;
            if (dom.rnIdcardImg) dom.rnIdcardImg.src = ev.target.result;
            if (dom.rnIdcardPlaceholder) dom.rnIdcardPlaceholder.style.display = 'none';
            if (dom.rnIdcardPreview) dom.rnIdcardPreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    function handleIdcardDrop(e) {
        e.preventDefault();
        if (dom.rnIdcardUpload) {
            dom.rnIdcardUpload.style.borderColor = 'rgba(0,180,255,0.25)';
            dom.rnIdcardUpload.style.background = 'rgba(0,180,255,0.03)';
        }
        var file = e.dataTransfer.files[0];
        if (!file) return;
        if (file.size > 5 * 1024 * 1024) { showToast('图片大小不能超过5MB'); return; }
        var reader = new FileReader();
        reader.onload = function(ev) {
            state.rnIdcardBase64 = ev.target.result;
            if (dom.rnIdcardImg) dom.rnIdcardImg.src = ev.target.result;
            if (dom.rnIdcardPlaceholder) dom.rnIdcardPlaceholder.style.display = 'none';
            if (dom.rnIdcardPreview) dom.rnIdcardPreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    function handleIdcardDragOver(e) {
        e.preventDefault();
        if (dom.rnIdcardUpload) {
            dom.rnIdcardUpload.style.borderColor = 'rgba(0,180,255,0.6)';
            dom.rnIdcardUpload.style.background = 'rgba(0,180,255,0.06)';
        }
    }

    function handleIdcardDragLeave(e) {
        if (dom.rnIdcardUpload) {
            dom.rnIdcardUpload.style.borderColor = 'rgba(0,180,255,0.25)';
            dom.rnIdcardUpload.style.background = 'rgba(0,180,255,0.03)';
        }
    }

    function clearIdcardImage() {
        state.rnIdcardBase64 = '';
        if (dom.rnIdcardImg) dom.rnIdcardImg.src = '';
        if (dom.rnIdcardPlaceholder) dom.rnIdcardPlaceholder.style.display = 'block';
        if (dom.rnIdcardPreview) dom.rnIdcardPreview.style.display = 'none';
        if (dom.rnIdcardFile) dom.rnIdcardFile.value = '';
    }

    async function submitRealname() {
        var btn = dom.rnSubmitBtn;
        var isUploadOnly = btn.getAttribute('data-mode') === 'upload-only' || state.rnUploadOnly;

        if (isUploadOnly) {
            if (!state.rnIdcardBase64) {
                showToast('⚠️ 请先选择身份证照片');
                return;
            }
            btn.disabled = true;
            btn.textContent = '上传中...';
            try {
                var upData = await api.uploadIdcard({ idcard_image: state.rnIdcardBase64 });
                if (upData.success) {
                    showToast('✅ 证件照上传成功');
                    closeRealnameModal();
                    await loadRealnameStatus();
                    return;
                } else {
                    if (dom.rnError) {
                        dom.rnError.textContent = upData.message || '上传失败';
                        dom.rnError.style.display = 'block';
                    }
                }
            } catch (e) {
                if (dom.rnError) {
                    dom.rnError.textContent = '网络错误';
                    dom.rnError.style.display = 'block';
                }
            }
            btn.disabled = false;
            btn.textContent = '上传证件照';
            return;
        }

        var name = (dom.rnInputName.value || '').trim();
        var idNumber = (dom.rnInputId.value || '').trim();

        if (name.length < 2) {
            if (dom.rnError) { dom.rnError.textContent = '请输入真实姓名（至少2个字）'; dom.rnError.style.display = 'block'; }
            return;
        }
        if (idNumber.length !== 18) {
            if (dom.rnError) { dom.rnError.textContent = '请输入18位身份证号码'; dom.rnError.style.display = 'block'; }
            return;
        }

        btn.disabled = true;
        btn.textContent = '验证中...';

        var body = { real_name: name, id_number: idNumber };
        if (state.rnIdcardBase64) body.idcard_image = state.rnIdcardBase64;

        try {
            var data = await api.verifyRealname(body);
            if (data.success) {
                showToast('✅ 实名认证成功');
                closeRealnameModal();
                await loadRealnameStatus();
                return;
            }
            if (dom.rnError) {
                dom.rnError.textContent = data.message || '认证失败，请检查信息';
                dom.rnError.style.display = 'block';
            }
        } catch (e) {
            if (dom.rnError) {
                dom.rnError.textContent = '网络错误';
                dom.rnError.style.display = 'block';
            }
        }
        btn.disabled = false;
        btn.textContent = '提交认证';
    }

    // ═══════════════════════════════════════════
    //  SECTION: Logout
    // ═══════════════════════════════════════════
    function handleLogout() {
        showToast('已退出登录');
        Auth.logout();
        setTimeout(function() {
            window.location.href = '/login.html';
        }, 1000);
    }

    // ═══════════════════════════════════════════
    //  SECTION: UI Helpers
    // ═══════════════════════════════════════════
    function toggleSection(id) {
        var body = document.getElementById(id);
        if (!body) return;
        var hd = body.previousElementSibling;
        var arrow = hd ? hd.querySelector('.section-arrow') : null;
        var isCollapsed = body.classList.contains('collapsed');
        if (isCollapsed) {
            body.classList.remove('collapsed');
            body.style.maxHeight = body.scrollHeight + 'px';
            if (arrow) arrow.textContent = '▼';
        } else {
            body.classList.add('collapsed');
            body.style.maxHeight = '';
            if (arrow) arrow.textContent = '▶';
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Offline / Local Cache
    // ═══════════════════════════════════════════
    function saveToLocalCache() {
        if (!state.profile) return;
        var storage = Auth.isRemember() ? localStorage : sessionStorage;
        storage.setItem('currentUser', JSON.stringify(state.profile));
        if (state.realname) {
            try { storage.setItem('realnameStatus', JSON.stringify(state.realname)); } catch(e) {}
        }
    }

    function loadFromLocalCache() {
        var cached = localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser');
        if (cached) {
            try {
                state.profile = JSON.parse(cached);
                renderProfile();
                renderAvatar();
                renderStats();
                fillEditForm();
            } catch(e) {}
        }
        var cachedRn = localStorage.getItem('realnameStatus') || sessionStorage.getItem('realnameStatus');
        if (cachedRn) {
            try {
                state.realname = JSON.parse(cachedRn);
                renderRealnameTags();
            } catch(e) {}
        }

        if (!state.profile) {
            dom.profileName.textContent = '加载失败';
            dom.profileInfo.textContent = '⚠️ 请刷新页面重试';
        }

        hideLoading();
        // Try loading VIP/realname in background
        if (VipModule) VipModule.loadVipStatus();
        loadRealnameStatus();
    }

    // ═══════════════════════════════════════════
    //  Public API
    // ═══════════════════════════════════════════
    return {
        init: init,
        openEditProfile: openEditProfile,
        closeEditProfile: closeEditProfile,
        openAvatarPicker: openAvatarPicker,
        closeAvatarPicker: closeAvatarPicker,
        selectPresetAvatar: selectPresetAvatar,
        uploadAvatar: uploadAvatar,
        openRealnameModal: openRealnameModal,
        closeRealnameModal: closeRealnameModal,
        startIdcardUploadForVerified: startIdcardUploadForVerified,
        clearIdcardImage: clearIdcardImage,
        submitRealname: submitRealname,
        handleLogout: handleLogout,
        toggleSection: toggleSection
    };

})();

document.addEventListener('DOMContentLoaded', Profile.init);
if (document.readyState !== 'loading') {
    setTimeout(function() {
        if (typeof Profile.init === 'function') Profile.init();
    }, 0);
}
