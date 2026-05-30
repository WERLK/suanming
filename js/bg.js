/**
 * 玄机算命网 - 动态宇宙粒子背景
 * Canvas 粒子系统：星点飘浮 + 连线 + 鼠标交互 + 渐变光晕
 */
(function() {
    'use strict';

    var canvas, ctx;
    var particles = [];
    var animId;
    var mouse = { x: -9999, y: -9999, active: false };
    var width, height;
    var isMobile = window.innerWidth < 768;

    // 配置
    var config = {
        particleCount: isMobile ? 60 : 120,
        minRadius: 0.5,
        maxRadius: 2.5,
        connectDistance: isMobile ? 80 : 150,
        lineAlpha: 0.08,
        speed: 0.3,
        mouseRadius: 120,
        mouseForce: 0.03,
        colors: [
            'rgba(255,215,0,OPACITY)',     // 金色
            'rgba(200,180,255,OPACITY)',    // 淡紫
            'rgba(100,180,255,OPACITY)',    // 淡蓝
            'rgba(255,255,255,OPACITY)',    // 白色
            'rgba(180,220,255,OPACITY)'     // 浅蓝白
        ]
    };

    // ===== 粒子类 =====
    function Particle() {
        this.reset(true);
    }

    Particle.prototype.reset = function(init) {
        this.x = Math.random() * width;
        this.y = init ? Math.random() * height : (Math.random() < 0.5 ? -20 : height + 20);
        this.vx = (Math.random() - 0.5) * config.speed;
        this.vy = (Math.random() - 0.5) * config.speed;
        this.radius = config.minRadius + Math.random() * (config.maxRadius - config.minRadius);
        this.colorIdx = Math.floor(Math.random() * config.colors.length);
        this.alpha = 0.3 + Math.random() * 0.7;
        this.pulseSpeed = 0.005 + Math.random() * 0.02;
        this.pulseOffset = Math.random() * Math.PI * 2;
    };

    Particle.prototype.update = function() {
        // 鼠标交互
        if (mouse.active) {
            var dx = this.x - mouse.x;
            var dy = this.y - mouse.y;
            var dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < config.mouseRadius && dist > 0) {
                var force = (config.mouseRadius - dist) / config.mouseRadius;
                this.vx += (dx / dist) * force * config.mouseForce;
                this.vy += (dy / dist) * force * config.mouseForce;
            }
        }

        // 速度衰减
        this.vx *= 0.999;
        this.vy *= 0.999;

        this.x += this.vx;
        this.y += this.vy;

        // 边界环绕
        var margin = 20;
        if (this.x < -margin) this.x = width + margin;
        if (this.x > width + margin) this.x = -margin;
        if (this.y < -margin) this.y = height + margin;
        if (this.y > height + margin) this.y = -margin;
    };

    Particle.prototype.draw = function() {
        var pulse = Math.sin(Date.now() * this.pulseSpeed + this.pulseOffset) * 0.3 + 0.7;
        var alpha = this.alpha * pulse;
        var color = config.colors[this.colorIdx].replace('OPACITY', alpha.toFixed(2));

        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);

        // 发光效果
        var glow = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius * 3);
        glow.addColorStop(0, color);
        glow.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = glow;
        ctx.fill();

        // 实心核心
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius * 0.5, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
    };

    // ===== 绘制连线 =====
    function drawConnections() {
        for (var i = 0; i < particles.length; i++) {
            for (var j = i + 1; j < particles.length; j++) {
                var dx = particles[i].x - particles[j].x;
                var dy = particles[i].y - particles[j].y;
                var dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < config.connectDistance) {
                    var alpha = (1 - dist / config.connectDistance) * config.lineAlpha;
                    ctx.strokeStyle = 'rgba(255,215,0,' + alpha.toFixed(3) + ')';
                    ctx.lineWidth = 0.4;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    // ===== 绘制背景光晕 =====
    var glowTime = 0;
    function drawAmbientGlow() {
        glowTime += 0.003;
        // 左上
        var g1 = ctx.createRadialGradient(width * 0.2, height * 0.3, 0, width * 0.2, height * 0.3, width * 0.5);
        var a1 = 0.03 + Math.sin(glowTime) * 0.01;
        g1.addColorStop(0, 'rgba(100,120,255,' + a1.toFixed(3) + ')');
        g1.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = g1;
        ctx.fillRect(0, 0, width, height);

        // 右下
        var g2 = ctx.createRadialGradient(width * 0.75, height * 0.6, 0, width * 0.75, height * 0.6, width * 0.4);
        var a2 = 0.04 + Math.cos(glowTime * 1.3) * 0.015;
        g2.addColorStop(0, 'rgba(255,180,100,' + a2.toFixed(3) + ')');
        g2.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = g2;
        ctx.fillRect(0, 0, width, height);
    }

    // ===== 主循环 =====
    function animate() {
        ctx.clearRect(0, 0, width, height);

        // 背景光晕
        drawAmbientGlow();

        // 粒子
        for (var i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
        }

        // 连线（移动端跳过以节省性能）
        if (!isMobile) {
            drawConnections();
        }

        animId = requestAnimationFrame(animate);
    }

    // ===== 初始化 =====
    function init() {
        canvas = document.createElement('canvas');
        canvas.id = '__bgCanvas';
        canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:1;pointer-events:none;';
        document.body.insertBefore(canvas, document.body.firstChild);

        ctx = canvas.getContext('2d');
        resize();
        createParticles();

        window.addEventListener('resize', onResize);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseleave', onMouseLeave);
        document.addEventListener('touchmove', onTouchMove, { passive: true });
        document.addEventListener('touchend', onMouseLeave);

        animate();
    }

    function createParticles() {
        particles = [];
        for (var i = 0; i < config.particleCount; i++) {
            particles.push(new Particle());
        }
    }

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
        isMobile = width < 768;
        config.connectDistance = isMobile ? 80 : 150;
    }

    var resizeTimer;
    function onResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            resize();
            createParticles();
        }, 200);
    }

    function onMouseMove(e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        mouse.active = true;
    }

    function onMouseLeave() {
        mouse.active = false;
    }

    function onTouchMove(e) {
        if (e.touches.length > 0) {
            mouse.x = e.touches[0].clientX;
            mouse.y = e.touches[0].clientY;
            mouse.active = true;
        }
    }

    // ===== 启动 =====
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
