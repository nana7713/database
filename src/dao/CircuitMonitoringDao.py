# dao/circuit_monitoring_dao.py
from models.circuit_monitoring import CircuitMonitoringData
from base import db_manager
from datetime import datetime

class CircuitMonitoringDao:
    def selectAll(self):
        with db_manager.get_session() as session:
            records = session.query(CircuitMonitoringData).all()
            return [{
                'circuit_data_id': record.circuit_data_id,
                'substation_id': record.substation_id,
                'circuit_id': record.circuit_id,
                'collection_time': record.collection_time.isoformat() if record.collection_time else None,
                'voltage': float(record.voltage) if record.voltage else None,
                'current': float(record.current) if record.current else None,
                'active_power': float(record.active_power) if record.active_power else None,
                'reactive_power': float(record.reactive_power) if record.reactive_power else None,
                'power_factor': float(record.power_factor) if record.power_factor else None,
                'forward_active_energy': float(record.forward_active_energy) if record.forward_active_energy else None,
                'reverse_active_energy': float(record.reverse_active_energy) if record.reverse_active_energy else None,
                'switch_status': record.switch_status,
                'cable_temp': float(record.cable_temp) if record.cable_temp else None,
                'capacitor_temp': float(record.capacitor_temp) if record.capacitor_temp else None
            } for record in records]
    
    def selectById(self, circuit_data_id):
        with db_manager.get_session() as session:
            record = session.query(CircuitMonitoringData).filter(CircuitMonitoringData.circuit_data_id == circuit_data_id).first()
            if record:
                return {
                    'circuit_data_id': record.circuit_data_id,
                    'substation_id': record.substation_id,
                    'circuit_id': record.circuit_id,
                    'collection_time': record.collection_time.isoformat() if record.collection_time else None,
                    'voltage': float(record.voltage) if record.voltage else None,
                    'current': float(record.current) if record.current else None,
                    'active_power': float(record.active_power) if record.active_power else None,
                    'reactive_power': float(record.reactive_power) if record.reactive_power else None,
                    'power_factor': float(record.power_factor) if record.power_factor else None,
                    'forward_active_energy': float(record.forward_active_energy) if record.forward_active_energy else None,
                    'reverse_active_energy': float(record.reverse_active_energy) if record.reverse_active_energy else None,
                    'switch_status': record.switch_status,
                    'cable_temp': float(record.cable_temp) if record.cable_temp else None,
                    'capacitor_temp': float(record.capacitor_temp) if record.capacitor_temp else None
                }
            return None
    
    def selectBySubstation(self, substation_id):
        with db_manager.get_session() as session:
            records = session.query(CircuitMonitoringData).filter(
                CircuitMonitoringData.substation_id == substation_id
            ).order_by(CircuitMonitoringData.collection_time.desc()).all()
            
            return [{
                'circuit_data_id': record.circuit_data_id,
                'substation_id': record.substation_id,
                'circuit_id': record.circuit_id,
                'collection_time': record.collection_time.isoformat() if record.collection_time else None,
                'voltage': float(record.voltage) if record.voltage else None,
                'current': float(record.current) if record.current else None,
                'active_power': float(record.active_power) if record.active_power else None,
                'reactive_power': float(record.reactive_power) if record.reactive_power else None,
                'power_factor': float(record.power_factor) if record.power_factor else None,
                'forward_active_energy': float(record.forward_active_energy) if record.forward_active_energy else None,
                'reverse_active_energy': float(record.reverse_active_energy) if record.reverse_active_energy else None,
                'switch_status': record.switch_status,
                'cable_temp': float(record.cable_temp) if record.cable_temp else None,
                'capacitor_temp': float(record.capacitor_temp) if record.capacitor_temp else None
            } for record in records]
    
    def selectBySubstationAndCircuit(self, substation_id, circuit_id):
        """根据变电站和电路ID查询"""
        with db_manager.get_session() as session:
            records = session.query(CircuitMonitoringData).filter(
                CircuitMonitoringData.substation_id == substation_id,
                CircuitMonitoringData.circuit_id == circuit_id
            ).order_by(CircuitMonitoringData.collection_time.desc()).all()
            
            return [self._record_to_dict(record) for record in records]
    
    def selectLatestBySubstation(self, substation_id, limit=100):
        """获取指定变电站的最新监测数据"""
        with db_manager.get_session() as session:
            records = session.query(CircuitMonitoringData).filter(
                CircuitMonitoringData.substation_id == substation_id
            ).order_by(CircuitMonitoringData.collection_time.desc()).limit(limit).all()
            
            return [self._record_to_dict(record) for record in records]
    
    def insert(self, data):
        """插入监测数据"""
        with db_manager.get_session() as session:
            record = CircuitMonitoringData(**data)
            session.add(record)
    
    def batchInsert(self, data_list):
        """批量插入监测数据"""
        with db_manager.get_session() as session:
            records = [CircuitMonitoringData(**data) for data in data_list]
            session.add_all(records)
            session.commit()
            # 批量刷新获取ID
            for record in records:
                session.refresh(record)
            return [record.circuit_data_id for record in records]
    
    def update(self, circuit_data_id, new_data):
        with db_manager.get_session() as session:
            record = session.query(CircuitMonitoringData).filter(
                CircuitMonitoringData.circuit_data_id == circuit_data_id
            ).first()
            
            if not record:
                print(f"监测数据ID {circuit_data_id} 不存在")
                return None
            
            for key, value in new_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
    
    def deleteById(self, circuit_data_id):
        with db_manager.get_session() as session:
            record = session.query(CircuitMonitoringData).filter(
                CircuitMonitoringData.circuit_data_id == circuit_data_id
            ).first()
            
            if record:
                session.delete(record)
                return True
            return False
    
    def deleteBySubstation(self, substation_id):
        """删除某个变电站的所有监测数据"""
        with db_manager.get_session() as session:
            count = session.query(CircuitMonitoringData).filter(
                CircuitMonitoringData.substation_id == substation_id
            ).delete()
            return count  # 返回删除的行数
    
    def _record_to_dict(self, record):
        """将记录对象转换为字典（内部辅助方法）"""
        return {
            'circuit_data_id': record.circuit_data_id,
            'substation_id': record.substation_id,
            'circuit_id': record.circuit_id,
            'collection_time': record.collection_time.isoformat() if record.collection_time else None,
            'voltage': float(record.voltage) if record.voltage else None,
            'current': float(record.current) if record.current else None,
            'active_power': float(record.active_power) if record.active_power else None,
            'reactive_power': float(record.reactive_power) if record.reactive_power else None,
            'power_factor': float(record.power_factor) if record.power_factor else None,
            'forward_active_energy': float(record.forward_active_energy) if record.forward_active_energy else None,
            'reverse_active_energy': float(record.reverse_active_energy) if record.reverse_active_energy else None,
            'switch_status': record.switch_status,
            'cable_temp': float(record.cable_temp) if record.cable_temp else None,
            'capacitor_temp': float(record.capacitor_temp) if record.capacitor_temp else None
        }