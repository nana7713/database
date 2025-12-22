# dao/transformer_monitoring_dao.py
from models.transformer_monitoring import TransformerMonitoringData
from base import db_manager

class TransformerMonitoringDao:
    def selectAll(self):
        with db_manager.get_session() as session:
            records = session.query(TransformerMonitoringData).all()
            return [{
                'transformer_data_id': record.transformer_data_id,
                'substation_id': record.substation_id,
                'transformer_id': record.transformer_id,
                'collection_time': record.collection_time.isoformat() if record.collection_time else None,
                'load_rate': float(record.load_rate) if record.load_rate else None,
                'winding_temp': float(record.winding_temp) if record.winding_temp else None,
                'core_temp': float(record.core_temp) if record.core_temp else None,
                'ambient_temp': float(record.ambient_temp) if record.ambient_temp else None,
                'ambient_humidity': float(record.ambient_humidity) if record.ambient_humidity else None,
                'running_status': record.running_status
            } for record in records]
    
    def selectById(self, transformer_data_id):
        with db_manager.get_session() as session:
            record = session.query(TransformerMonitoringData).filter(
                TransformerMonitoringData.transformer_data_id == transformer_data_id
            ).first()
            
            if record:
                return {
                    'transformer_data_id': record.transformer_data_id,
                    'substation_id': record.substation_id,
                    'transformer_id': record.transformer_id,
                    'collection_time': record.collection_time.isoformat() if record.collection_time else None,
                    'load_rate': float(record.load_rate) if record.load_rate else None,
                    'winding_temp': float(record.winding_temp) if record.winding_temp else None,
                    'core_temp': float(record.core_temp) if record.core_temp else None,
                    'ambient_temp': float(record.ambient_temp) if record.ambient_temp else None,
                    'ambient_humidity': float(record.ambient_humidity) if record.ambient_humidity else None,
                    'running_status': record.running_status
                }
            return None
    
    def selectBySubstation(self, substation_id):
        with db_manager.get_session() as session:
            records = session.query(TransformerMonitoringData).filter(
                TransformerMonitoringData.substation_id == substation_id
            ).order_by(TransformerMonitoringData.collection_time.desc()).all()
            
            return [self._record_to_dict(record) for record in records]
    
    def selectAbnormalRecords(self):
        """查询所有异常记录"""
        with db_manager.get_session() as session:
            records = session.query(TransformerMonitoringData).filter(
                TransformerMonitoringData.running_status == '异常'
            ).order_by(TransformerMonitoringData.collection_time.desc()).all()
            
            return [self._record_to_dict(record) for record in records]
    
    def insert(self, data):
        with db_manager.get_session() as session:
            record = TransformerMonitoringData(**data)
            session.add(record)
    
    def update(self, transformer_data_id, new_data):
        with db_manager.get_session() as session:
            record = session.query(TransformerMonitoringData).filter(
                TransformerMonitoringData.transformer_data_id == transformer_data_id
            ).first()
            
            if not record:
                print(f"变压器监测数据ID {transformer_data_id} 不存在")
                return None
            
            for key, value in new_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
    
    def deleteById(self, transformer_data_id):
        with db_manager.get_session() as session:
            record = session.query(TransformerMonitoringData).filter(
                TransformerMonitoringData.transformer_data_id == transformer_data_id
            ).first()
            
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
    
    def _record_to_dict(self, record):
        """内部辅助方法"""
        return {
            'transformer_data_id': record.transformer_data_id,
            'substation_id': record.substation_id,
            'transformer_id': record.transformer_id,
            'collection_time': record.collection_time.isoformat() if record.collection_time else None,
            'load_rate': float(record.load_rate) if record.load_rate else None,
            'winding_temp': float(record.winding_temp) if record.winding_temp else None,
            'core_temp': float(record.core_temp) if record.core_temp else None,
            'ambient_temp': float(record.ambient_temp) if record.ambient_temp else None,
            'ambient_humidity': float(record.ambient_humidity) if record.ambient_humidity else None,
            'running_status': record.running_status
        }