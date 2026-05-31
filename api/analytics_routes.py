"""
数据分析 API 路由
"""
from flask import Blueprint, request, jsonify
from .analytics_db import (
    get_overview, get_module_stats, get_daily_stats,
    get_hourly_stats, get_user_profile_stats, aggregate_hourly,
    get_vip_stats, get_page_stats
)

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/overview')
def overview():
    """数据总览"""
    try:
        data = get_overview()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/modules')
def modules():
    """模块排行"""
    try:
        days = request.args.get('days', 30, type=int)
        data = get_module_stats(days=days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/daily')
def daily():
    """按天统计"""
    try:
        days = request.args.get('days', 30, type=int)
        data = get_daily_stats(days=days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/hours')
def hours():
    """按小时分布"""
    try:
        days = request.args.get('days', 7, type=int)
        data = get_hourly_stats(days=days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/users')
def users():
    """用户画像"""
    try:
        data = get_user_profile_stats()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/aggregate')
def aggregate():
    """手动触发小时聚合"""
    aggregate_hourly()
    return jsonify({'success': True, 'message': '聚合完成'})


@analytics_bp.route('/vip')
def vip_stats():
    """VIP 行为统计"""
    try:
        days = request.args.get('days', 30, type=int)
        data = get_vip_stats(days=days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@analytics_bp.route('/pages')
def page_stats():
    """页面访问排行"""
    try:
        days = request.args.get('days', 7, type=int)
        data = get_page_stats(days=days)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
