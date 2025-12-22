from typing import List, Optional, Dict, Any
from sqlalchemy import desc, asc, and_, or_, func
from datetime import datetime, date, timedelta
from models.dashboard_models import DashboardConfig, RealtimeSummaryData, HistoricalTrendData
from base import db_manager


class DashboardConfigDAO:
    """大屏展示配置数据访问对象"""

    def insert_config(self, config_data: Dict[str, Any]) -> DashboardConfig:
        """新增大屏展示配置"""
        with db_manager.get_session() as session:
            config = DashboardConfig(**config_data)
            session.add(config)
            session.commit()
            return config

    def get_config_by_id(self, config_id: int) -> Optional[DashboardConfig]:
        """根据配置编号查询配置"""
        with db_manager.get_session() as session:
            return session.query(DashboardConfig).filter(
                DashboardConfig.config_id == config_id
            ).first()

    def get_configs_by_module(self, display_module: str) -> List[DashboardConfig]:
        """根据展示模块查询配置列表"""
        with db_manager.get_session() as session:
            return session.query(DashboardConfig).filter(
                DashboardConfig.display_module == display_module
            ).all()

    def get_configs_by_permission(self, permission_level: str) -> List[DashboardConfig]:
        """根据权限等级查询配置列表"""
        with db_manager.get_session() as session:
            return session.query(DashboardConfig).filter(
                DashboardConfig.permission_level == permission_level
            ).all()

    def update_config(self, config_id: int, update_data: Dict[str, Any]) -> Optional[DashboardConfig]:
        """更新大屏展示配置"""
        with db_manager.get_session() as session:
            config = session.query(DashboardConfig).filter(
                DashboardConfig.config_id == config_id
            ).first()
            if config:
                for key, value in update_data.items():
                    setattr(config, key, value)
                session.commit()
            return config

    def delete_config(self, config_id: int) -> bool:
        """删除大屏展示配置"""
        with db_manager.get_session() as session:
            config = session.query(DashboardConfig).filter(
                DashboardConfig.config_id == config_id
            ).first()
            if config:
                session.delete(config)
                session.commit()
                return True
            return False

    def get_all_configs(self) -> List[DashboardConfig]:
        """获取所有大屏展示配置"""
        with db_manager.get_session() as session:
            return session.query(DashboardConfig).all()


class RealtimeSummaryDAO:
    """实时汇总数据访问对象"""

    def insert_summary(self, summary_data: Dict[str, Any]) -> RealtimeSummaryData:
        """新增实时汇总数据"""
        with db_manager.get_session() as session:
            summary = RealtimeSummaryData(**summary_data)
            session.add(summary)
            session.commit()
            return summary

    def get_summary_by_id(self, summary_id: int) -> Optional[RealtimeSummaryData]:
        """根据汇总编号查询实时数据"""
        with db_manager.get_session() as session:
            return session.query(RealtimeSummaryData).filter(
                RealtimeSummaryData.summary_id == summary_id
            ).first()

    def get_latest_summary(self) -> Optional[RealtimeSummaryData]:
        """获取最新的实时汇总数据"""
        with db_manager.get_session() as session:
            return session.query(RealtimeSummaryData).order_by(
                desc(RealtimeSummaryData.statistics_time)
            ).first()

    def get_summary_by_time_range(self, start_time: datetime, end_time: datetime) -> List[RealtimeSummaryData]:
        """根据时间范围查询实时汇总数据"""
        with db_manager.get_session() as session:
            return session.query(RealtimeSummaryData).filter(
                and_(
                    RealtimeSummaryData.statistics_time >= start_time,
                    RealtimeSummaryData.statistics_time <= end_time
                )
            ).order_by(asc(RealtimeSummaryData.statistics_time)).all()

    def get_summary_by_date(self, target_date: date) -> List[RealtimeSummaryData]:
        """根据日期查询当天的实时汇总数据"""
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = datetime.combine(target_date, datetime.max.time())
        return self.get_summary_by_time_range(start_time, end_time)

    def update_summary(self, summary_id: int, update_data: Dict[str, Any]) -> Optional[RealtimeSummaryData]:
        """更新实时汇总数据"""
        with db_manager.get_session() as session:
            summary = session.query(RealtimeSummaryData).filter(
                RealtimeSummaryData.summary_id == summary_id
            ).first()
            if summary:
                for key, value in update_data.items():
                    setattr(summary, key, value)
                session.commit()
            return summary

    def delete_summary(self, summary_id: int) -> bool:
        """删除实时汇总数据"""
        with db_manager.get_session() as session:
            summary = session.query(RealtimeSummaryData).filter(
                RealtimeSummaryData.summary_id == summary_id
            ).first()
            if summary:
                session.delete(summary)
                session.commit()
                return True
            return False

    def get_alarm_statistics(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取告警统计信息（最近N天）"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        with db_manager.get_session() as session:
            result = session.query(
                func.date(RealtimeSummaryData.statistics_time).label('stat_date'),
                func.sum(RealtimeSummaryData.total_alarms).label('total_alarms'),
                func.sum(RealtimeSummaryData.high_level_alarms).label('high_alarms'),
                func.sum(RealtimeSummaryData.medium_level_alarms).label('medium_alarms'),
                func.sum(RealtimeSummaryData.low_level_alarms).label('low_alarms')
            ).filter(
                and_(
                    RealtimeSummaryData.statistics_time >= start_date,
                    RealtimeSummaryData.statistics_time <= end_date
                )
            ).group_by(func.date(RealtimeSummaryData.statistics_time)).all()

            return [{
                'stat_date': row.stat_date,
                'total_alarms': row.total_alarms or 0,
                'high_alarms': row.high_alarms or 0,
                'medium_alarms': row.medium_alarms or 0,
                'low_alarms': row.low_alarms or 0
            } for row in result]


class HistoricalTrendDAO:
    """历史趋势数据访问对象"""

    def insert_trend(self, trend_data: Dict[str, Any]) -> HistoricalTrendData:
        """新增历史趋势数据"""
        with db_manager.get_session() as session:
            trend = HistoricalTrendData(**trend_data)
            session.add(trend)
            session.commit()
            return trend

    def get_trend_by_id(self, trend_id: int) -> Optional[HistoricalTrendData]:
        """根据趋势编号查询历史趋势数据"""
        with db_manager.get_session() as session:
            return session.query(HistoricalTrendData).filter(
                HistoricalTrendData.trend_id == trend_id
            ).first()

    def get_trends_by_energy_type(self, energy_type: str, cycle: str = None) -> List[HistoricalTrendData]:
        """根据能源类型和统计周期查询历史趋势数据"""
        with db_manager.get_session() as session:
            query = session.query(HistoricalTrendData).filter(
                HistoricalTrendData.energy_type == energy_type
            )

            if cycle:
                query = query.filter(HistoricalTrendData.statistical_cycle == cycle)

            return query.order_by(desc(HistoricalTrendData.statistical_date)).all()

    def get_trends_by_date_range(self, energy_type: str, start_date: date, end_date: date,
                                 cycle: str = None) -> List[HistoricalTrendData]:
        """根据时间范围和能源类型查询历史趋势数据"""
        with db_manager.get_session() as session:
            query = session.query(HistoricalTrendData).filter(
                and_(
                    HistoricalTrendData.energy_type == energy_type,
                    HistoricalTrendData.statistical_date >= start_date,
                    HistoricalTrendData.statistical_date <= end_date
                )
            )

            if cycle:
                query = query.filter(HistoricalTrendData.statistical_cycle == cycle)

            return query.order_by(asc(HistoricalTrendData.statistical_date)).all()

    def get_growth_analysis(self, energy_type: str, cycle: str, months: int = 12) -> List[Dict[str, Any]]:
        """获取增长分析数据（最近N个月）"""
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        trends = self.get_trends_by_date_range(energy_type, start_date, end_date, cycle)

        return [{
            'statistical_date': trend.statistical_date,
            'energy_value': float(trend.energy_value),
            'yoy_growth_rate': float(trend.yoy_growth_rate) if trend.yoy_growth_rate else None,
            'mom_growth_rate': float(trend.mom_growth_rate) if trend.mom_growth_rate else None,
            'industry_average': float(trend.industry_average) if trend.industry_average else None,
            'growth_status': '能耗上升' if trend.yoy_growth_rate and trend.yoy_growth_rate > 0 else '能耗下降'
        } for trend in trends]

    def update_trend(self, trend_id: int, update_data: Dict[str, Any]) -> Optional[HistoricalTrendData]:
        """更新历史趋势数据"""
        with db_manager.get_session() as session:
            trend = session.query(HistoricalTrendData).filter(
                HistoricalTrendData.trend_id == trend_id
            ).first()
            if trend:
                for key, value in update_data.items():
                    setattr(trend, key, value)
                session.commit()
            return trend

    def delete_trend(self, trend_id: int) -> bool:
        """删除历史趋势数据"""
        with db_manager.get_session() as session:
            trend = session.query(HistoricalTrendData).filter(
                HistoricalTrendData.trend_id == trend_id
            ).first()
            if trend:
                session.delete(trend)
                session.commit()
                return True
            return False

    def get_energy_comparison(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """获取多能源类型对比数据"""
        with db_manager.get_session() as session:
            result = session.query(
                HistoricalTrendData.energy_type,
                HistoricalTrendData.statistical_cycle,
                func.avg(HistoricalTrendData.energy_value).label('avg_energy'),
                func.avg(HistoricalTrendData.yoy_growth_rate).label('avg_yoy'),
                func.avg(HistoricalTrendData.mom_growth_rate).label('avg_mom')
            ).filter(
                and_(
                    HistoricalTrendData.statistical_date >= start_date,
                    HistoricalTrendData.statistical_date <= end_date
                )
            ).group_by(
                HistoricalTrendData.energy_type,
                HistoricalTrendData.statistical_cycle
            ).all()

            return [{
                'energy_type': row.energy_type,
                'statistical_cycle': row.statistical_cycle,
                'average_energy': float(row.avg_energy) if row.avg_energy else 0,
                'average_yoy': float(row.avg_yoy) if row.avg_yoy else 0,
                'average_mom': float(row.avg_mom) if row.avg_mom else 0
            } for row in result]