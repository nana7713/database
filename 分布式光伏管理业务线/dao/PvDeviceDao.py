from models.pv_device import PvDevice
from base import db_manager


class PvDeviceDao:
    def select_all(self):
        with db_manager.get_session() as session:
            devices = session.query(PvDevice).all()
            return [{
                'device_id': device.device_id,
                'device_type': device.device_type,
                'location': device.location,
                'capacity': float(device.capacity) if device.capacity else None,
                'operation_date': device.operation_date.isoformat() if device.operation_date else None,
                'calibration_cycle': device.calibration_cycle,
                'status': device.status,
                'protocol': device.protocol
            } for device in devices]

    def select_by_id(self, device_id):
        with db_manager.get_session() as session:
            device = session.query(PvDevice).filter(PvDevice.device_id == device_id).first()
            if device:
                return {
                    'device_id': device.device_id,
                    'device_type': device.device_type,
                    'location': device.location,
                    'capacity': float(device.capacity) if device.capacity else None,
                    'operation_date': device.operation_date.isoformat() if device.operation_date else None,
                    'calibration_cycle': device.calibration_cycle,
                    'status': device.status,
                    'protocol': device.protocol
                }
            return None

    def select_by_status(self, status):
        with db_manager.get_session() as session:
            devices = session.query(PvDevice).filter(PvDevice.status == status).all()
            return [self._device_to_dict(device) for device in devices]

    def select_by_type(self, device_type):
        with db_manager.get_session() as session:
            devices = session.query(PvDevice).filter(PvDevice.device_type == device_type).all()
            return [self._device_to_dict(device) for device in devices]

    def insert(self, device_data):
        with db_manager.get_session() as session:
            device = PvDevice(**device_data)
            session.add(device)
            return device.device_id

    def update(self, device_id, new_data):
        with db_manager.get_session() as session:
            device = session.query(PvDevice).filter(PvDevice.device_id == device_id).first()
            if not device:
                return None

            for key, value in new_data.items():
                if hasattr(device, key):
                    setattr(device, key, value)

            return self._device_to_dict(device)

    def delete(self, device_id):
        with db_manager.get_session() as session:
            device = session.query(PvDevice).filter(PvDevice.device_id == device_id).first()
            if device:
                session.delete(device)
                return True
            return False

    def count_by_status(self, status):
        with db_manager.get_session() as session:
            return session.query(PvDevice).filter(PvDevice.status == status).count()

    def _device_to_dict(self, device):
        return {
            'device_id': device.device_id,
            'device_type': device.device_type,
            'location': device.location,
            'capacity': float(device.capacity) if device.capacity else None,
            'operation_date': device.operation_date.isoformat() if device.operation_date else None,
            'calibration_cycle': device.calibration_cycle,
            'status': device.status,
            'protocol': device.protocol
        }