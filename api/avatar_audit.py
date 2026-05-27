"""
头像自动审核模块
基于全网头像审核规则：
1. 禁止内容：色情、暴力、政治敏感、血腥、广告
2. 图片要求：JPG/PNG，<2MB，100-300像素
3. 审核标准：三级分类（Pass/Review/Block）
4. 自动审核：基于PIL图片分析 + 规则判断
"""

from PIL import Image
import io
import base64
from collections import Counter
import os

# 审核结果常量
AUDIT_PASS = 'pass'      # 通过
AUDIT_REVIEW = 'review'   # 需人工复审
AUDIT_BLOCK = 'block'     # 拒绝

class AvatarAuditor:
    """头像自动审核类"""
    
    # 配置文件大小和格式限制
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    ALLOWED_FORMATS = ['JPEG', 'PNG', 'GIF']
    MIN_DIMENSION = 50   # 最小尺寸
    MAX_DIMENSION = 1000  # 最大尺寸
    
    @staticmethod
    def audit_avatar(image_data, filename='avatar.jpg'):
        """
        自动审核头像
        :param image_data: base64编码的图片数据或二进制数据
        :param filename: 文件名（用于判断格式）
        :return: dict {'result': 'pass/review/block', 'reason': '原因'}
        """
        try:
            # 1. 解码图片
            if isinstance(image_data, str):
                # base64 字符串
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            # 2. 检查文件大小
            file_size = len(image_bytes)
            if file_size > AvatarAuditor.MAX_FILE_SIZE:
                return {
                    'result': AUDIT_BLOCK,
                    'reason': f'文件大小超过2MB（当前：{file_size/1024/1024:.2f}MB）'
                }
            
            # 3. 打开图片进行验证
            img = Image.open(io.BytesIO(image_bytes))
            
            # 4. 检查格式
            if img.format not in AvatarAuditor.ALLOWED_FORMATS:
                return {
                    'result': AUDIT_BLOCK,
                    'reason': f'不支持的图片格式（仅支持JPG/PNG/GIF，当前：{img.format}）'
                }
            
            # 5. 检查尺寸
            width, height = img.size
            if width < AvatarAuditor.MIN_DIMENSION or height < AvatarAuditor.MIN_DIMENSION:
                return {
                    'result': AUDIT_BLOCK,
                    'reason': f'图片尺寸过小（最小50x50像素，当前：{width}x{height}）'
                }
            
            if width > AvatarAuditor.MAX_DIMENSION or height > AvatarAuditor.MAX_DIMENSION:
                return {
                    'result': AUDIT_BLOCK,
                    'reason': f'图片尺寸过大（最大1000x1000像素，当前：{width}x{height}）'
                }
            
            # 6. 内容审核（基于图片特征分析）
            content_result = AvatarAuditor._audit_content(img)
            
            return content_result
            
        except Exception as e:
            return {
                'result': AUDIT_BLOCK,
                'reason': f'图片解析失败：{str(e)}'
            }
    
    @staticmethod
    def _audit_content(img):
        """
        审核图片内容
        基于颜色分布、特征分析进行违规检测
        """
        try:
            # 转换为RGB
            img_rgb = img.convert('RGB')
            width, height = img.size
            
            # 缩小图片以提高处理速度
            img_small = img_rgb.resize((100, 100))
            pixels = list(img_small.getdata())
            
            # 统计颜色分布
            r_avg = sum(p[0] for p in pixels) // len(pixels)
            g_avg = sum(p[1] for p in pixels) // len(pixels)
            b_avg = sum(p[2] for p in pixels) // len(pixels)
            
            # 计算皮肤色调比例（简单的人体肤色检测）
            skin_tone_count = 0
            for p in pixels:
                r, g, b = p
                # 简单肤色判断（RGB范围）
                if (r > 95 and g > 40 and b > 20 and 
                    r > g and r > b and 
                    abs(r - g) > 15):
                    skin_tone_count += 1
            
            skin_ratio = skin_tone_count / len(pixels)
            
            # 审核规则判断
            
            # 规则1：检测大量皮肤色调（可能涉黄）
            if skin_ratio > 0.6:
                return {
                    'result': AUDIT_REVIEW,
                    'reason': '检测到大量皮肤色调，建议人工复审'
                }
            
            # 规则2：检测血腥色调（红色占比过高）
            red_ratio = sum(1 for p in pixels if p[0] > 200 and p[1] < 100 and p[2] < 100) / len(pixels)
            if red_ratio > 0.5:
                return {
                    'result': AUDIT_REVIEW,
                    'reason': '检测到大量红色色调，可能为血腥内容'
                }
            
            # 规则3：检测纯黑/纯白图片（可能为违规内容）
            black_ratio = sum(1 for p in pixels if p[0] < 30 and p[1] < 30 and p[2] < 30) / len(pixels)
            white_ratio = sum(1 for p in pixels if p[0] > 225 and p[1] > 225 and p[2] > 225) / len(pixels)
            
            if black_ratio > 0.8 or white_ratio > 0.8:
                return {
                    'result': AUDIT_REVIEW,
                    'reason': '图片颜色过于单一，建议人工复审'
                }
            
            # 规则4：检测广告特征（大量纯色块）
            color_counts = Counter(pixels)
            most_common_ratio = color_counts.most_common(1)[0][1] / len(pixels)
            if most_common_ratio > 0.3:
                return {
                    'result': AUDIT_REVIEW,
                    'reason': '检测到大面积纯色块，可能包含广告或文字'
                }
            
            # 通过所有检测
            return {
                'result': AUDIT_PASS,
                'reason': '审核通过'
            }
            
        except Exception as e:
            return {
                'result': AUDIT_REVIEW,
                'reason': f'内容审核异常，建议人工复审：{str(e)}'
            }
    
    @staticmethod
    def resize_avatar(image_data, size=(200, 200)):
        """
        调整头像尺寸（标准化）
        :param image_data: 原始图片数据
        :param size: 目标尺寸
        :return: 调整后的图片二进制数据
        """
        try:
            if isinstance(image_data, str):
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            img = Image.open(io.BytesIO(image_bytes))
            img_resized = img.resize(size, Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            img_resized.save(output, format='JPEG', quality=85)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f'头像缩放失败：{str(e)}')


# 测试代码
if __name__ == '__main__':
    # 示例：创建一个测试图片
    test_img = Image.new('RGB', (200, 200), color=(255, 200, 150))
    import base64
    buffer = io.BytesIO()
    test_img.save(buffer, format='JPEG')
    test_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 审核测试
    result = AvatarAuditor.audit_avatar(f'data:image/jpeg;base64,{test_base64}')
    print(f"审核结果：{result['result']}")
    print(f"原因：{result['reason']}")
