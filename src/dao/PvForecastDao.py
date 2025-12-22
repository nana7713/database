from models.pv_forecast import PvForecast
from base import db_manager


class PvForecastDao:
    def select_all(self):
        with db_manager.get_session() as session:
            forecasts = session.query(PvForecast).all()
            return [self._forecast_to_dict(forecast) for forecast in forecasts]

    def select_by_id(self, forecast_id):
        with db_manager.get_session() as session:
            forecast = session.query(PvForecast).filter(PvForecast.forecast_id == forecast_id).first()
            return self._forecast_to_dict(forecast) if forecast else None

    def select_by_device(self, device_id):
        with db_manager.get_session() as session:
            forecasts = session.query(PvForecast).filter(PvForecast.device_id == device_id).all()
            return [self._forecast_to_dict(forecast) for forecast in forecasts]

    def select_by_date(self, forecast_date):
        with db_manager.get_session() as session:
            forecasts = session.query(PvForecast).filter(PvForecast.forecast_date == forecast_date).all()
            return [self._forecast_to_dict(forecast) for forecast in forecasts]

    def select_high_deviation(self, threshold=15.0):
        with db_manager.get_session() as session:
            forecasts = session.query(PvForecast).filter(
                PvForecast.deviation_rate > threshold
            ).all()
            return [self._forecast_to_dict(forecast) for forecast in forecasts]

    def insert(self, forecast_data):
        with db_manager.get_session() as session:
            forecast = PvForecast(**forecast_data)
            session.add(forecast)
            return forecast.forecast_id

    def update(self, forecast_id, new_data):
        with db_manager.get_session() as session:
            forecast = session.query(PvForecast).filter(PvForecast.forecast_id == forecast_id).first()
            if not forecast:
                return None

            for key, value in new_data.items():
                if hasattr(forecast, key):
                    setattr(forecast, key, value)

            return self._forecast_to_dict(forecast)

    def update_deviation_rate(self, forecast_id, actual_generation):
        with db_manager.get_session() as session:
            forecast = session.query(PvForecast).filter(PvForecast.forecast_id == forecast_id).first()
            if not forecast:
                return None

            # 将 Decimal 转换为 float 进行计算
            forecast_generation = float(forecast.forecast_generation) if forecast.forecast_generation else 0
            actual_gen = float(actual_generation) if actual_generation else 0

            if forecast_generation > 0:
                deviation = abs(actual_gen - forecast_generation) / forecast_generation * 100
                forecast.deviation_rate = deviation
                forecast.actual_generation = actual_generation

                return {
                    'forecast_id': forecast.forecast_id,
                    'deviation_rate': float(deviation)
                }
            return None

    def delete(self, forecast_id):
        with db_manager.get_session() as session:
            forecast = session.query(PvForecast).filter(PvForecast.forecast_id == forecast_id).first()
            if forecast:
                session.delete(forecast)
                return True
            return False

    def _forecast_to_dict(self, forecast):
        return {
            'forecast_id': forecast.forecast_id,
            'device_id': forecast.device_id,
            'grid_point_id': forecast.grid_point_id,
            'forecast_date': forecast.forecast_date.isoformat() if forecast.forecast_date else None,
            'time_slot': forecast.time_slot,
            'forecast_generation': float(forecast.forecast_generation) if forecast.forecast_generation else None,
            'actual_data_id': forecast.actual_data_id,
            'actual_generation': float(forecast.actual_generation) if forecast.actual_generation else None,
            'deviation_rate': float(forecast.deviation_rate) if forecast.deviation_rate else None,
            'model_version': forecast.model_version
        }