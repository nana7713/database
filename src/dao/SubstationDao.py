# dao/substation_dao.py
from models.substation import Substation
from base import db_manager

class SubstationDao:
    def selectAll(self):
        with db_manager.get_session() as session:
            stations = session.query(Substation).all()
            return [{
                'substation_id': station.substation_id,
                'plant_area_id': station.plant_area_id,
                'substation_name': station.substation_name,
                'substation_location_desc': station.substation_location_desc,
                'voltage_level': station.voltage_level,
                'transformer_count': station.transformer_count,
                'commissioning_date': station.commissioning_date.isoformat() if station.commissioning_date else None,
                'responsible_user_id': station.responsible_user_id,
                'contact_phone': station.contact_phone
            } for station in stations]
    
    def selectBySubstationId(self, substation_id):
        with db_manager.get_session() as session:
            station = session.query(Substation).filter(Substation.substation_id == substation_id).first()
            if station:
                return {
                    'substation_id': station.substation_id,
                    'plant_area_id': station.plant_area_id,
                    'substation_name': station.substation_name,
                    'substation_location_desc': station.substation_location_desc,
                    'voltage_level': station.voltage_level,
                    'transformer_count': station.transformer_count,
                    'commissioning_date': station.commissioning_date.isoformat() if station.commissioning_date else None,
                    'responsible_user_id': station.responsible_user_id,
                    'contact_phone': station.contact_phone
                }
            return None
    
    def selectByPlantAreaId(self, plant_area_id):
        """根据厂区ID查询变电站"""
        with db_manager.get_session() as session:
            stations = session.query(Substation).filter(Substation.plant_area_id == plant_area_id).all()
            return [{
                'substation_id': station.substation_id,
                'plant_area_id': station.plant_area_id,
                'substation_name': station.substation_name,
                'substation_location_desc': station.substation_location_desc,
                'voltage_level': station.voltage_level,
                'transformer_count': station.transformer_count,
                'commissioning_date': station.commissioning_date.isoformat() if station.commissioning_date else None,
                'responsible_user_id': station.responsible_user_id,
                'contact_phone': station.contact_phone
            } for station in stations]
    
    def selectByResponsibleUserId(self, user_id):
        """根据负责人ID查询变电站"""
        with db_manager.get_session() as session:
            stations = session.query(Substation).filter(Substation.responsible_user_id == user_id).all()
            return [{
                'substation_id': station.substation_id,
                'plant_area_id': station.plant_area_id,
                'substation_name': station.substation_name,
                'substation_location_desc': station.substation_location_desc,
                'voltage_level': station.voltage_level,
                'transformer_count': station.transformer_count,
                'commissioning_date': station.commissioning_date.isoformat() if station.commissioning_date else None,
                'responsible_user_id': station.responsible_user_id,
                'contact_phone': station.contact_phone
            } for station in stations]
    
    def insert(self, station_data):
        with db_manager.get_session() as session:
            station = Substation(**station_data)
            session.add(station)
            return station.substation_id
    
    def update(self, substation_id, new_data):
        with db_manager.get_session() as session:
            station = session.query(Substation).filter(Substation.substation_id == substation_id).first()
            if not station:
                print(f"变电站ID {substation_id} 不存在")
                return None
            
            for key, value in new_data.items():
                if hasattr(station, key):
                    setattr(station, key, value)
          
            
            return {
                'substation_id': station.substation_id,
                'plant_area_id': station.plant_area_id,
                'substation_name': station.substation_name,
                'substation_location_desc': station.substation_location_desc,
                'voltage_level': station.voltage_level,
                'transformer_count': station.transformer_count,
                'commissioning_date': station.commissioning_date.isoformat() if station.commissioning_date else None,
                'responsible_user_id': station.responsible_user_id,
                'contact_phone': station.contact_phone
            }
    
    def deleteBySubstationId(self, substation_id):
        with db_manager.get_session() as session:
            station = session.query(Substation).filter(Substation.substation_id == substation_id).first()
            if station:
                session.delete(station)
                return True
            return False
    
    def countByPlantArea(self, plant_area_id):
        """统计某个厂区的变电站数量"""
        with db_manager.get_session() as session:
            return session.query(Substation).filter(Substation.plant_area_id == plant_area_id).count()