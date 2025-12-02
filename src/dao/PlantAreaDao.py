# dao/plantarea_dao.py
from models.plant_area import PlantArea
from base import db_manager

class PlantAreaDao:
    def selectAll(self):
        with db_manager.get_session() as session:
            areas = session.query(PlantArea).all()
            return [{
                'plant_area_id': area.plant_area_id,
                'plant_area_name': area.plant_area_name,
                'location_desc': area.location_desc,
                'manager_id': area.manager_id,
                'contact_phone': area.contact_phone
            } for area in areas]
    
    def selectByPlantAreaId(self, plant_area_id):
        with db_manager.get_session() as session:
            area = session.query(PlantArea).filter(PlantArea.plant_area_id == plant_area_id).first()
            if area:
                return {
                    'plant_area_id': area.plant_area_id,
                    'plant_area_name': area.plant_area_name,
                    'location_desc': area.location_desc,
                    'manager_id': area.manager_id,
                    'contact_phone': area.contact_phone
                }
            return None
    
    def selectByManagerId(self, manager_id):
        with db_manager.get_session() as session:
            areas = session.query(PlantArea).filter(PlantArea.manager_id == manager_id).all()
            return [{
                'plant_area_id': area.plant_area_id,
                'plant_area_name': area.plant_area_name,
                'location_desc': area.location_desc,
                'manager_id': area.manager_id,
                'contact_phone': area.contact_phone
            } for area in areas]
    
    def insert(self, area_data):
        """插入厂区，area_data 是字典"""
        with db_manager.get_session() as session:
            area = PlantArea(**area_data)
            session.add(area)
            return area.plant_area_id
    
    def update(self, plant_area_id, new_data):
        with db_manager.get_session() as session:
            area = session.query(PlantArea).filter(PlantArea.plant_area_id == plant_area_id).first()
            if not area:
                print(f"厂区ID {plant_area_id} 不存在")
                return None
            
            for key, value in new_data.items():
                if hasattr(area, key):
                    setattr(area, key, value)
            
            
            return {
                'plant_area_id': area.plant_area_id,
                'plant_area_name': area.plant_area_name,
                'location_desc': area.location_desc,
                'manager_id': area.manager_id,
                'contact_phone': area.contact_phone
            }
    
    def deleteByPlantAreaId(self, plant_area_id):
        with db_manager.get_session() as session:
            area = session.query(PlantArea).filter(PlantArea.plant_area_id == plant_area_id).first()
            if area:
                session.delete(area)
                return True
            return False
    
    def count(self):
        """统计厂区数量"""
        with db_manager.get_session() as session:
            return session.query(PlantArea).count()