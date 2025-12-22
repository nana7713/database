from models.pv_generation import PvGeneration
from base import db_manager


class PvGenerationDao:
    def select_all(self):
        with db_manager.get_session() as session:
            records = session.query(PvGeneration).all()
            return [self._record_to_dict(record) for record in records]

    def select_by_id(self, data_id):
        with db_manager.get_session() as session:
            record = session.query(PvGeneration).filter(PvGeneration.data_id == data_id).first()
            return self._record_to_dict(record) if record else None

    def select_by_device(self, device_id):
        with db_manager.get_session() as session:
            records = session.query(PvGeneration).filter(PvGeneration.device_id == device_id).all()
            return [self._record_to_dict(record) for record in records]

    def select_by_time_range(self, start_time, end_time):
        with db_manager.get_session() as session:
            records = session.query(PvGeneration).filter(
                PvGeneration.collect_time.between(start_time, end_time)
            ).all()
            return [self._record_to_dict(record) for record in records]

    def select_abnormal_efficiency(self, threshold=85.0):
        with db_manager.get_session() as session:
            records = session.query(PvGeneration).filter(
                PvGeneration.inverter_efficiency < threshold
            ).all()
            return [self._record_to_dict(record) for record in records]

    def insert(self, data):
        with db_manager.get_session() as session:
            record = PvGeneration(**data)
            session.add(record)
            return record.data_id

    def batch_insert(self, data_list):
        with db_manager.get_session() as session:
            records = [PvGeneration(**data) for data in data_list]
            session.add_all(records)
            return [record.data_id for record in records]

    def update(self, data_id, new_data):
        with db_manager.get_session() as session:
            record = session.query(PvGeneration).filter(PvGeneration.data_id == data_id).first()
            if not record:
                return None

            for key, value in new_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)

            return self._record_to_dict(record)

    def delete(self, data_id):
        with db_manager.get_session() as session:
            record = session.query(PvGeneration).filter(PvGeneration.data_id == data_id).first()
            if record:
                session.delete(record)
                return True
            return False

    def _record_to_dict(self, record):
        return {
            'data_id': record.data_id,
            'device_id': record.device_id,
            'grid_point_id': record.grid_point_id,
            'collect_time': record.collect_time.isoformat() if record.collect_time else None,
            'generation': float(record.generation) if record.generation else None,
            'feed_in': float(record.feed_in) if record.feed_in else None,
            'self_use': float(record.self_use) if record.self_use else None,
            'inverter_efficiency': float(record.inverter_efficiency) if record.inverter_efficiency else None,
            'string_voltage': float(record.string_voltage) if record.string_voltage else None,
            'string_current': float(record.string_current) if record.string_current else None
        }