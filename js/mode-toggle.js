/**
 * 专业/初学模式切换 - 共享组件 v1.0
 * 所有算命模块通用，提供模式切换UI和简化渲染逻辑
 */
(function(global) {
    'use strict';

    var STORAGE_KEY = 'suanming_mode';        // 全局模式偏好
    var DEFAULT_MODE = 'pro';

    /**
     * ModeToggle 核心对象
     */
    var ModeToggle = {
        // 当前模式
        _mode: null,

        /**
         * 获取当前模式（优先读取DOM，其次localStorage，最后默认值）
         */
        getMode: function() {
            if (this._mode) return this._mode;
            var el = document.getElementById('globalModeSelect');
            if (el && el.value) {
                this._mode = el.value;
                return this._mode;
            }
            try {
                var saved = localStorage.getItem(STORAGE_KEY);
                if (saved && (saved === 'pro' || saved === 'simple')) {
                    this._mode = saved;
                    return this._mode;
                }
            } catch(e) {}
            this._mode = DEFAULT_MODE;
            return this._mode;
        },

        /**
         * 设置模式
         */
        setMode: function(mode) {
            this._mode = mode;
            try { localStorage.setItem(STORAGE_KEY, mode); } catch(e) {}
            // 同步所有同页面toggle
            var pills = document.querySelectorAll('.mode-toggle-pill');
            for (var i = 0; i < pills.length; i++) {
                var opts = pills[i].querySelectorAll('.mode-toggle-option');
                for (var j = 0; j < opts.length; j++) {
                    if (opts[j].dataset.mode === mode) {
                        opts[j].classList.add('active');
                    } else {
                        opts[j].classList.remove('active');
                    }
                }
            }
            // 同步select元素
            var sel = document.getElementById('globalModeSelect');
            if (sel) sel.value = mode;
            // 同步body class
            if (mode === 'simple') {
                document.body.classList.add('mode-simple');
            } else {
                document.body.classList.remove('mode-simple');
            }
            // 触发自定义事件
            var event = new CustomEvent('modechange', { detail: { mode: mode } });
            document.dispatchEvent(event);
        },

        /**
         * 判断是否为初学模式
         */
        isSimple: function() {
            return this.getMode() === 'simple';
        },

        /**
         * 在指定容器中注入模式切换UI
         * @param {string|Element} container - CSS选择器或DOM元素
         * @param {Object} options
         * @param {string} options.label - 标签文字，默认"排盘模式"
         * @param {string} options.proLabel - 专业模式标签，默认"专业模式"
         * @param {string} options.simpleLabel - 初学模式标签，默认"新手模式"
         * @param {Function} options.onChange - 模式切换回调(mode)
         * @returns {HTMLElement} 创建的wrapper元素
         */
        injectUI: function(container, options) {
            options = options || {};
            var label = options.label || '排盘模式';
            var proLabel = options.proLabel || '专业模式';
            var simpleLabel = options.simpleLabel || '新手模式';
            var currentMode = this.getMode();

            var target;
            if (typeof container === 'string') {
                target = document.querySelector(container);
            } else {
                target = container;
            }
            if (!target) return null;

            var wrapper = document.createElement('div');
            wrapper.className = 'mode-toggle-wrapper';

            var lbl = document.createElement('span');
            lbl.className = 'mode-toggle-label';
            lbl.textContent = label;
            wrapper.appendChild(lbl);

            var pill = document.createElement('div');
            pill.className = 'mode-toggle-pill';

            var proOpt = document.createElement('div');
            proOpt.className = 'mode-toggle-option' + (currentMode === 'pro' ? ' active' : '');
            proOpt.dataset.mode = 'pro';
            proOpt.textContent = proLabel;

            var simpleOpt = document.createElement('div');
            simpleOpt.className = 'mode-toggle-option' + (currentMode === 'simple' ? ' active' : '');
            simpleOpt.dataset.mode = 'simple';
            simpleOpt.textContent = simpleLabel;

            var self = this;
            proOpt.addEventListener('click', function() {
                self.setMode('pro');
                if (options.onChange) options.onChange('pro');
            });
            simpleOpt.addEventListener('click', function() {
                self.setMode('simple');
                if (options.onChange) options.onChange('simple');
            });

            pill.appendChild(proOpt);
            pill.appendChild(simpleOpt);
            wrapper.appendChild(pill);

            target.appendChild(wrapper);

            // 初始化body class
            if (currentMode === 'simple') {
                document.body.classList.add('mode-simple');
            }

            return wrapper;
        },

        /**
         * 渲染简化的通用结果卡片
         * @param {Object} data - API返回的数据
         * @param {string} moduleName - 模块名称
         * @param {string} targetSelector - 结果容器选择器
         */
        renderSimpleResult: function(data, moduleName, targetSelector) {
            var target = typeof targetSelector === 'string' ?
                document.querySelector(targetSelector) : targetSelector;
            if (!target) return;

            var html = '<div class="beginner-result">';

            // 卡片1：模块名称
            html += '<div class="beginner-card">';
            html += '<h3>' + moduleName + '</h3>';
            if (data.summary) {
                html += '<p>' + data.summary + '</p>';
            } else if (data.prediction) {
                html += '<p>' + data.prediction + '</p>';
            }
            html += '</div>';

            // 卡片2：评分（如果有）
            if (data.scores && typeof data.scores === 'object') {
                html += '<div class="beginner-card"><h3>评分总览</h3>';
                html += '<div class="beginner-score-grid">';
                var keys = Object.keys(data.scores);
                for (var i = 0; i < keys.length; i++) {
                    var k = keys[i];
                    html += '<div class="beginner-score-item">';
                    html += '<div class="score-label">' + k + '</div>';
                    html += '<div class="score-value">' + data.scores[k] + '</div>';
                    html += '</div>';
                }
                html += '</div></div>';
            }

            // 卡片3：幸运元素（如果有）
            if (data.lucky_elements) {
                var le = data.lucky_elements;
                html += '<div class="beginner-card"><h3>幸运指引</h3>';
                if (le.colors) html += '<p>🎨 幸运色：<span class="highlight">' + le.colors + '</span></p>';
                if (le.numbers) html += '<p>🔢 幸运数字：<span class="highlight">' + le.numbers + '</span></p>';
                if (le.directions) html += '<p>🧭 吉方：<span class="highlight">' + le.directions + '</span></p>';
                html += '</div>';
            }

            // 卡片4：建议
            if (data.advice) {
                html += '<div class="beginner-card"><h3>建议</h3><p>' + data.advice + '</p></div>';
            } else if (data.suggestion) {
                html += '<div class="beginner-card"><h3>建议</h3><p>' + data.suggestion + '</p></div>';
            }

            html += '</div>';
            target.innerHTML = html;
        },

        /**
         * 渲染简化的一键分析结果（用于无具体API数据的模块）
         * @param {string} moduleName - 模块名称
         * @param {string} category - 模块分类
         * @param {string} targetSelector - 结果容器选择器
         */
        renderSimpleStatic: function(moduleName, category, targetSelector) {
            var target = typeof targetSelector === 'string' ?
                document.querySelector(targetSelector) : targetSelector;
            if (!target) return;

            var tips = {
                '八字命理': '八字排盘通过分析出生时间的天干地支，揭示你的先天命格和后天运势走向。',
                '紫微斗数': '紫微斗数以命宫为核心，通过十二宫位的星曜分布，全面展现人生各个领域。',
                '生肖运势': '生肖运势结合流年太岁和生肖五行，预测年度整体运势和注意事项。',
                '姓名学': '姓名学通过分析姓名的笔画、五行、音律等要素，评判名字对运势的影响。',
                '面相学': '面相学通过观察面部五官、气色、骨相等特征，推断性格和命运趋势。',
                '手相学': '手相学通过手掌纹路、形态、色泽等特征，分析人生各阶段的运势。',
                '风水堪舆': '风水学通过分析环境布局与气场的互动，提供改善运势的空间调整建议。',
                '周公解梦': '解梦学通过分析梦境中的符号和情节，揭示潜意识和未来预兆。',
                '塔罗牌占卜': '塔罗牌通过牌面的象征意义和排列组合，为具体问题提供启示和指引。',
                '黄道吉日': '黄道吉日根据天干地支和神煞分布，选择最有利的日期进行重要活动。',
                '六爻占卜': '六爻占卜通过摇卦得出的卦象和爻辞，对具体问题进行预测和判断。',
                '血型性格': '血型性格学通过血型分析性格特征、行为模式和人际关系倾向。',
                '星座运势': '星座运势结合星象运行和星座特质，预测各星座在不同领域的运势。',
                '奇门遁甲': '奇门遁甲通过天盘、地盘、人盘、神盘的组合，进行高精度预测和谋略规划。',
                '太乙神数': '太乙神数以天文历法为基础，通过数理推算进行宏观预测。',
                '铁板神数': '铁板神数以数字密码为核心，通过精密计算进行人生预测。',
                '梅花易数': '梅花易数以卦象变化为基础，通过象数理占进行灵活预测。',
                '数字能量': '数字能量学通过分析数字的五行属性和能量场，评判其对运势的影响。',
                '符咒化解': '符咒化解通过符箓和咒语的能量，化解不利因素，增强吉祥运势。',
                '择吉文化': '择吉文化通过传统历法和民俗智慧，选择最佳时机进行各项活动。'
            };

            var tip = tips[category] || '本模块通过专业分析，为你提供详尽的命理解读和运势指引。';

            var html = '<div class="beginner-result">';
            html += '<div class="beginner-card"><h3>📋 ' + moduleName + '</h3><p>' + tip + '</p></div>';
            html += '<div class="beginner-card"><h3>💡 温馨提示</h3><p>切换到<strong style="color:#e8b84b">专业模式</strong>可查看完整分析内容，包括详细数据、历史文化和实用技巧。</p></div>';
            html += '</div>';
            target.innerHTML = html;
        }
    };

    // 导出到全局
    global.ModeToggle = ModeToggle;

    // DOM加载完成后自动同步body class
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            if (ModeToggle.isSimple()) {
                document.body.classList.add('mode-simple');
            }
        });
    } else {
        if (ModeToggle.isSimple()) {
            document.body.classList.add('mode-simple');
        }
    }

})(window);
