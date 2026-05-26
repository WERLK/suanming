#!/usr/bin/env python3
"""
修复 zhougong.html 和 huangdao.html：
1. 补充 imageAnalysisArea + imageAnalysisResult 区域
2. 补充 showDreamDetail / showEventDetail 的完整分析内容
"""

import re

# ========== 1. 修复 zhougong.html ==========
with open('modules/zhougong.html', 'r', encoding='utf-8') as f:
    zg = f.read()

# 加 imageAnalysisArea（在 content-area 内，section 前）
if 'id="imageAnalysisArea"' not in zg:
    area_html = '''
        <!-- 图片分析结果区域 -->
        <div class="image-analysis-area" id="imageAnalysisArea" style="display:none; margin-top:1.5rem;">
            <div style="background:linear-gradient(135deg,rgba(255,215,0,0.08),rgba(255,215,0,0.02));border:1px solid rgba(255,215,0,0.15);border-radius:12px;padding:1.5rem;">
                <h3 style="color:#ffd700;margin-bottom:1rem;">📷 图片分析结果</h3>
                <div id="imageAnalysisResult" style="color:rgba(255,255,255,0.85);line-height:1.8;font-size:0.9rem;white-space:pre-wrap;"></div>
                <button type="button" onclick="document.getElementById('imageAnalysisArea').style.display='none';" style="margin-top:1rem;background:rgba(255,215,0,0.2);color:#ffd700;border:1px solid rgba(255,215,0,0.3);border-radius:8px;padding:0.5rem 1rem;cursor:pointer;">关闭</button>
            </div>
        </div>
'''
    # 插到最后一个 </div> 前（content-area 的关闭标签前）
    zg = re.sub(r'(\s*</div>\s*</body>)', area_html + r'\1', zg, count=1)

# 补充 showDreamDetail 完整内容
old_dream = r'''switch(category) {
                case 'animal':
                    content = '<div class="section"><h2>🐉 动物类梦境</h2><p>动物在梦境中通常代表本能、情感、或特定人物。</p><ul><li><strong>蛇</strong>：财富、智慧、贵人/小人</li><li><strong>鱼</strong>：财运、机遇</li><li><strong>龙</strong>：权力、成功、大贵人</li><li><strong>虎</strong>：权威、挑战、困难</li></ul></div>';
                    break;
                case 'nature':
                    content = '<div class="section"><h2>🌊 自然类梦境</h2><p>自然现象在梦境中通常代表情绪状态、人生变化。</p><ul><li><strong>水</strong>：情感、财运</li><li><strong>火</strong>：激情、愤怒、危险</li><li><strong>山</strong>：障碍、目标、依靠</li><li><strong>风</strong>：变化、消息、自由</li></ul></div>';
                    break;
                case 'people':
                    content = '<div class="section"><h2>👥 人物类梦境</h2><p>人物在梦境中通常代表关系、自我投射。</p><ul><li><strong>去世亲人</strong>：庇佑、牵挂、指引</li><li><strong>陌生人</strong>：未知、新机遇</li><li><strong>恋人</strong>：感情状态、内心渴望</li><li><strong>小孩</strong>：纯真、新开始、内在潜能</li></ul></div>';
                    break;
                case 'buildings':
                    content = '<div class="section"><h2>🏠 建筑类梦境</h2><p>建筑物在梦境中通常代表自我、家庭、人生状态。</p><ul><li><strong>房屋</strong>：家庭、内在自我</li><li><strong>礼堂</strong>：庆典、成功、喜事</li><li><strong>厕所</strong>：净化、释放、隐私</li><li><strong>楼梯</strong>：上升/下降、进步/退步</li></ul></div>';
                    break;
            }'''

new_dream = r'''switch(category) {
                case 'animal':
                    content = `<div class="section">
                        <h2>🐉 动物类梦境详解</h2>
                        <p>动物在梦境中通常代表本能、情感、或特定人物。不同动物有不同寓意：</p>
                        <table class="result-table">
                            <tr><th>动物</th><th>基本寓意</th><th>吉凶预判</th></tr>
                            <tr><td>蛇</td><td>财富、智慧、贵人</td><td class="lucky">大吉（被蛇咬需防小人）</td></tr>
                            <tr><td>鱼</td><td>财运、机遇</td><td class="lucky">吉（活鱼吉，死鱼凶）</td></tr>
                            <tr><td>龙</td><td>权力、成功</td><td class="lucky">大吉</td></tr>
                            <tr><td>虎</td><td>权威、挑战</td><td class="unlucky">半吉半凶（看情境）</td></tr>
                            <tr><td>鼠</td><td>机敏、小人</td><td class="unlucky">凶（被鼠咬需防破财）</td></tr>
                            <tr><td>牛</td><td>勤奋、稳重</td><td class="lucky">吉（牛耕地主丰收）</td></tr>
                        </table>
                    </div>`;
                    break;
                case 'nature':
                    content = `<div class="section">
                        <h2>🌊 自然类梦境详解</h2>
                        <p>自然现象在梦境中通常代表情绪状态、人生变化。解读要点：</p>
                        <table class="result-table">
                            <tr><th>自然现象</th><th>基本寓意</th><th>吉凶预判</th></tr>
                            <tr><td>清水</td><td>财源滚滚、心情愉悦</td><td class="lucky">大吉</td></tr>
                            <tr><td>浑水</td><td>情感纠纷、财务风险</td><td class="unlucky">凶</td></tr>
                            <tr><td>大火</td><td>激情、重大变化</td><td class="lucky">吉（火旺主事成）</td></tr>
                            <tr><td>大风</td><td>变化、消息、动荡</td><td class="unlucky">半凶（防出行不利）</td></tr>
                            <tr><td>高山</td><td>障碍、目标、依靠</td><td class="lucky">吉（登山主事业有成）</td></tr>
                            <tr><td>洪水</td><td>重大转变、情绪泛滥</td><td class="unlucky">凶（防破财伤身）</td></tr>
                        </table>
                    </div>`;
                    break;
                case 'people':
                    content = `<div class="section">
                        <h2>👥 人物类梦境详解</h2>
                        <p>人物在梦境中通常代表关系、自我投射。不同人物寓意不同：</p>
                        <table class="result-table">
                            <tr><th>人物类型</th><th>基本寓意</th><th>吉凶预判</th></tr>
                            <tr><td>去世亲人</td><td>庇佑、牵挂、指引</td><td class="lucky">大吉（面带微笑主福荫）</td></tr>
                            <tr><td>恋人/配偶</td><td>感情状态、内心渴望</td><td class="lucky">吉（牵手主感情和睦）</td></tr>
                            <tr><td>陌生人</td><td>未知、新机遇</td><td class="lucky">半吉（看表情）</td></tr>
                            <tr><td>小孩</td><td>纯真、新开始</td><td class="lucky">吉（小孩笑主喜事）</td></tr>
                            <tr><td>已故名人</td><td>榜样、人生指引</td><td class="lucky">吉（得指点主进步）</td></tr>
                        </table>
                    </div>`;
                    break;
                case 'buildings':
                    content = `<div class="section">
                        <h2>🏠 建筑类梦境详解</h2>
                        <p>建筑物在梦境中通常代表自我、家庭、人生状态。</p>
                        <table class="result-table">
                            <tr><th>建筑物</th><th>基本寓意</th><th>吉凶预判</th></tr>
                            <tr><td>新房/大屋</td><td>家运亨通、人生新阶</td><td class="lucky">大吉</td></tr>
                            <tr><td>老房/破屋</td><td>怀旧、停滞、健康隐忧</td><td class="unlucky">凶（需防家人健康）</td></tr>
                            <tr><td>礼堂/宴席</td><td>庆典、成功、喜事临近</td><td class="lucky">大吉</td></tr>
                            <tr><td>厕所/污秽</td><td>净化、释放、去霉运</td><td class="lucky">半吉（去旧迎新）</td></tr>
                            <tr><td>高楼/电梯</td><td>上升、进步、目标达成</td><td class="lucky">吉（登高主事业有成）</td></tr>
                        </table>
                    </div>`;
                    break;
            }'''

if old_dream in zg:
    zg = zg.replace(old_dream, new_dream)
    print('  ✓ zhougong.html: 补充了 showDreamDetail 完整内容')
else:
    print('  ✗ zhougong.html: 未找到旧 showDreamDetail 内容，跳过')

with open('modules/zhougong.html', 'w', encoding='utf-8') as f:
    f.write(zg)
print('✓ zhougong.html 修复完成')

# ========== 2. 修复 huangdao.html ==========
with open('modules/huangdao.html', 'r', encoding='utf-8') as f:
    hd = f.read()

# 加 imageAnalysisArea
if 'id="imageAnalysisArea"' not in hd:
    area_html = '''
        <!-- 图片分析结果区域 -->
        <div class="image-analysis-area" id="imageAnalysisArea" style="display:none; margin-top:1.5rem;">
            <div style="background:linear-gradient(135deg,rgba(255,215,0,0.08),rgba(255,215,0,0.02));border:1px solid rgba(255,215,0,0.15);border-radius:12px;padding:1.5rem;">
                <h3 style="color:#ffd700;margin-bottom:1rem;">📷 图片分析结果</h3>
                <div id="imageAnalysisResult" style="color:rgba(255,255,255,0.85);line-height:1.8;font-size:0.9rem;white-space:pre-wrap;"></div>
                <button type="button" onclick="document.getElementById('imageAnalysisArea').style.display='none';" style="margin-top:1rem;background:rgba(255,215,0,0.2);color:#ffd700;border:1px solid rgba(255,215,0,0.3);border-radius:8px;padding:0.5rem 1rem;cursor:pointer;">关闭</button>
            </div>
        </div>
'''
    hd = re.sub(r'(\s*</div>\s*</body>)', area_html + r'\1', hd, count=1)
    print('  ✓ huangdao.html: 添加了 imageAnalysisArea')

# 补充 showEventDetail 完整内容
old_event = r'''switch(eventType) {
                case 'marriage':
                    content = '<div class="section"><h2>💒 结婚嫁娶择日要点</h2><h3>✅ 首选吉日</h3><ul><li>天德、月德、天喜、天赦、不将日</li><li>成日、开日、天愿、民日</li></ul><h3>⚔️ 避忌</h3><ul><li>破日、闭日、月破、四离四绝日</li><li>忌冲新娘生肖</li></ul><h3>📋 其他要点</h3><ul><li>选女方行嫁大利月和小利月</li><li>避开三娘煞、杨公忌等凶日</li></ul></div>';
                    break;
                case 'move':
                    content = '<div class="section"><h2>🏠 搬家入宅择日要点</h2><h3>✅ 首选吉日</h3><ul><li>天马、成日、开日、天德合、月德合</li><li>宜有天财、天仓</li></ul><h3>⚔️ 避忌</h3><ul><li>月破、平日、收日、闭日</li><li>忌冲家主生肖</li></ul><h3>📋 其他要点</h3><ul><li>宜选与宅主命卦相合之日</li><li>入住时宜燃放鞭炮（如允许）辟邪</li></ul></div>';
                    break;
                case 'business':
                    content = '<div class="section"><h2>🏪 开业开市择日要点</h2><h3>✅ 首选吉日</h3><ul><li>满日、成日、开日、天愿、民日</li><li>宜有天财、天仓</li></ul><h3>⚔️ 避忌</h3><ul><li>破日、闭日、四废日</li><li>忌冲店主生肖</li></ul><h3>📋 其他要点</h3><ul><li>开业时间宜在上午（阳气足）</li><li>可请舞狮队助兴（如允许）</li></ul></div>';
                    break;
                case 'construction':
                    content = '<div class="section"><h2>🏗 动土修造择日要点</h2><h3>✅ 首选吉日</h3><ul><li>成日、开日、天德、月德</li><li>宜有天德合、月德合</li></ul><h3>⚔️ 避忌</h3><ul><li>月建、土府、地囊、土符日</li><li>忌冲宅主生肖和坐山方向</li></ul><h3>📋 其他要点</h3><ul><li>动土前宜祭拜土地公</li><li>坐向要符合风水原则</li></ul></div>';
                    break;
            }'''

new_event = r'''switch(eventType) {
                case 'marriage':
                    content = `<div class="section">
                        <h2>💒 结婚嫁娶择日详解</h2>
                        <h3>✅ 首选吉日（按优先级排序）</</h3>
                        <table class="result-table">
                            <tr><th>吉日类型</th><th>具体名称</th><th>寓意</th></tr>
                            <tr><td>天德/月德日</td><td>天德、月德、天德合、月德合</td><td class="lucky">大吉（百无禁忌）</td></tr>
                            <tr><td>三合/六合日</td><td>与新郎新娘生肖三合或六合之日</td><td class="lucky">吉（婚姻和谐长久）</td></tr>
                            <tr><td>成日/开日</td><td>建星中的成日、开日</td><td class="lucky">吉（事成开放）</td></tr>
                            <tr><td>天喜/天赦日</td><td>天喜（主喜事）、天赦（主化解）</td><td class="lucky">大吉</td></tr>
                        </table>
                        <h3>⚔️ 严格避忌</h3>
                        <table class="result-table">
                            <tr><th>凶日类型</th><th>具体名称</th><th>后果</th></tr>
                            <tr><td>破日/闭日</td><td>建星中的破日、闭日</td><td class="unlucky">凶（破散闭塞）</td></tr>
                            <tr><td>四离/四绝日</td><td>春分、秋分、夏至、冬至前一日</td><td class="unlucky">凶（气场分离）</td></tr>
                            <tr><td>三娘煞/杨公忌</td><td>每月初三、初七、十三、十八、廿二、廿七</td><td class="unlucky">凶（传说月老不牵线）</td></tr>
                            <tr><td>冲生肖</td><td>日子地支冲新郎或新娘生肖</td><td class="unlucky">凶（主婚后不和）</td></tr>
                        </table>
                        <h3>📋 其他要点</h3>
                        <ul>
                            <li><strong>选女方大利月：</strong>首先看女方生肖所属的大利月（如鼠/马年妇利正/七月）</li>
                            <li><strong>避开三娘煞：</strong>每月初三、初七、十三、十八、廿二、廿七不宜嫁娶</li>
                            <li><strong>择吉时：</strong>不但要择吉日，还要择吉时（通常选上午9-11点）</li>
                        </ul>
                    </div>`;
                    break;
                case 'move':
                    content = `<div class="section">
                        <h2>🏠 搬家入宅择日详解</h2>
                        <h3>✅ 首选吉日</h3>
                        <table class="result-table">
                            <tr><th>吉日类型</th><th>具体名称</th><th>寓意</th></tr>
                            <tr><td>天马/成日</td><td>天马（主快运）、建星成日</td><td class="lucky">吉（搬家顺利快速安顿）</td></tr>
                            <tr><td>开日/天德合</td><td>建星开日、天德合、月德合</td><td class="lucky">大吉（开放纳福）</td></tr>
                            <tr><td>天财/天仓</td><td>天财（主财运）、天仓（主粮仓富足）</td><td class="lucky">吉（搬家后财运亨通）</td></tr>
                        </table>
                        <h3>⚔️ 严格避忌</h3>
                        <table class="result-table">
                            <tr><th>凶日类型</th><th>具体名称</th><th>后果</th></tr>
                            <tr><td>月破/平日</td><td>建星中的月破、平日、收日、闭日</td><td class="unlucky">凶（破散平滞收纳闭塞）</td></tr>
                            <tr><td>冲家主生肖</td><td>日子地支冲家中经济支柱生肖</td><td class="unlucky">凶（主家运不宁）</td></tr>
                            <tr><td>五墓/重丧日</td><td>特定方位对应的凶日</td><td class="unlucky">凶（主伤病死丧）</td></tr>
                        </table>
                        <h3>📋 其他要点</h3>
                        <ul>
                            <li><strong>与宅主命卦相合：</strong>选日子宜配合宅主八字喜用神</li>
                            <li><strong>入住仪式：</strong>入住时宜全屋开灯3天、烧开水（滚财）、放绿植（生气）</li>
                            <li><strong>入宅时间：</strong>宜在白天（上午9-15点前）完成入住</li>
                        </ul>
                    </div>`;
                    break;
                case 'business':
                    content = `<div class="section">
                        <h2>🏪 开业开市择日详解</h2>
                        <h3>✅ 首选吉日</h3>
                        <table class="result-table">
                            <tr><th>吉日类型</th><th>具体名称</th><th>寓意</th></tr>
                            <tr><td>满日/成日</td><td>建星满日（主圆满）、成日（主事成）</td><td class="lucky">大吉（开业圆满成功）</td></tr>
                            <tr><td>开日/天愿</td><td>建星开日（主开放）、天愿日（主天意顺遂）</td><td class="lucky">吉（客源广开）</td></tr>
                            <tr><td>天财/天仓</td><td>天财（主财运）、天仓（主货仓富足）</td><td class="lucky">吉（开业财源滚滚）</td></tr>
                        </table>
                        <h3>⚔️ 严格避忌</h3>
                        <table class="result-table">
                            <tr><th>凶日类型</th><th>具体名称</th><th>后果</th></tr>
                            <tr><td>破日/闭日</td><td>建星破日（主破败）、闭日（主闭塞）</td><td class="unlucky">凶（开业破财闭门塞运）</td></tr>
                            <tr><td>四废日</td><td>春庚申辛酉、夏壬辰癸巳、秋甲寅乙卯、冬丙戌丁亥</td><td class="unlucky">凶（主四季废歇无成）</td></tr>
                            <tr><td>冲店主生肖</td><td>日子地支冲店主生肖</td><td class="unlucky">凶（主开业后经营不顺）</td></tr>
                        </table>
                        <h3>📋 其他要点</h3>
                        <ul>
                            <li><strong>开业时间：</strong>宜在上午（9-11点阳气最足时）举行开业仪式</li>
                            <li><strong>请舞狮队：</strong>如条件允许，请舞狮队助兴（狮为瑞兽，主挡煞招财）</li>
                            <li><strong>择吉时：</strong>开业不但要择吉日，还要择吉时（通常选上午9-11点）</li>
                        </ul>
                    </div>`;
                    break;
                case 'construction':
                    content = `<div class="section">
                        <h2>🏗 动土修造择日详解</h2>
                        <h3>✅ 首选吉日</h3>
                        <table class="result-table">
                            <tr><th>吉日类型</th><th>具体名称</th><th>寓意</th></tr>
                            <tr><td>成日/开日</td><td>建星成日（主事成）、开日（主开放）</td><td class="lucky">吉（动土顺利建成圆满）</td></tr>
                            <tr><td>天德/月德</td><td>天德（主天庇佑）、月德（主月华庇佑）</td><td class="lucky">大吉（百无禁忌动土平安）</td></tr>
                            <tr><td>天德合/月德合</td><td>天德合、月德合（与主德合）</td><td class="lucky">吉（主贵人相助顺利应通过）</td></tr>
                        </table>
                        <h3>⚔️ 严格避忌</h3>
                        <table class="result-table">
                            <tr><th>凶日类型</th><th>具体名称</th><th>后果</th></tr>
                            <tr><td>月建/土府</td><td>建星月建（主月令当权）、土府（主土神发怒）</td><td class="unlucky">凶（动土犯煞主伤亡）</td></tr>
                            <tr><td>地囊/土符</td><td>地囊（地主凶煞）、土符（土神符令）</td><td class="unlucky">凶（主动土后家人生病）</td></tr>
                            <tr><td>冲宅主/坐山</td><td>日子地支冲宅主生肖或房屋坐山方向</td><td class="unlucky">凶（主房主健康受损）</td></tr>
                        </table>
                        <h3>📋 其他要点</h3>
                        <ul>
                            <li><strong>动土前祭拜：</strong>宜祭拜土地公（用三牲、水果、香烛）</li>
                            <li><strong>坐向符合风水：</strong>房屋的坐向要符合风水原则（如坐北向南为坎宅，宜选水/火日动土）</li>
                            <li><strong>动土时间：</strong>宜在上午（阳气足时）动第一铲土，并由宅主先动</li>
                        </ul>
                    </div>`;
                    break;
            }'''

if old_event in hd:
    hd = hd.replace(old_event, new_event)
    print('  ✓ huangdao.html: 补充了 showEventDetail 完整内容')
else:
    print('  ✗ huangdao.html: 未找到旧 showEventDetail 内容，尝试模糊匹配...')
    # 尝试用正则替换
    pattern = r'switch\(eventType\)\s*\{[^}]*case \'marriage\'[^}]*case \'move\'[^}]*case \'business\'[^}]*case \'construction\'[^}]*\}'
    if re.search(pattern, hd):
        hd = re.sub(pattern, new_event, hd)
        print('  ✓ huangdao.html: 通过正则匹配补充了 showEventDetail')
    else:
        print('  ✗ huangdao.html: 无法自动补充 showEventDetail，请手动处理')

with open('modules/huangdao.html', 'w', encoding='utf-8') as f:
    f.write(hd)
print('✓ huangdao.html 修复完成')

print('\n✅ 两个文件修复完成！')
