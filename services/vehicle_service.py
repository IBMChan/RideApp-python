
from models.vehicle import Vehicle
from utils.db import vehicles_col


class VehicleService:
    def get_next_vehicle_id(self) -> str:
        vehicles = list(vehicles_col.find())
        max_id = 0
        for v in vehicles:
            vid = v.get("vehicle_id", "")
            if isinstance(vid, int):
                max_id = max(max_id, vid)
            elif isinstance(vid, str) and vid and vid[0].upper() == 'V' and vid[1:].isdigit():
                max_id = max(max_id, int(vid[1:]))
        return f"V{max_id+1:03d}"
    def __init__(self):
        pass


    def load_vehicles(self):
        return {v["driver_id"]: v for v in vehicles_col.find()}


    def save_vehicle(self, driver_id: str, vehicle: Vehicle, vehicle_id: str):
        doc = {
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "make": vehicle.make,
            "model": vehicle.model,
            "plate": vehicle.plate,
            "color": vehicle.color,
            "year": vehicle.year
        }
        vehicles_col.update_one({"vehicle_id": vehicle_id}, {"$set": doc}, upsert=True)

    def register_vehicle(self, driver_id: str, vehicle: Vehicle, vehicle_id: str):
        self.save_vehicle(driver_id, vehicle, vehicle_id)
        print(f"✅ Vehicle registered for driver {driver_id} with vehicle_id {vehicle_id}")
