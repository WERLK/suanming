/**
 * 玄机算命网 - 个人中心模块
 * v1.4.0 - 重构版：集中状态管理 / DOM缓存 / API封装 / 事件委托
 */
window.Profile = (function() {
    'use strict';

    // ═══════════════════════════════════════════
    //  SECTION: State
    // ═══════════════════════════════════════════
    var state = {
        profile: null,    // GET /api/profile 返回的完整用户对象
        vip: null,        // GET /api/vip/status 返回的VIP状态
        realname: null,   // GET /api/profile/realname-status 返回的实名状态
        // UI 标志
        loading: false,
        vipAdWatching: false,
        vipAdClaiming: false,
        vipAdTimer: null,
        vipAdSeconds: 0,
        wheelSpinning: false,
        wheelRemaining: 5,   // 本地副本，loadVIP后更新
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
        dom.tagVip          = document.getElementById('tagVip');
        dom.tagVerified     = document.getElementById('tagVerified');
        dom.tagIdcard       = document.getElementById('tagIdcard');

        // Stats
        dom.divinationCount = document.getElementById('divinationCount');
        dom.favoriteCount   = document.getElementById('favoriteCount');
        dom.daysCount       = document.getElementById('daysCount');

        // VIP card
        dom.vipCard         = document.getElementById('vipCard');
        dom.vipBadge        = document.getElementById('vipBadge');
        dom.vipExpire       = document.getElementById('vipExpire');
        dom.vipProgressBar  = document.getElementById('vipProgressBar');
        dom.vipRemaining    = document.getElementById('vipRemaining');
        dom.vipAdSection    = document.getElementById('vipAdSection');
        dom.vipAdArea       = document.getElementById('vipAdArea');
        dom.vipAdSlot       = document.getElementById('vipAdSlot');
        dom.vipAdCountdown  = document.getElementById('vipAdCountdown');
        dom.vipAdDaily      = document.getElementById('vipAdDaily');
        dom.vipAdWatchBtn   = document.getElementById('vipAdWatchBtn');

        // Points & Wheel
        dom.pointsValue     = document.getElementById('pointsValue');
        dom.checkinBtn      = document.getElementById('checkinBtn');
        dom.streakBadge     = document.getElementById('streakBadge');
        dom.wheelCanvas     = document.getElementById('wheelCanvas');
        dom.wheelSpinBtn    = document.getElementById('wheelSpinBtn');
        dom.wheelRemain     = document.getElementById('wheelRemain');

        // Redeem
        dom.redeemModal     = document.getElementById('redeemModal');
        dom.redeemPoints    = document.getElementById('redeemPoints');

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

        // Plans & Benefits
        dom.permanentPlanDesc  = document.getElementById('permanentPlanDesc');
        dom.permanentPlanBadge = document.getElementById('permanentPlanBadge');
        dom.planFree           = document.getElementById('planFree');
        dom.planBasic          = document.getElementById('planBasic');
        dom.planPermanent      = document.getElementById('planPermanent');

        // Sections
        dom.sectPlans     = document.getElementById('sectPlans');
        dom.sectBenefits  = document.getElementById('sectBenefits');
        dom.sectKnowledge = document.getElementById('sectKnowledge');

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

    api.getVipStatus = function() {
        return Auth.request('/api/vip/status', { method: 'GET' });
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

    api.watchAd = function() {
        return Auth.request('/api/vip/watch-ad', { method: 'POST' });
    };

    api.checkin = function() {
        return Auth.request('/api/vip/checkin', { method: 'POST' });
    };

    api.redeem = function(type) {
        return Auth.request('/api/vip/redeem', { method: 'POST', body: { type: type } });
    };

    api.spinWheel = function() {
        return Auth.request('/api/vip/wheel', { method: 'POST' });
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
            // Phase 1: Parallel — profile + VIP
            var results = await Promise.all([
                api.getProfile(),
                api.getVipStatus()
            ]);

            var profileData = results[0];
            var vipData = results[1];

            if (!profileData.success) throw new Error(profileData.message);

            state.profile = profileData.user;
            state.vip = vipData.success ? vipData : null;

            // Render from state
            renderProfile();
            renderStats();
            renderVIP();
            renderAvatar();
            saveToLocalCache();

            // Phase 2: Realname (non-blocking, profile already has verification bool)
            loadRealnameStatus();

            // Fill edit form
            fillEditForm();

            hideLoading();

        } catch (error) {
            console.error('加载用户数据失败:', error);
            // Fallback to local cache
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
                    case 'open-avatar-picker':
                        openAvatarPicker();
                        break;
                    case 'watch-ad':
                        watchVipAd();
                        break;
                    case 'claim-ad-reward':
                        claimVipAdReward();
                        break;
                    case 'do-checkin':
                        doCheckin();
                        break;
                    case 'open-redeem':
                        openRedeem();
                        break;
                    case 'spin-wheel':
                        spinWheel();
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
                }
            });
        }

        // ── Modal backdrop clicks ──
        var modals = [dom.editProfileModal, dom.avatarPickerModal, dom.redeemModal, dom.realnameModal];
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
            'modalCloseRedeem': closeRedeem,
            'modalCloseRedeemBtn': closeRedeem,
            'modalCloseRealname': closeRealnameModal
        };
        Object.keys(closeBtns).forEach(function(id) {
            var el = document.getElementById(id);
            if (el) el.addEventListener('click', closeBtns[id]);
        });

        // ── Avatar picker delegation ──
        if (dom.avatarPickerModal) {
            dom.avatarPickerModal.addEventListener('click', function(e) {
                // Select avatar emoji
                var avOpt = e.target.closest('.avatar-option');
                if (avOpt) {
                    selectPresetAvatar(avOpt.textContent.trim());
                    return;
                }
            });
        }

        // ── Avatar upload label ──
        var uploadLabel = document.getElementById('avatarUploadLabel');
        if (uploadLabel) {
            uploadLabel.addEventListener('click', function() {
                if (dom.avatarInput) dom.avatarInput.click();
            });
        }

        // ── Avatar input change ──
        if (dom.avatarInput) {
            dom.avatarInput.addEventListener('change', uploadAvatar);
        }

        // ── Redeem modal delegation ──
        if (dom.redeemModal) {
            dom.redeemModal.addEventListener('click', function(e) {
                var opt = e.target.closest('[data-action="do-redeem"]');
                if (opt) {
                    doRedeem(opt.getAttribute('data-type'));
                    return;
                }
            });
        }

        // ── Realname modal: idcard upload area click → trigger file input ──
        if (dom.rnIdcardUpload) {
            dom.rnIdcardUpload.addEventListener('click', function(e) {
                // Don't trigger if clicking clear button
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
        // From localStorage as primary, fallback to 0
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

        // Days count from profile.create_time
        var days = 0;
        if (state.profile && state.profile.create_time) {
            var created = new Date(state.profile.create_time);
            days = Math.max(1, Math.floor((Date.now() - created.getTime()) / 86400000));
        }
        dom.daysCount.textContent = days;
    }

    function renderVIP() {
        var v = state.vip;
        if (!v) return;

        dom.vipCard.style.display = 'block';

        // Badge
        dom.vipBadge.textContent = v.vip_level_name || '';
        dom.vipBadge.className = 'vip-badge ' + (v.vip_level || 'free');

        // Header VIP tag
        if (dom.tagVip) {
            if (v.vip_level === 'permanent') {
                dom.tagVip.textContent = '永久会员';
                dom.tagVip.className = 'profile-tag tag-vip tag-vip-perm';
            } else if (v.vip_level === 'basic') {
                dom.tagVip.textContent = 'VIP会员';
                dom.tagVip.className = 'profile-tag tag-vip tag-vip-active';
            } else {
                dom.tagVip.textContent = '免费用户';
                dom.tagVip.className = 'profile-tag tag-vip';
            }
        }

        // Expire
        if (v.vip_level === 'permanent') {
            dom.vipExpire.textContent = '永久有效';
        } else if (v.vip_expire) {
            var d = new Date(v.vip_expire);
            dom.vipExpire.textContent = '到期: ' + d.toLocaleDateString('zh-CN');
        } else {
            dom.vipExpire.textContent = '';
        }

        // Progress bar & remaining text
        var totalAdCount = v.total_ad_count || 0;
        var threshold = v.bonus_threshold || 20;
        var todayAds = v.today_ads || 0;
        var maxAds = v.max_daily_ads || 0;
        var adRemaining = Math.max(0, maxAds - todayAds);

        updateVipAdInfo(todayAds, maxAds);

        if (v.vip_level === 'permanent') {
            dom.vipRemaining.textContent = '🎉 永久会员（今日可看广告' + maxAds + '次）';
            dom.vipProgressBar.style.width = '100%';
        } else if (v.vip_remaining) {
            dom.vipRemaining.textContent = '剩余: ' + v.vip_remaining + ' | 今日广告 ' + adRemaining + '/' + maxAds + ' 次 | 里程碑 ' + totalAdCount + '/' + threshold;
            var expireDate = new Date(v.vip_expire);
            var now = new Date();
            var total = expireDate - now;
            var max = 7 * 24 * 3600 * 1000;
            var pct = Math.min(100, Math.max(0, (total / max) * 100));
            dom.vipProgressBar.style.width = pct + '%';
        } else {
            var permPct = Math.min(100, Math.round((totalAdCount / threshold) * 100));
            dom.vipRemaining.textContent = '今日广告 ' + adRemaining + '/' + maxAds + ' 次 | 里程碑 ' + totalAdCount + '/' + threshold + '（每' + threshold + '次触发随机奖励）';
            dom.vipProgressBar.style.width = permPct + '%';
        }

        // Points
        if (v.points !== undefined) {
            dom.pointsValue.textContent = v.points;
        }

        // Check-in
        if (v.today_checked_in) {
            dom.checkinBtn.textContent = '✅ 已签到';
            dom.checkinBtn.disabled = true;
            dom.checkinBtn.style.opacity = '0.5';
        } else {
            dom.checkinBtn.textContent = '✅ 每日签到';
            dom.checkinBtn.disabled = false;
            dom.checkinBtn.style.opacity = '1';
        }

        // Streak
        if (v.checkin_streak !== undefined) {
            dom.streakBadge.textContent = '连续' + v.checkin_streak + '天';
        }

        // Wheel remaining
        var remaining = v.wheel_spins_remaining || 0;
        state.wheelRemaining = remaining;
        if (dom.wheelRemain) dom.wheelRemain.textContent = remaining;
        dom.wheelSpinBtn.disabled = remaining <= 0;
        dom.wheelSpinBtn.textContent = remaining > 0 ? ('🎰 转转盘（剩' + remaining + '次）') : '🎰 今日次数已用完';

        // Plan cards
        updatePlanCards(v);

        // Draw wheel
        drawWheel();
    }

    function updatePlanCards(v) {
        // Highlight active plan
        var allCards = document.querySelectorAll('.vip-plan-card');
        for (var i = 0; i < allCards.length; i++) { allCards[i].classList.remove('active'); }
        var allBadges = document.querySelectorAll('.vip-plan-card .plan-badge');
        for (var j = 0; j < allBadges.length; j++) { allBadges[j].textContent = '—'; }

        if (v.vip_level === 'permanent') {
            if (dom.planPermanent) dom.planPermanent.classList.add('active');
            if (dom.permanentPlanDesc) dom.permanentPlanDesc.textContent = '已解锁永久会员\n全部功能永久使用';
            if (dom.permanentPlanBadge) {
                dom.permanentPlanBadge.textContent = '已解锁';
                dom.permanentPlanBadge.className = 'plan-badge plan-badge-p';
            }
        } else {
            if (v.vip_level === 'basic') {
                if (dom.planBasic) dom.planBasic.classList.add('active');
            } else {
                if (dom.planFree) dom.planFree.classList.add('active');
            }
            if (dom.permanentPlanDesc) dom.permanentPlanDesc.textContent = '累计' + (v.bonus_threshold || 20) + '次触发奖励';
            var totalAdCount = v.total_ad_count || 0;
            var threshold = v.bonus_threshold || 20;
            var nextMilestone = Math.ceil(totalAdCount / threshold) * threshold;
            if (dom.permanentPlanBadge) {
                dom.permanentPlanBadge.textContent = totalAdCount + '/' + nextMilestone;
                dom.permanentPlanBadge.className = 'plan-badge plan-badge-p';
            }
        }
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
                // Update state locally
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
    //  SECTION: VIP — Ad Watching
    // ═══════════════════════════════════════════
    function updateVipAdInfo(todayAds, maxAds) {
        var remaining = Math.max(0, maxAds - todayAds);
        dom.vipAdDaily.innerHTML = '今日可观看 <strong>' + remaining + '</strong> 次';
        // Only disable when we have a valid max (maxAds > 0) and no remaining
        if (maxAds > 0 && remaining <= 0) {
            dom.vipAdWatchBtn.disabled = true;
            dom.vipAdWatchBtn.style.opacity = '0.4';
            dom.vipAdCountdown.textContent = '今日已用完';
        } else {
            dom.vipAdWatchBtn.disabled = false;
            dom.vipAdWatchBtn.style.opacity = '1';
        }
    }

    async function watchVipAd() {
        if (state.vipAdWatching) return;

        // Check remaining
        var todayAds = state.vip ? (state.vip.today_ads || 0) : 0;
        var maxAds = state.vip ? (state.vip.max_daily_ads || 0) : 0;
        // maxAds=0 means unlimited/uninitialized, don't block
        if (maxAds > 0 && todayAds >= maxAds) {
            showToast('⚠️ 今日广告次数已用完');
            return;
        }

        // Try BaiduAd
        if (typeof BaiduAd !== 'undefined' && BaiduAd.isReady && BaiduAd.isReady()) {
            state.vipAdTarget = 'baidu';
            if (dom.vipAdSlot) dom.vipAdSlot.innerHTML = '<span>📺</span><div id="vipAdContainer" style="width:100%;height:100%;"></div>';
            BaiduAd.show('vipAdContainer', { onComplete: function() {
                if (!state.vipAdWatching) return;
                state.vipAdSeconds = 0;
                claimVipAdReward();
            }});
            state.vipAdWatching = true;
            startAdCountdown();
            return;
        }

        // Fallback: countdown timer
        state.vipAdWatching = true;
        state.vipAdSeconds = 15;
        state.vipAdTarget = 'countdown';
        startAdCountdown();
    }

    function startAdCountdown() {
        dom.vipAdCountdown.textContent = state.vipAdSeconds > 0 ? ('⏳ ' + state.vipAdSeconds + 's') : '📺 广告观看中...';
        dom.vipAdWatchBtn.disabled = true;
        dom.vipAdWatchBtn.textContent = '观看中...';
        dom.vipAdSlot.innerHTML = '<span>📺</span>';

        state.vipAdTimer = setInterval(function() {
            if (state.vipAdSeconds > 0) {
                state.vipAdSeconds--;
                dom.vipAdCountdown.textContent = '⏳ ' + state.vipAdSeconds + 's';
            }
            if (state.vipAdSeconds <= 0 && state.vipAdTarget === 'countdown') {
                clearInterval(state.vipAdTimer);
                state.vipAdTimer = null;
                state.vipAdWatching = false;
                dom.vipAdWatchBtn.textContent = '🎁 领取奖励';
                dom.vipAdWatchBtn.disabled = false;
                dom.vipAdWatchBtn.setAttribute('data-action', 'claim-ad-reward');
            }
        }, 1000);
    }

    async function claimVipAdReward() {
        if (state.vipAdClaiming) return;
        state.vipAdClaiming = true;
        try {
            var data = await api.watchAd();
            if (data.success) {
                showToast(data.message || '观看完成！');
                await loadVipStatus();
            } else {
                showToast('⚠️ ' + (data.message || '领取失败'));
            }
        } catch (e) {
            showToast('网络错误，请重试');
        }
        state.vipAdClaiming = false;
        resetVipAdUI();
    }

    function resetVipAdUI() {
        if (state.vipAdTimer) {
            clearInterval(state.vipAdTimer);
            state.vipAdTimer = null;
        }
        state.vipAdWatching = false;
        state.vipAdClaiming = false;
        state.vipAdSeconds = 0;
        if (typeof BaiduAd !== 'undefined' && BaiduAd.destroy) BaiduAd.destroy();
        dom.vipAdSlot.innerHTML = '<span>📺</span>';
        dom.vipAdWatchBtn.textContent = '▶ 看广告赚时长';
        dom.vipAdWatchBtn.setAttribute('data-action', 'watch-ad');
        dom.vipAdCountdown.textContent = '';
    }

    // ═══════════════════════════════════════════
    //  SECTION: VIP — Check-in
    // ═══════════════════════════════════════════
    async function doCheckin() {
        dom.checkinBtn.disabled = true;
        dom.checkinBtn.textContent = '签到中...';
        try {
            var data = await api.checkin();
            if (data.success) {
                showToast(data.message || '签到成功！');
                await loadVipStatus();
            } else {
                showToast('⚠️ ' + (data.message || '签到失败'));
                dom.checkinBtn.disabled = false;
                dom.checkinBtn.textContent = '✅ 每日签到';
            }
        } catch (e) {
            showToast('网络错误，请重试');
            dom.checkinBtn.disabled = false;
            dom.checkinBtn.textContent = '✅ 每日签到';
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Points Redeem
    // ═══════════════════════════════════════════
    function openRedeem() {
        if (state.vip && state.vip.points !== undefined) {
            dom.redeemPoints.textContent = state.vip.points;
        }
        if (dom.redeemModal) dom.redeemModal.classList.add('show');
    }

    function closeRedeem() {
        if (dom.redeemModal) dom.redeemModal.classList.remove('show');
    }

    async function doRedeem(type) {
        try {
            var data = await api.redeem(type);
            if (data.success) {
                showToast(data.message || '兑换成功！');
                closeRedeem();
                await loadVipStatus();
            } else {
                showToast('⚠️ ' + (data.message || '兑换失败'));
            }
        } catch (e) {
            showToast('网络错误，请重试');
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: VIP — Common
    // ═══════════════════════════════════════════
    async function loadVipStatus() {
        try {
            var data = await api.getVipStatus();
            if (data.success) {
                state.vip = data;
                renderVIP();
            }
        } catch (e) {
            console.error('加载VIP状态失败:', e);
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Lucky Wheel
    // ═══════════════════════════════════════════
    var wheelColors = ['#ff6b35','#ff9f43','#ffd700','#feca57','#54a0ff','#5f27cd','#00d2d3','#1dd1a1'];
    var wheelPrizes = ['1hVIP','2hVIP','5分','10分','免广卡x1','免广卡x3','24hVIP','50分'];

    function drawWheel() {
        var canvas = dom.wheelCanvas;
        if (!canvas) return;
        var ctx = canvas.getContext('2d');
        var cx = canvas.width / 2, cy = canvas.height / 2, r = 54;
        var segAngle = (2 * Math.PI) / 8;

        for (var i = 0; i < 8; i++) {
            var startAngle = i * segAngle;
            var endAngle = startAngle + segAngle;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, r, startAngle, endAngle);
            ctx.fillStyle = wheelColors[i];
            ctx.fill();
            ctx.strokeStyle = 'rgba(0,0,0,0.3)';
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(startAngle + segAngle / 2);
            ctx.textAlign = 'center';
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 9px sans-serif';
            ctx.fillText(wheelPrizes[i], r * 0.6, 4);
            ctx.restore();
        }

        ctx.beginPath();
        ctx.arc(cx, cy, 14, 0, 2 * Math.PI);
        ctx.fillStyle = '#1a1a2e';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255,215,0,0.5)';
        ctx.lineWidth = 3;
        ctx.stroke();
    }

    async function spinWheel() {
        // Bug Fix #1: state.wheelSpinning prevents double-spin
        if (state.wheelSpinning) return;
        if (state.wheelRemaining <= 0) {
            showToast('今日次数已用完');
            return;
        }

        state.wheelSpinning = true;
        dom.wheelSpinBtn.disabled = true;

        // Bug Fix #2: Call API FIRST, then animate to server-determined segment
        try {
            var data = await api.spinWheel();

            if (data.success) {
                // Determine target segment from response
                var targetSegment = 0;
                if (typeof data.prize_index === 'number') {
                    targetSegment = data.prize_index;
                } else {
                    targetSegment = wheelPrizes.indexOf(data.prize_name);
                    if (targetSegment < 0) targetSegment = 0;
                }

                // Animate to correct segment
                var totalRotation = (5 * 360) + (targetSegment * 45) + Math.random() * 30;
                var startTime = Date.now();
                var spinDuration = 3000;
                var canvas = dom.wheelCanvas;

                function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

                function animateSpin() {
                    var elapsed = Date.now() - startTime;
                    var progress = Math.min(1, elapsed / spinDuration);
                    var easedProgress = easeOutCubic(progress);
                    var rotation = totalRotation * easedProgress;
                    canvas.style.transform = 'rotate(' + rotation + 'deg)';

                    if (progress < 1) {
                        requestAnimationFrame(animateSpin);
                    } else {
                        // Bug Fix #1: Reset spinning state
                        state.wheelSpinning = false;
                        showToast(data.message);
                        loadVipStatus();
                    }
                }
                requestAnimationFrame(animateSpin);

            } else {
                // Bug Fix #1: Reset on API error too
                state.wheelSpinning = false;
                showToast('⚠️ ' + (data.message || '转盘抽奖失败'));
                loadVipStatus();
            }
        } catch (e) {
            // Bug Fix #1: Reset on network error
            state.wheelSpinning = false;
            dom.wheelSpinBtn.disabled = false;
            showToast('网络错误，请重试');
            loadVipStatus();
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Avatar
    // ═══════════════════════════════════════════
    function openAvatarPicker() {
        // Clear previous highlight
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
        // Highlight selection
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
        if (file.size > 2 * 1024 * 1024) {
            showToast('⚠️ 图片大小不能超过2MB');
            input.value = '';
            return;
        }

        showToast('⏳ 正在上传头像...');

        var reader = new FileReader();
        // Bug Fix #5: Wrap reader.onload in its own try/catch
        reader.onload = async function(e) {
            try {
                var data = await api.uploadAvatar({ image: e.target.result });
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
        };
        reader.readAsDataURL(file);
        input.value = '';
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
        // Reset
        state.rnUploadOnly = false;
        if (dom.rnVerifiedContent) dom.rnVerifiedContent.style.display = 'none';
        if (dom.rnFormContent) dom.rnFormContent.style.display = 'block';
        if (dom.rnError) dom.rnError.style.display = 'none';
        if (dom.rnSubmitBtn) {
            dom.rnSubmitBtn.textContent = '提交认证';
            dom.rnSubmitBtn.removeAttribute('data-mode');
        }
        // Show tip/privacy text in normal mode
        if (dom.rnTipText) dom.rnTipText.style.display = 'block';
        if (dom.rnPrivacyNotice) dom.rnPrivacyNotice.style.display = 'block';
        // Show name/id inputs
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

        // Hide name/id inputs
        if (dom.rnInputName && dom.rnInputName.parentElement) dom.rnInputName.parentElement.style.display = 'none';
        if (dom.rnInputId && dom.rnInputId.parentElement) dom.rnInputId.parentElement.style.display = 'none';

        // Bug Fix #7: Use explicit IDs instead of positional selectors
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

        // Upload-only mode
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
                    return; // Bug Fix #3: Early return on success
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

        // Normal verification mode
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
                // Bug Fix #3: Early return — skip re-enable
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
        // Only reached on failure
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
        // Bug Fix #4: Now also loads realname tags from cache
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
        // Load realname from cache
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
        loadVipStatus();
        loadRealnameStatus();
    }

    // ═══════════════════════════════════════════
    //  Public API
    // ═══════════════════════════════════════════
    return {
        init: init,
        // Expose for HTML onclick fallbacks (transitional)
        openEditProfile: openEditProfile,
        closeEditProfile: closeEditProfile,
        openAvatarPicker: openAvatarPicker,
        closeAvatarPicker: closeAvatarPicker,
        selectPresetAvatar: selectPresetAvatar,
        uploadAvatar: uploadAvatar,
        openRedeem: openRedeem,
        closeRedeem: closeRedeem,
        doRedeem: doRedeem,
        doCheckin: doCheckin,
        spinWheel: spinWheel,
        watchVipAd: watchVipAd,
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
// Also draw wheel immediately if canvas is already in DOM
if (document.readyState !== 'loading') {
    setTimeout(function() {
        if (typeof Profile.init === 'function') Profile.init();
    }, 0);
}
