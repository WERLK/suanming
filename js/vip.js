/**
 * 玄机算命网 - VIP会员中心模块 (v1.2.0)
 * 从 profile.js 提取：VIP状态管理 / 广告 / 签到 / 积分兑换 / 幸运转盘
 */
window.VipModule = (function() {
    'use strict';

    // ═══════════════════════════════════════════
    //  SECTION: State
    // ═══════════════════════════════════════════
    var state = {
        vip: null,
        // Ad watching
        vipAdWatching: false,
        vipAdClaiming: false,
        vipAdTimer: null,
        vipAdSeconds: 0,
        // Wheel
        wheelSpinning: false,
        wheelRemaining: 5
    };

    // ═══════════════════════════════════════════
    //  SECTION: DOM Cache
    // ═══════════════════════════════════════════
    var dom = {};

    function cacheDom() {
        // VIP banner
        dom.vipCenterBanner = document.getElementById('vipCenterBanner');
        dom.vipCenterBadge  = document.getElementById('vipCenterBadge');

        // VIP card
        dom.vipCard         = document.getElementById('vipCard');
        dom.vipBadge        = document.getElementById('vipBadge');
        dom.vipExpire       = document.getElementById('vipExpire');
        dom.vipProgressBar  = document.getElementById('vipProgressBar');
        dom.vipRemaining    = document.getElementById('vipRemaining');
        dom.vipStatusSub    = document.getElementById('vipStatusSub');
        dom.vipAdSlot       = document.getElementById('vipAdSlot');
        dom.vipAdCountdown  = document.getElementById('vipAdCountdown');
        dom.vipAdDaily      = document.getElementById('vipAdDaily');
        dom.vipAdWatchBtn   = document.getElementById('vipAdWatchBtn');
        dom.vipAdBtnIcon    = document.getElementById('vipAdBtnIcon');
        dom.vipAdBtnText    = document.getElementById('vipAdBtnText');
        dom.vipAdBtnRemain  = document.getElementById('vipAdBtnRemain');
        dom.vipAdPlayback   = document.getElementById('vipAdPlayback');

        // Points & Check-in
        dom.pointsValue     = document.getElementById('pointsValue');
        dom.checkinBtn      = document.getElementById('checkinBtn');
        dom.streakBadge     = document.getElementById('streakBadge');

        // Wheel
        dom.wheelCanvas     = document.getElementById('wheelCanvas');
        dom.wheelSpinBtn    = document.getElementById('wheelSpinBtn');
        dom.wheelRemain     = document.getElementById('wheelRemain');

        // Redeem modal
        dom.redeemModal     = document.getElementById('redeemModal');
        dom.redeemPoints    = document.getElementById('redeemPoints');

        // Plan cards
        dom.permanentPlanDesc  = document.getElementById('permanentPlanDesc');
        dom.permanentPlanBadge = document.getElementById('permanentPlanBadge');
        dom.basicPlanDesc      = document.getElementById('basicPlanDesc');
        dom.basicPlanBadge     = document.getElementById('basicPlanBadge');
        dom.freePlanDesc       = document.getElementById('freePlanDesc');
        dom.freePlanBadge      = document.getElementById('freePlanBadge');
        dom.planFree           = document.getElementById('planFree');
        dom.planBasic          = document.getElementById('planBasic');
        dom.planPermanent      = document.getElementById('planPermanent');

        // Profile header tag (shared with Profile module via DOM)
        dom.tagVip = document.getElementById('tagVip');
    }

    // ═══════════════════════════════════════════
    //  SECTION: API Layer
    // ═══════════════════════════════════════════
    var api = {};

    api.getVipStatus = function() {
        return Auth.request('/api/vip/status', { method: 'GET' });
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

    // ═══════════════════════════════════════════
    //  SECTION: Init
    // ═══════════════════════════════════════════
    function init() {
        cacheDom();
        bindEvents();
        drawWheel();
    }

    function bindEvents() {
        // ── Direct click handler for watch-ad button (fallback to event delegation) ──
        if (dom.vipAdWatchBtn) {
            dom.vipAdWatchBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (dom.vipAdWatchBtn.disabled) return;
                watchVipAd();
            });
        }

        // ── Direct click handler for checkin button ──
        if (dom.checkinBtn) {
            dom.checkinBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (dom.checkinBtn.disabled) return;
                doCheckin();
            });
        }

        // ── Direct click handler for wheel spin button ──
        if (dom.wheelSpinBtn) {
            dom.wheelSpinBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (dom.wheelSpinBtn.disabled) return;
                spinWheel();
            });
        }

        // Redeem modal: close on backdrop click
        if (dom.redeemModal) {
            dom.redeemModal.addEventListener('click', function(e) {
                if (e.target === this) closeRedeem();
            });
        }

        // Redeem modal delegation (for do-redeem actions)
        if (dom.redeemModal) {
            dom.redeemModal.addEventListener('click', function(e) {
                var opt = e.target.closest('[data-action="do-redeem"]');
                if (opt) {
                    doRedeem(opt.getAttribute('data-type'));
                }
            });
        }

        // Close buttons for redeem modal
        var closeBtns = ['modalCloseRedeem', 'modalCloseRedeemBtn'];
        closeBtns.forEach(function(id) {
            var el = document.getElementById(id);
            if (el) el.addEventListener('click', closeRedeem);
        });
    }

    // ═══════════════════════════════════════════
    //  SECTION: Set VIP Data (called by Profile)
    // ═══════════════════════════════════════════
    function setVipData(vipData) {
        state.vip = vipData;
        if (vipData) {
            renderVIP();
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Render
    // ═══════════════════════════════════════════
    function renderVIP() {
        var v = state.vip;
        if (!v) return;

        if (dom.vipCard) dom.vipCard.style.display = 'block';
        if (dom.vipCenterBanner) dom.vipCenterBanner.style.display = 'block';

        // Banner badge
        if (dom.vipCenterBadge) {
            dom.vipCenterBadge.textContent = '⭐ ' + (v.vip_level_name || '免费用户');
        }

        // Card badge
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

        // Data
        var totalAdCount = v.total_ad_count || 0;
        var threshold = v.bonus_threshold || 20;
        var todayAds = v.today_ads || 0;
        var maxAds = v.max_daily_ads || 0;
        var adRemaining = Math.max(0, maxAds - todayAds);

        updateVipAdInfo(todayAds, maxAds);

        // Progress bar & status text (left-right layout)
        if (v.vip_level === 'permanent') {
            dom.vipProgressBar.style.width = '100%';
            dom.vipProgressBar.style.background = 'linear-gradient(90deg, #ffd700, #ffed4a)';
            dom.vipRemaining.textContent = '🎉 永久会员';
            if (dom.vipStatusSub) dom.vipStatusSub.textContent = '今日可看广告 ' + maxAds + ' 次';
        } else if (v.vip_remaining) {
            var expireDate = new Date(v.vip_expire);
            var now = new Date();
            var total = expireDate - now;
            var vipMax = 7 * 24 * 3600 * 1000; // 7 days as 100%
            var vipPct = Math.min(100, Math.max(2, (total / vipMax) * 100));
            dom.vipProgressBar.style.width = vipPct + '%';
            dom.vipProgressBar.style.background = 'linear-gradient(90deg, #4caf50, #81c784)';
            dom.vipRemaining.textContent = '剩余: ' + v.vip_remaining;
            if (dom.vipStatusSub) dom.vipStatusSub.textContent = '里程碑 ' + totalAdCount + '/' + threshold + ' 次';
        } else {
            // Free user: show milestone progress (grey bar)
            var msPct = Math.min(98, Math.round((totalAdCount % threshold) / threshold * 100));
            if (totalAdCount === 0) msPct = 2;
            dom.vipProgressBar.style.width = msPct + '%';
            dom.vipProgressBar.style.background = 'linear-gradient(90deg, #666, #999)';
            dom.vipRemaining.textContent = '免费用户';
            if (dom.vipStatusSub) dom.vipStatusSub.textContent = '里程碑 ' + (totalAdCount % threshold) + '/' + threshold + ' 次';
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
        if (dom.wheelSpinBtn) {
            dom.wheelSpinBtn.disabled = remaining <= 0;
            dom.wheelSpinBtn.textContent = remaining > 0 ? ('🎰 转转盘（剩' + remaining + '次）') : '🎰 今日次数已用完';
        }

        // Plan cards
        updatePlanCards(v);
    }

    function updatePlanCards(v) {
        var allCards = document.querySelectorAll('.vip-plan-card');
        for (var i = 0; i < allCards.length; i++) { allCards[i].classList.remove('active'); }
        var allBadges = document.querySelectorAll('.vip-plan-card .plan-badge');
        for (var j = 0; j < allBadges.length; j++) { allBadges[j].textContent = '—'; }

        var totalAdCount = v.total_ad_count || 0;
        var threshold = v.bonus_threshold || 20;
        var maxAds = v.max_daily_ads || 3;

        if (v.vip_level === 'permanent') {
            // Permanent: all plan descriptions show actual values
            if (dom.planPermanent) dom.planPermanent.classList.add('active');
            if (dom.permanentPlanDesc) dom.permanentPlanDesc.textContent = '已解锁 · 全部功能永久使用';
            if (dom.permanentPlanBadge) {
                dom.permanentPlanBadge.textContent = '已解锁';
                dom.permanentPlanBadge.className = 'plan-badge plan-badge-p';
            }
            if (dom.freePlanDesc) dom.freePlanDesc.textContent = '每日' + maxAds + '次';
            if (dom.freePlanBadge) { dom.freePlanBadge.textContent = '解锁'; dom.freePlanBadge.className = 'plan-badge plan-badge-f'; }
            if (dom.basicPlanDesc) dom.basicPlanDesc.textContent = '每日' + maxAds + '次';
            if (dom.basicPlanBadge) { dom.basicPlanBadge.textContent = '解锁'; dom.basicPlanBadge.className = 'plan-badge plan-badge-b'; }
        } else {
            if (v.vip_level === 'basic') {
                // Basic: show actual maxAds (5 for basic, 3 for free)
                if (dom.planBasic) dom.planBasic.classList.add('active');
                if (dom.freePlanDesc) dom.freePlanDesc.textContent = '每日3次';
                if (dom.freePlanBadge) { dom.freePlanBadge.textContent = '已解锁'; dom.freePlanBadge.className = 'plan-badge plan-badge-f'; }
                if (dom.basicPlanDesc) dom.basicPlanDesc.textContent = '每日' + maxAds + '次';
                if (dom.basicPlanBadge) { dom.basicPlanBadge.textContent = '当前'; dom.basicPlanBadge.className = 'plan-badge plan-badge-b'; }
            } else {
                // Free
                if (dom.planFree) dom.planFree.classList.add('active');
                if (dom.freePlanDesc) dom.freePlanDesc.textContent = '每日' + maxAds + '次';
                if (dom.freePlanBadge) { dom.freePlanBadge.textContent = '当前'; dom.freePlanBadge.className = 'plan-badge plan-badge-f'; }
                if (dom.basicPlanDesc) dom.basicPlanDesc.textContent = '每日5次';
                if (dom.basicPlanBadge) { dom.basicPlanBadge.textContent = '可升级'; dom.basicPlanBadge.className = 'plan-badge plan-badge-b'; }
            }
            // Permanent plan: milestone progress
            if (dom.permanentPlanDesc) dom.permanentPlanDesc.textContent = '累计' + threshold + '次触发奖励';
            var nextMilestone = Math.ceil(totalAdCount / threshold) * threshold;
            if (dom.permanentPlanBadge) {
                dom.permanentPlanBadge.textContent = totalAdCount + '/' + nextMilestone;
                dom.permanentPlanBadge.className = 'plan-badge plan-badge-p';
            }
        }
    }

    // ═══════════════════════════════════════════
    //  SECTION: Ad Watching (v2 — one-click auto-claim)
    // ═══════════════════════════════════════════
    function updateVipAdInfo(todayAds, maxAds) {
        var remaining = Math.max(0, maxAds - todayAds);
        if (dom.vipAdBtnRemain) dom.vipAdBtnRemain.textContent = '（剩' + remaining + '次）';
        if (maxAds > 0 && remaining <= 0) {
            dom.vipAdWatchBtn.disabled = true;
            dom.vipAdWatchBtn.style.opacity = '0.4';
            if (dom.vipAdBtnIcon) dom.vipAdBtnIcon.textContent = '🚫';
            if (dom.vipAdBtnText) dom.vipAdBtnText.textContent = '今日已用完';
            if (dom.vipAdBtnRemain) dom.vipAdBtnRemain.textContent = '';
            dom.vipAdCountdown.textContent = '';
        } else {
            dom.vipAdWatchBtn.disabled = false;
            dom.vipAdWatchBtn.style.opacity = '1';
            if (dom.vipAdBtnIcon) dom.vipAdBtnIcon.textContent = '📺';
            if (dom.vipAdBtnText) dom.vipAdBtnText.textContent = '看广告赚时长';
        }
    }

    function watchVipAd() {
        if (state.vipAdWatching || state.vipAdClaiming) return;

        var todayAds = state.vip ? (state.vip.today_ads || 0) : 0;
        var maxAds = state.vip ? (state.vip.max_daily_ads || 0) : 0;
        if (maxAds > 0 && todayAds >= maxAds) {
            showToast('⚠️ 今日广告次数已用完');
            return;
        }

        state.vipAdWatching = true;
        state.vipAdSeconds = 8;
        var total = 8;

        // Show playback animation area
        if (dom.vipAdPlayback) dom.vipAdPlayback.style.display = 'flex';
        if (dom.vipAdSlot) {
            dom.vipAdSlot.innerHTML = '<div class="ad-progress-ring"><div class="ad-progress-fill"></div><span class="ad-timer-icon">📺</span></div>';
        }

        // Button: show countdown
        dom.vipAdWatchBtn.disabled = true;
        if (dom.vipAdBtnIcon) dom.vipAdBtnIcon.textContent = '⏳';
        if (dom.vipAdBtnText) dom.vipAdBtnText.textContent = total + 's';
        if (dom.vipAdBtnRemain) dom.vipAdBtnRemain.textContent = '';
        dom.vipAdCountdown.textContent = '广告播放中...';

        state.vipAdTimer = setInterval(function() {
            state.vipAdSeconds--;
            if (state.vipAdSeconds > 0) {
                if (dom.vipAdBtnText) dom.vipAdBtnText.textContent = state.vipAdSeconds + 's';
            } else {
                // Done — auto claim
                clearInterval(state.vipAdTimer);
                state.vipAdTimer = null;
                state.vipAdWatching = false;
                doClaimReward();
            }
        }, 1000);
    }

    function doClaimReward() {
        state.vipAdClaiming = true;
        if (dom.vipAdBtnIcon) dom.vipAdBtnIcon.textContent = '⏳';
        if (dom.vipAdBtnText) dom.vipAdBtnText.textContent = '领取中...';
        if (dom.vipAdBtnRemain) dom.vipAdBtnRemain.textContent = '';
        dom.vipAdCountdown.textContent = '正在验证...';

        api.watchAd().then(function(data) {
            if (data.success) {
                showToast(data.message || '✅ 观看完成！');
                loadVipStatus();  // refreshes everything including ad info
            } else {
                showToast('⚠️ ' + (data.message || '领取失败'));
                resetVipAdUI();
            }
        }).catch(function() {
            showToast('网络错误，请重试');
            resetVipAdUI();
        }).finally(function() {
            state.vipAdClaiming = false;
        });
    }

    function resetVipAdUI() {
        if (state.vipAdTimer) {
            clearInterval(state.vipAdTimer);
            state.vipAdTimer = null;
        }
        state.vipAdWatching = false;
        state.vipAdClaiming = false;
        state.vipAdSeconds = 0;

        if (dom.vipAdPlayback) dom.vipAdPlayback.style.display = 'none';
        if (dom.vipAdSlot) dom.vipAdSlot.innerHTML = '<span>📺</span>';
        if (dom.vipAdBtnIcon) dom.vipAdBtnIcon.textContent = '📺';
        if (dom.vipAdBtnText) dom.vipAdBtnText.textContent = '看广告赚时长';

        // Restore remain count
        var v = state.vip;
        if (v) {
            var todayAds = v.today_ads || 0;
            var maxAds = v.max_daily_ads || 0;
            var remaining = Math.max(0, maxAds - todayAds);
            if (dom.vipAdBtnRemain) dom.vipAdBtnRemain.textContent = '（剩' + remaining + '次）';
        }

        dom.vipAdWatchBtn.disabled = false;
        dom.vipAdWatchBtn.style.opacity = '1';
        dom.vipAdWatchBtn.setAttribute('data-action', 'watch-ad');
        dom.vipAdCountdown.textContent = '';
    }

    // Backward compat: claimVipAdReward → doClaimReward (for BaiduAd callbacks if any)
    function claimVipAdReward() {
        doClaimReward();
    }

    // ═══════════════════════════════════════════
    //  SECTION: Check-in
    // ═══════════════════════════════════════════
    function doCheckin() {
        dom.checkinBtn.disabled = true;
        dom.checkinBtn.textContent = '签到中...';
        api.checkin().then(function(data) {
            if (data.success) {
                showToast(data.message || '签到成功！');
                loadVipStatus();
            } else {
                showToast('⚠️ ' + (data.message || '签到失败'));
                dom.checkinBtn.disabled = false;
                dom.checkinBtn.textContent = '✅ 每日签到';
            }
        }).catch(function() {
            showToast('网络错误，请重试');
            dom.checkinBtn.disabled = false;
            dom.checkinBtn.textContent = '✅ 每日签到';
        });
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

    function doRedeem(type) {
        api.redeem(type).then(function(data) {
            if (data.success) {
                showToast(data.message || '兑换成功！');
                closeRedeem();
                loadVipStatus();
            } else {
                showToast('⚠️ ' + (data.message || '兑换失败'));
            }
        }).catch(function() {
            showToast('网络错误，请重试');
        });
    }

    // ═══════════════════════════════════════════
    //  SECTION: VIP Status Refresh
    // ═══════════════════════════════════════════
    function loadVipStatus() {
        return api.getVipStatus().then(function(data) {
            if (data.success) {
                state.vip = data;
                renderVIP();
            }
        }).catch(function(e) {
            console.error('加载VIP状态失败:', e);
        });
    }

    function getVipData() {
        return state.vip;
    }

    // For external async use (returns promise)
    function fetchVipStatus() {
        return api.getVipStatus();
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

    function spinWheel() {
        if (state.wheelSpinning) return;
        if (state.wheelRemaining <= 0) {
            showToast('今日次数已用完');
            return;
        }

        state.wheelSpinning = true;
        if (dom.wheelSpinBtn) dom.wheelSpinBtn.disabled = true;

        api.spinWheel().then(function(data) {
            if (data.success) {
                var targetSegment = 0;
                if (typeof data.prize_index === 'number') {
                    targetSegment = data.prize_index;
                } else {
                    targetSegment = wheelPrizes.indexOf(data.prize_name);
                    if (targetSegment < 0) targetSegment = 0;
                }

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
                        state.wheelSpinning = false;
                        showToast(data.message);
                        loadVipStatus();
                    }
                }
                requestAnimationFrame(animateSpin);

            } else {
                state.wheelSpinning = false;
                showToast('⚠️ ' + (data.message || '转盘抽奖失败'));
                loadVipStatus();
            }
        }).catch(function() {
            state.wheelSpinning = false;
            if (dom.wheelSpinBtn) dom.wheelSpinBtn.disabled = false;
            showToast('网络错误，请重试');
            loadVipStatus();
        });
    }

    // ═══════════════════════════════════════════
    //  Public API
    // ═══════════════════════════════════════════
    return {
        init: init,
        setVipData: setVipData,
        getVipData: getVipData,
        fetchVipStatus: fetchVipStatus,
        loadVipStatus: loadVipStatus,
        watchVipAd: watchVipAd,
        claimVipAdReward: claimVipAdReward,
        doCheckin: doCheckin,
        openRedeem: openRedeem,
        closeRedeem: closeRedeem,
        doRedeem: doRedeem,
        spinWheel: spinWheel,
        drawWheel: drawWheel
    };

})();
