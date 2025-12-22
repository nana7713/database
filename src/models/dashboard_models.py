from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Date, DECIMAL, Text, CheckConstraint
from datetime import datetime
from base import db_manager


class DashboardConfig(db_manager.Base):
    """大屏展示配置表模型"""
    __tablename__ = 'dashboard_config'

    config_id = Column(BigInteger, primary_key=True, comment='配置编号')
    display_module = Column(String(50), nullable=False, comment='展示模块')
    refresh_frequency = Column(Integer, nullable=False, comment='数据刷新频率(秒)')
    display_fields = Column(Text, nullable=False, comment='展示字段')
    sorting_rule = Column(String(50), comment='排序规则')
    permission_level = Column(String(20), nullable=False, comment='权限等级')

    __table_args__ = (
        CheckConstraint(
            "display_module IN ('能源总览', '光伏总览', '配电网运行状态', '告警统计')",
            name='chk_display_module'
        ),
        CheckConstraint(
            "sorting_rule IN ('按时间降序', '按能耗降序')",
            name='chk_sorting_rule'
        ),
        CheckConstraint(
            "permission_level IN ('管理员', '能源管理员', '运维人员')",
            name='chk_permission_level'
        ),
        {'comment': '大屏展示配置表'}
    )


class RealtimeSummaryData(db_manager.Base):
    """实时汇总数据表模型"""
    __tablename__ = 'realtime_summary_data'

    summary_id = Column(BigInteger, primary_key=True, comment='汇总编号')
    statistics_time = Column(DateTime, nullable=False, unique=True, comment='统计时间')
    total_electricity = Column(DECIMAL(15, 2), comment='总用电量(kWh)')
    total_water = Column(DECIMAL(15, 2), comment='总用水量(m³)')
    total_steam = Column(DECIMAL(15, 2), comment='总蒸汽消耗量(t)')
    total_gas = Column(DECIMAL(15, 2), comment='总天然气消耗量(m³)')
    pv_total_generation = Column(DECIMAL(15, 2), comment='光伏总发电量(kWh)')
    pv_self_use = Column(DECIMAL(15, 2), comment='光伏自用电量(kWh)')
    total_alarms = Column(Integer, comment='总告警次数')
    high_level_alarms = Column(Integer, comment='高等级告警数')
    medium_level_alarms = Column(Integer, comment='中等级告警数')
    low_level_alarms = Column(Integer, comment='低等级告警数')

    __table_args__ = {'comment': '实时汇总数据表'}


class HistoricalTrendData(db_manager.Base):
    """历史趋势数据表模型"""
    __tablename__ = 'historical_trend_data'

    trend_id = Column(BigInteger, primary_key=True, comment='趋势编号')
    energy_type = Column(String(10), nullable=False, comment='能源类型')
    statistical_cycle = Column(String(4), nullable=False, comment='统计周期')
    statistical_date = Column(Date, nullable=False, comment='统计时间')
    energy_value = Column(DECIMAL(15, 2), nullable=False, comment='能耗/发电量数值')
    yoy_growth_rate = Column(DECIMAL(5, 2), comment='同比增长率(%)')
    mom_growth_rate = Column(DECIMAL(5, 2), comment='环比增长率(%)')
    industry_average = Column(DECIMAL(15, 2), comment='行业均值')

    __table_args__ = (
        CheckConstraint(
            "energy_type IN ('电', '水', '蒸汽', '天然气', '光伏')",
            name='chk_energy_type'
        ),
        CheckConstraint(
            "statistical_cycle IN ('日', '周', '月')",
            name='chk_statistical_cycle'
        ),
        {'comment': '历史趋势数据表'}
    )
