"""数据集路由：自定义数据集与分类管理"""

from datetime import datetime

from flask import Blueprint, jsonify, request

import fcntl
import json
import os
import random
import string


from app.api.deps import _get_auth_user, load_users, save_users
from config import DATA_DIR, DATASETS_FILE, DIVINATION_FILE

bp = Blueprint('datasets', __name__)

@bp.route('/api/datasets', methods=['GET'])
def get_datasets():
    """获取数据集列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(DATASETS_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                datasets_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        user_datasets = datasets_data.get(user['id'], [])
        # 返回摘要（不含 records 详情，减少传输量）
        summaries = []
        for ds in user_datasets:
            summaries.append({
                'id': ds['id'],
                'name': ds['name'],
                'description': ds.get('description', ''),
                'fields': ds.get('fields', []),
                'record_count': len(ds.get('records', [])),
                'created_at': ds.get('created_at', ''),
                'updated_at': ds.get('updated_at', '')
            })

        summaries.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return jsonify({'success': True, 'datasets': summaries}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/datasets', methods=['POST'])
def create_dataset():
    """创建数据集"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        name = (data.get('name', '') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': '请输入数据集名称'}), 400

        description = data.get('description', '')
        fields = data.get('fields', [])
        # 验证字段定义
        valid_types = {'text', 'number', 'date', 'select'}
        for fld in fields:
            if not fld.get('name'):
                return jsonify({'success': False, 'message': '字段名不能为空'}), 400
            if fld.get('type', 'text') not in valid_types:
                return jsonify({'success': False, 'message': f'不支持的字段类型: {fld.get("type")}'}), 400

        now = datetime.now().isoformat()
        dataset = {
            'id': 'ds_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            'name': name,
            'description': description,
            'fields': fields,
            'records': [],
            'created_at': now,
            'updated_at': now
        }

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)
                if user['id'] not in datasets_data:
                    datasets_data[user['id']] = []
                datasets_data[user['id']].append(dataset)
                f.seek(0)
                f.truncate()
                json.dump(datasets_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '数据集创建成功', 'dataset': {
            'id': dataset['id'], 'name': name, 'description': description,
            'fields': fields, 'record_count': 0, 'created_at': now, 'updated_at': now
        }}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/datasets/<dataset_id>', methods=['PUT'])
def update_dataset(dataset_id):
    """更新数据集（名称、描述、字段）"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                user_datasets = datasets_data.get(user['id'], [])
                found = False
                for ds in user_datasets:
                    if ds['id'] == dataset_id:
                        if 'name' in data:
                            ds['name'] = data['name'].strip()
                        if 'description' in data:
                            ds['description'] = data['description']
                        if 'fields' in data:
                            ds['fields'] = data['fields']
                        ds['updated_at'] = datetime.now().isoformat()
                        found = True
                        break

                if not found:
                    return jsonify({'success': False, 'message': '数据集不存在'}), 404

                f.seek(0)
                f.truncate()
                json.dump(datasets_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '更新成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """删除数据集"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                if user['id'] in datasets_data:
                    datasets_data[user['id']] = [
                        d for d in datasets_data[user['id']] if d['id'] != dataset_id
                    ]

                f.seek(0)
                f.truncate()
                json.dump(datasets_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/datasets/<dataset_id>/records', methods=['GET'])
def get_dataset_records(dataset_id):
    """获取数据集记录列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        with open(DATASETS_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                datasets_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        for ds in datasets_data.get(user['id'], []):
            if ds['id'] == dataset_id:
                records = ds.get('records', [])
                total = len(records)
                start = (page - 1) * per_page
                end = start + per_page
                return jsonify({
                    'success': True,
                    'dataset': {'id': ds['id'], 'name': ds['name'], 'fields': ds.get('fields', [])},
                    'records': records[start:end],
                    'total': total,
                    'page': page,
                    'per_page': per_page
                }), 200

        return jsonify({'success': False, 'message': '数据集不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/datasets/<dataset_id>/records', methods=['POST'])
def add_dataset_record(dataset_id):
    """添加记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        record_data = data.get('data', {})

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                for ds in datasets_data.get(user['id'], []):
                    if ds['id'] == dataset_id:
                        record = {
                            'id': 'rec_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                            'data': record_data,
                            'created_at': datetime.now().isoformat()
                        }
                        ds.setdefault('records', []).append(record)
                        ds['updated_at'] = datetime.now().isoformat()

                        f.seek(0)
                        f.truncate()
                        json.dump(datasets_data, f, ensure_ascii=False, indent=2)
                        return jsonify({'success': True, 'message': '记录添加成功', 'record': record}), 200

                return jsonify({'success': False, 'message': '数据集不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/datasets/<dataset_id>/records/<record_id>', methods=['PUT'])
def update_dataset_record(dataset_id, record_id):
    """更新记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        record_data = data.get('data', {})

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                for ds in datasets_data.get(user['id'], []):
                    if ds['id'] == dataset_id:
                        for rec in ds.get('records', []):
                            if rec['id'] == record_id:
                                rec['data'] = record_data
                                ds['updated_at'] = datetime.now().isoformat()
                                f.seek(0)
                                f.truncate()
                                json.dump(datasets_data, f, ensure_ascii=False, indent=2)
                                return jsonify({'success': True, 'message': '记录更新成功'}), 200
                        return jsonify({'success': False, 'message': '记录不存在'}), 404

                return jsonify({'success': False, 'message': '数据集不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/datasets/<dataset_id>/records/<record_id>', methods=['DELETE'])
def delete_dataset_record(dataset_id, record_id):
    """删除记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                for ds in datasets_data.get(user['id'], []):
                    if ds['id'] == dataset_id:
                        ds['records'] = [r for r in ds.get('records', []) if r['id'] != record_id]
                        ds['updated_at'] = datetime.now().isoformat()
                        f.seek(0)
                        f.truncate()
                        json.dump(datasets_data, f, ensure_ascii=False, indent=2)
                        return jsonify({'success': True, 'message': '记录删除成功'}), 200

                return jsonify({'success': False, 'message': '数据集不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 分类管理 ==========
CATEGORIES_FILE = os.path.join(DATA_DIR, 'categories.json')

if not os.path.exists(CATEGORIES_FILE):
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


@bp.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                categories_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        user_categories = categories_data.get(user['id'], [])
        user_categories.sort(key=lambda x: x.get('created_at', ''))

        return jsonify({'success': True, 'categories': user_categories}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/categories', methods=['POST'])
def create_category():
    """创建分类"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        name = (data.get('name', '') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': '请输入分类名称'}), 400

        color = data.get('color', '#ffd700')
        icon = data.get('icon', '📋')

        category = {
            'id': 'cat_' + ''.join(random.choices(string.ascii_letters + string.digits, k=12)),
            'name': name,
            'color': color,
            'icon': icon,
            'created_at': datetime.now().isoformat()
        }

        with open(CATEGORIES_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                categories_data = json.load(f)
                if user['id'] not in categories_data:
                    categories_data[user['id']] = []
                categories_data[user['id']].append(category)
                f.seek(0)
                f.truncate()
                json.dump(categories_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '分类创建成功', 'category': category}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """更新分类"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()

        with open(CATEGORIES_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                categories_data = json.load(f)

                for cat in categories_data.get(user['id'], []):
                    if cat['id'] == category_id:
                        if 'name' in data:
                            cat['name'] = data['name'].strip()
                        if 'color' in data:
                            cat['color'] = data['color']
                        if 'icon' in data:
                            cat['icon'] = data['icon']
                        f.seek(0)
                        f.truncate()
                        json.dump(categories_data, f, ensure_ascii=False, indent=2)
                        return jsonify({'success': True, 'message': '分类更新成功'}), 200

                return jsonify({'success': False, 'message': '分类不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除分类（同时清除历史记录中对该分类的引用）"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(CATEGORIES_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                categories_data = json.load(f)

                if user['id'] in categories_data:
                    categories_data[user['id']] = [
                        c for c in categories_data[user['id']] if c['id'] != category_id
                    ]

                f.seek(0)
                f.truncate()
                json.dump(categories_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        # 清除历史记录中的分类引用
        with open(DIVINATION_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                histories = json.load(f)
                if user['id'] in histories:
                    for h in histories[user['id']]:
                        if h.get('category_id') == category_id:
                            h['category_id'] = ''
                f.seek(0)
                f.truncate()
                json.dump(histories, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '分类删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

