"""
管理端分析 API（/api/admin/analytics/*）。

安全变更：原版完全无鉴权，任何访客均可读取全部运营数据；
现要求请求头 X-Admin-Token（环境变量 ADMIN_TOKEN）校验，
未配置 ADMIN_TOKEN 时接口整体禁用（返回 503），避免裸奔上线。
"""
import os

from flask import Blueprint, jsonify, request

from app.services.analytics_db import (
    aggregate_hourly, get_daily_stats, get_hourly_stats, get_module_stats,
    get_overview, get_page_stats, get_region_stats, get_user_profile_stats,
    get_vip_stats,
)

analytics_bp = Blueprint('analytics', __name__)

def _check_admin():
    """校验管理端令牌。"""
    expected = os.environ.get('ADMIN_TOKEN', '')
    if not expected:
        return False, (jsonify({'success': False, 'message': '管理端未配置令牌，接口已禁用'}), 503)
    provided = request.headers.get('X-Admin-Token', '')
    if provided != expected:
        return False, (jsonify({'success': False, 'message': '无效的管理令牌'}), 401)
    return True, None

@analytics_bp.before_request
def _require_admin():
    ok, err = _check_admin()
    if not ok:
        return err

@analytics_bp.route('/overview')
def overview():
    """数据总览"""
    try:
        data = get_overview()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/modules')
def module_stats():
    """模块统计"""
    try:
        data = get_module_stats()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/daily')
def daily_stats():
    """每日统计"""
    try:
        days = request.args.get('days', 30, type=int)
        data = get_daily_stats(days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/hours')
def hourly_stats():
    """每小时统计"""
    try:
        data = get_hourly_stats()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/users')
def user_profile_stats():
    """用户画像统计"""
    try:
        data = get_user_profile_stats()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/vip')
def vip_stats():
    """VIP 统计"""
    try:
        data = get_vip_stats()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/pages')
def page_stats():
    """页面统计"""
    try:
        data = get_page_stats()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/regions')
def region_stats():
    """地区分布"""
    try:
        data = get_region_stats()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/aggregate', methods=['POST'])
def aggregate():
    """手动触发小时聚合"""
    try:
        aggregate_hourly()
        return jsonify({'success': True, 'message': '聚合完成'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
