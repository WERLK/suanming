#!/usr/bin/env python3
"""
ASCII-only fix for login.html. No Chinese chars in this script.
Patterns match by code structure, not by Chinese text.
"""
import re

FILE = '/root/suanming/login.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ---- Fix 1: loadImageCaptcha - add data.message display on !success ----
# Find: "catch (e) { Auth.showMsg('authMsg', '...', true);" right after the captchaImage line
pattern1 = re.compile(
    r"(async function loadImageCaptcha\(\) \{\s*"
    r"try \{\s*"
    r"var data = await Auth\.generateCaptcha\(\);.*?"
    r"captchaId = data\.captcha_id;.*?"
    r"\$\('captchaImage'\)\.innerHTML = '<img src=\"' \+ data\.captcha_image \+ '\" alt=\"[^\"]+\">';\s*"
    r"\}\s*"
    r"catch \(e\) \{)",
    re.DOTALL
)
match = pattern1.search(content)
if match:
    end_of_try = match.group(0).rfind('}')
    # Insert else block before the closing brace of try
    insert_at = match.start() + end_of_try
    repl = (
        "        } else {\n"
        "            Auth.showMsg('authMsg', data.message || 'Captcha load failed', true);\n"
        "        "
    )
    new_content = content[:insert_at] + repl + content[insert_at:]
    content = new_content
    changes += 1
    print('[OK] loadImageCaptcha - added error message for !success')

# ---- Fix 2: refreshSlider - add loading state ----
# Find the function body between "function refreshSlider()" and next "function"
pattern2 = re.compile(
    r"(function refreshSlider\(\) \{\s*)"
    r"(Auth\.generateSlider\(\)\.then\(function\(data\) \{)"
)
match2 = pattern2.search(content)
if match2 and '$(\'sliderHint\').textContent' not in match2.group(0)[:50]:
    # Add loading state before API call
    insert_pos = match2.start(2)
    content = content[:insert_pos] + "$('sliderHint').textContent = 'Loading...';\n        " + content[insert_pos:]
    changes += 1
    print('[OK] refreshSlider - added loading state')

# Also add catch handler with error display
old_catch = ".catch(function() {});"
new_catch = (
    ".catch(function() {\n"
    "            $('sliderHint').textContent = 'Network error, please refresh';\n"
    "            $('sliderHint').style.color = '#ff6b6b';\n"
    "        });"
)
if old_catch in content and 'Network error' not in content:
    content = content.replace(old_catch, new_catch, 1)
    changes += 1
    print('[OK] refreshSlider - added catch handler')

# ---- Fix 3: Slider submit - check sliderId before verify ----
pattern3 = re.compile(
    r"(} else if \(captchaType === 'slider'\) \{\s*)"
    r"(var pct = )"
)
match3 = pattern3.search(content)
if match3 and 'if (!sliderId)' not in content:
    check = (
        "if (!sliderId) {\n"
        "                Auth.showMsg('authMsg', 'Slider not loaded, please refresh', true);\n"
        "                refreshSlider();\n"
        "                return;\n"
        "            }\n                "
    )
    content = content[:match3.start(2)] + check + content[match3.start(2):]
    changes += 1
    print('[OK] slider verify - added sliderId empty check')

# ---- Fix 4: SMS code display - better fallback ----
pattern4 = re.compile(
    r"var msg = data\.code \? '[^']+' \+ data\.code \+ '[^']+' : '[^']+';",
    re.DOTALL
)
match4 = pattern4.search(content)
if match4:
    old_line = match4.group(0)
    new_line = (
        "var msg;\n"
        "            if (data.code && data.code !== null && data.code !== undefined) {\n"
        "                msg = 'Code: ' + data.code + ' (demo)';\n"
        "            } else if (data.message && data.message.indexOf('demo') >= 0) {\n"
        "                msg = data.message;\n"
        "            } else {\n"
        "                msg = data.message || 'SMS sent';\n"
        "            }"
    )
    content = content.replace(old_line, new_line, 1)
    changes += 1
    print('[OK] SMS code display - compatibility enhanced')

if changes == 0:
    print('[SKIP] login.html already patched or not found')
else:
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'[DONE] login.html fixed ({changes} changes)')
    print('Remember: Ctrl+F5 in browser to clear cache')
