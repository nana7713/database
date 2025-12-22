# app.py 
from flask import Flask, jsonify
from datetime import datetime
import base  # 在文件顶部导入base

def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    
    # 导入模型
    from models.user import User
    from models.role import Role, UserRole
    from models.plant_area import PlantArea
    from models.alarm_models import Device, Alarm, MaintenanceOrder
    from models.dashboard_models import DashboardConfig, RealtimeSummaryData, HistoricalTrendData
    from models.energy_models import EnergyMeteringEquipment, EnergyMonitoringData, PeakValleyEnergyData
    
    try:
        # 创建表
        base.db_manager.Base.metadata.create_all(bind=base.db_manager.engine)
        print("✓ 数据库表创建成功")
        
        # 初始化角色
        init_roles()
        
    except Exception as e:
        print(f"✗ 数据库初始化失败: {str(e)}")

def init_roles():
    """初始化角色"""
    from models.role import Role
    
    with base.db_manager.get_session() as session:
        if session.query(Role).count() == 0:
            print("添加角色数据...")
            
            roles = [
                Role(role_id=1, role_code='ADMIN', role_name='系统管理员', description='拥有所有权限'),
                Role(role_id=2, role_code='ENERGY_MANAGER', role_name='能源管理员', description='能源管理相关权限'),
                Role(role_id=3, role_code='MAINTENANCE', role_name='运维人员', description='设备运维相关权限'),
                Role(role_id=4, role_code='DATA_ANALYST', role_name='数据分析师', description='数据分析相关权限'),
                Role(role_id=5, role_code='MANAGER', role_name='企业管理层', description='查看报表和决策'),
                Role(role_id=6, role_code='WORK_ORDER_ADMIN', role_name='运维工单管理员', description='工单管理权限'),
                Role(role_id=7, role_code='USER', role_name='普通用户', description='基础查看权限')
            ]
            
            session.add_all(roles)
            session.commit()
            print(f"✓ 添加了 {len(roles)} 个角色")

def create_app():
    """创建Flask应用"""
    app = Flask(__name__, static_folder='frontend', static_url_path='/')
    
    app.config['SECRET_KEY'] = '智慧能源管理系统密钥-2025'
    app.config['JSON_AS_ASCII'] = False
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    @app.route('/test')
    def test():
        # 添加导入
        from sqlalchemy import text
        
        with base.db_manager.get_session() as session:
            # 使用 text() 包装
            result = session.execute(text('SELECT 1')).scalar()
            return jsonify({'success': True, 'data': result})
        
    # 注册路由
    try:
        from routes.auth_routes import auth_bp
        from routes.substation_routes import substation_bp
        from routes.alarm_routes import alarm_bp
        from routes.dashboard_routes import dashboard_bp
        from routes.energy_routes import energy_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(substation_bp)
        app.register_blueprint(alarm_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(energy_bp)
        
        print("✓ 所有路由注册成功")
    except Exception as e:
        print(f"⚠ 路由导入失败: {str(e)}")
    
    return app

if __name__ == '__main__':
    print("=" * 50)
    print("智慧能源管理系统 API")
    print("=" * 50)
    
    # 1. 初始化数据库
    init_database()
    
    # 2. 创建并运行应用
    app = create_app()
    
    print(f"\n服务已启动: http://localhost:5000")
    print("可用接口:")
    print("  GET  /           - 首页")
    print("  GET  /health     - 健康检查")
    print("  GET  /test       - 数据库测试")
    print("  POST /api/auth/register - 用户注册")
    print("  POST /api/auth/login    - 用户登录")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)