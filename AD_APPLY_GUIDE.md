# 广告联盟账户申请资料

## 一、Google AdSense 申请资料

### 网站信息
- **网站名称**：玄机算命网
- **网站地址**：https://webview.e2b.bj7.sandbox.cloudstudio.club/（上线后替换成你的域名）
- **网站描述**：
  > 玄机算命网是一个面向中文用户的在线算命平台，提供八字排盘、紫微斗数、生肖运势、黄道吉日、姻缘配对、风水布局、起名改名、周公解梦等多种命理服务。平台采用会员制，用户可通过观看广告免费领取会员时长。

### 内容类型
- [x] 娱乐
- [x] 生活方式
- [x]  spirituality / 命理

### 流量来源
- 搜索引擎（百度、Google）
- 社交媒体（微信、微博、小红书）
- 直接访问

### 收款信息（审核通过后填）
- 收款方式：银行电汇 / 支票
- 币种：人民币（CNY）或美元（USD）

---

## 二、有乐付（Youlefu）申请资料

### 媒体信息
- **媒体名称**：玄机算命网
- **媒体类型**：Web / H5
- **媒体地址**：（上线后填你的域名）
- **日均 PV**：（填真实估算，如：500 / 2000 / 10000）
- **日均 UV**：（填真实估算，如：100 / 500 / 2000）

### 推广方式
-  SEO / 搜索引擎优化
- 社交媒体分享（微信、微博）
- 社群运营（Q群、微信群）

### 收款信息
- **收款人姓名**：（你的真实姓名，与身份证一致）
- **身份证号**：（审核通过后填）
- **收款方式**：支付宝 / 银行卡
- **支付宝账号**：（审核通过后填）
- **银行卡号**：（审核通过后填）

### 接入方式
- 选择：Offerwall（激励墙）
- 广告位描述：用户完成激励任务 → 免费领取1天VIP会员

---

## 三、申请步骤速查

### Google AdSense
1. 打开 https://www.google.com/adsense/start/
2. 登录你的 Google 账号（Gmail）
3. 输入网站地址
4. 填写收款信息（姓名、地址）
5. 等待审核（6-8周，耐心等）
6. 审核通过后，复制 `data-ad-client="ca-pub-XXXX"` 里的 `XXXX`
7. 把 `XXXX` 填到 `index.html` 的 `YOUR_PUB_ID`

### 有乐付
1. 打开 https://www.youlefu.com/
2. 点「媒体主入驻」
3. 填媒体信息（名称、地址、流量）
4. 等待审核（3-5工作日）
5. 审核通过后，在后台获取 `pub_id`
6. 把 `pub_id` 填到 `index.html` 的 `YOUR_PUB_ID`

---

## 四、配置代码（审核通过后用）

### 有乐付 — 替换 index.html 第 ~1068 行
```javascript
function startYoulefu() {
    var PUB_ID = 'YOUR_REAL_PUB_ID';  // ← 替换成真实 pub_id

    if (PUB_ID === 'YOUR_REAL_PUB_ID') {
        showToast('请配置有乐付 pub_id');
        mockAd();
        return;
    }

    window.YLF && window.YLF.show({
        pubId: PUB_ID,
        userId: currentUser.phone,
        onReward: function(reward) { grantAdReward(); },
        onClose: function() { showToast('已关闭广告'); }
    });
}
```

### Google AdSense — 替换 index.html 第 ~1046 行
```javascript
function startGoogleAd() {
    var PUB_ID = 'YOUR_REAL_PUB_ID';  // ← 替换成真实 data-ad-client

    if (PUB_ID === 'YOUR_REAL_PUB_ID') {
        showToast('请配置 Google AdSense');
        mockAd();
        return;
    }

    // 展示 Google 激励广告（需要 AdMob + 应用壳）
    showToast('Google 激励广告需要应用壳，当前使用模拟模式');
    mockAd();
}
```

---

## 五、现在能做什么？

✅ **不用等审核**，现在就能用 mock 模式跑通流程：
1. 打开预览链接
2. 登录 → 点「我的」→ 开通会员
3. 点「立即观看」
4. 等 15 秒 → 自动获得 1 天免费会员 ✅

等审核通过后，**只改一行** `var AD_MODE = 'youlfu';` 就能切到真实广告 ⚡

---

## 六、申请遇到问题？

- Google AdSense 审核慢 → 先用 mock 跑用户量，等流量起来再申
- 有乐付审核不过 → 检查网站是否有备案号 + 实名认证
- 两个都不过 → 继续用 mock，流量到 1万/日 后再申

---

**祝你申请顺利！审核通过后把 pub_id 发我，我帮你一键配置 ✅**
