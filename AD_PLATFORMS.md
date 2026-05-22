# 玄机算命网 - 广告对接配置指南

## 当前状态

`watchAd()` 函数已支持**可配置广告平台**接入。

---

## 个人可申请的广告平台（按推荐顺序）

### 1. Youlefu（有乐付）⽤ 推荐
- **官网**：https://www.youlefu.com/
- **资质要求**：✅ 个人可申请（身份证 + 网站备案）
- **接⼊类型**：Offerwall（⽤ 推荐）
- **结算**：⽬ 付宝 / 银⾏ 卡
- **对接⽅ 式**：在 `watchAd()` 内调⽤ 他们的 JS SDK

示例（接⼊后替换 `watchAd()` 内容）：
```javascript
function watchAd() {
    if (!currentUser) { showToast('请先登录'); return; }
    // 有乐付 Offerwall 对接
    window.YLF && window.YLF.show({
        pubId: 'YOUR_PUB_ID',   // 替换成你的 pubId
        userId: currentUser.phone,
        onReward: function(reward) {
            // ⽙ ⽙ ⽙ ⽙ ⽙ 回调：⽤ 户完成 offer
            grantAdReward();
        },
        onClose: function() { showToast('已取消'); }
    });
}
```

---

### 2. Tapjoy Offerwall（海外）
- **官⽹ **：https://www.tapjoy.com/
- **个⼈ 可接**：✅（需⽹ ⽣ 址 + ⼀ ⽗ 量）
- **适⽤ ⽆ ⽑**：主要海外⽤ 户
- **对接⽅ 式**：类似上述，JS SDK 嵌⼊ 

---

### 3. AdScend Media Offerwall
- **官⽹ **：https://www.adscendmedia.com/
- **个⼈ 可接**：✅
- **要求**：⽹ ⽘ 有流量 / 社区 

---

### 4. ⽚ ⽚ 量汇 / 穿⼭ 甲（国内正规，但需企业）
- 优量汇：https://e.qq.com/ （⚝️ 需企业营业执照）
- 穿⼭ 甲：https://www.chuanshanjia.com/ （⚝️ 需企业）
- **个⼈ 可过审的替代**：⽤ ⽹ ⽚ ⽙ ⽚ 代接（⚠️ 有⻛ 险，不推荐）

---

## 现在可以怎样测试？

### ⽚ ⽴ 式 A：继续⽤ 拟（现在就能跑）
当前 `watchAd()` 已有 mock 模式：
- 15 秒倒计时 → ⽙ ⽙ ⽑ 领取会员
- ⽚ ⽵ 试步骤：登录 → 我的 → 开通会员 → ⽚ 看⼴ ⽴ 频 → ⽙ ⽙ ⽑ 领取

### ⽴ ⽴ 式 B：接⼊ Youlefu（个⼈ 可接，需申请）
1. 去 https://www.youlefu.com/ 注册
2. 创建应⽤ → 获取 `pubId`
3. 在 `index.html` 的 `watchAd()` 中替换 `YOUR_PUB_ID_HERE`
4. 引⼊ 他们的 JS SDK（按官⽅ 拷⻚ ）
5. 测试 → 上⽤ 

---

## 快速配置（你只需要改这⾏ 个地⽅ ）

在 `/workspace/index.html` 中找到这⾏ ：

```javascript
function watchAd() {
    ...
    // pub_id 替换成你在优量汇后台拿到的媒体ID
    var PUB_ID = 'YOUR_PUB_ID_HERE';
    var SLOT_ID = 'YOUR_SLOT_ID_HERE';
```

把 `YOUR_PUB_ID_HERE` 和 `YOUR_SLOT_ID_HERE` 替换成真实 ID 即可。

---

## 如果你现在就想"看起来是真的"

我可以帮你加⼊ ⼀ 个**假装播放广告**的 UI（15 秒进度条 + ⽚ ⽴ 按钮），⽤ 户体验更真实。

**需要我加吗？**  // 在 watchAd() 里加⼊ 进度条 UI