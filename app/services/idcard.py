"""
身份证号解析与校验
18位身份证：AAAAAA YYYYMMDD XXX C
- 前6位  = 地区码
- 7-14位 = 出生日期
- 第17位 = 性别（奇数男，偶数女）
- 第18位 = 校验位
"""
from datetime import datetime

# 校验权重
_WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
_CHECK_CODES = '10X98765432'

# 省级地区码 → 省市名称（覆盖31个省级行政区）
_REGION_MAP = {
    '11': '北京市', '12': '天津市', '13': '河北省', '14': '山西省',
    '15': '内蒙古自治区', '21': '辽宁省', '22': '吉林省', '23': '黑龙江省',
    '31': '上海市', '32': '江苏省', '33': '浙江省', '34': '安徽省',
    '35': '福建省', '36': '江西省', '37': '山东省', '41': '河南省',
    '42': '湖北省', '43': '湖南省', '44': '广东省',
    '45': '广西壮族自治区', '46': '海南省',
    '50': '重庆市', '51': '四川省', '52': '贵州省', '53': '云南省',
    '54': '西藏自治区', '61': '陕西省', '62': '甘肃省', '63': '青海省',
    '64': '宁夏回族自治区', '65': '新疆维吾尔自治区',
    '71': '台湾省', '81': '香港特别行政区', '82': '澳门特别行政区',
}


def validate_id_card(id_number):
    """
    校验18位身份证号

    返回: {
        'valid': bool,
        'birth_date': 'YYYY-MM-DD' or None,
        'gender': 'male'/'female' or None,
        'region_code': '110000' or None,
        'region_name': '北京市' or None,
        'age': int or None,
        'error': str or None
    }
    """
    result = {
        'valid': False, 'birth_date': None, 'gender': None,
        'region_code': None, 'region_name': None, 'age': None, 'error': None
    }

    if not id_number or not isinstance(id_number, str):
        result['error'] = '身份证号不能为空'
        return result

    num = id_number.strip().upper()
    if len(num) != 18:
        result['error'] = '身份证号应为18位'
        return result
    if not num[:17].isdigit():
        result['error'] = '身份证号前17位必须为数字'
        return result

    # 1. 校验位验证
    total = sum(int(num[i]) * _WEIGHTS[i] for i in range(17))
    expected = _CHECK_CODES[total % 11]
    if num[17] != expected:
        result['error'] = '身份证号校验位不正确'
        return result

    # 2. 解析出生日期
    try:
        birth = datetime.strptime(num[6:14], '%Y%m%d')
        # 日期合法性：不能晚于今天，不能早于1900年
        now = datetime.now()
        if birth > now:
            result['error'] = '出生日期不能晚于今天'
            return result
        if birth.year < 1900:
            result['error'] = '出生日期不合法'
            return result
        result['birth_date'] = birth.strftime('%Y-%m-%d')
        result['age'] = now.year - birth.year - (
            (now.month, now.day) < (birth.month, birth.day))
    except ValueError:
        result['error'] = '出生日期不合法'
        return result

    # 3. 解析性别（第17位）
    ordinal = int(num[16])
    result['gender'] = 'male' if ordinal % 2 == 1 else 'female'

    # 4. 解析地区
    province_code = num[:2] + '0000'
    city_code = num[:4] + '00'
    result['region_code'] = num[:6]
    result['region_name'] = _REGION_MAP.get(num[:2], '未知地区')

    result['valid'] = True
    return result


def get_region_name(province_code):
    """根据前2位省份代码获取省份名称"""
    return _REGION_MAP.get(province_code, '未知地区')


def mask_name(name):
    """脱敏姓名：张三 → 张*，欧阳锋 → 欧*锋"""
    if not name or len(name) < 2:
        return name or '*'
    if len(name) == 2:
        return name[0] + '*'
    return name[0] + '*' + name[-1]


def mask_id_last4(id_number):
    """只暴露身份证后4位，其余替换为*"""
    if not id_number or len(id_number) < 4:
        return '****'
    return '*' * (len(id_number) - 4) + id_number[-4:]
