from __future__ import annotations

from rental_system.factory import VehicleFactory
from rental_system.manager import RentalManager
from rental_system.models import Car, Bike
from rental_system.cli import RentalCLI

DEMO_FLEET = [

    Car(
        vehicle_number="KA-01-AB-1234",
        brand="Maruti Swift",
        base_price_per_day=800.0,
        seats=5,          
    ),
    Car(
        vehicle_number="MH-12-CD-5678",
        brand="Toyota Innova",
        base_price_per_day=1500.0,
        seats=8,          
    ),
    Car(
        vehicle_number="DL-03-EF-0011",
        brand="Hyundai Creta",
        base_price_per_day=1200.0,
        seats=5,
    ),

    Bike(
        vehicle_number="DL-05-GH-9012",
        brand="Honda Activa 6G",
        base_price_per_day=200.0,
        engine_cc=110,    
    ),
    Bike(
        vehicle_number="TN-09-IJ-3456",
        brand="KTM Duke 200",
        base_price_per_day=400.0,
        engine_cc=200,    
    ),
    Bike(
        vehicle_number="RJ-14-KL-7890",
        brand="Royal Enfield Classic 350",
        base_price_per_day=500.0,
        engine_cc=350,    
    ),
]

def _seed_fleet(manager: RentalManager) -> None:

    for vehicle in DEMO_FLEET:
        try:
            manager.add_vehicle(vehicle)
        except Exception:
            pass   

if __name__ == "__main__":
    DATA_FILE = "data/fleet.json"

    manager = RentalManager(data_file=DATA_FILE)
    manager.load_fleet()

    if manager.fleet_size() == 0:
        print("\n  [INFO] No saved data found — loading demo fleet...")
        _seed_fleet(manager)
        manager.save_fleet()

    cli = RentalCLI(manager)
    cli.run()
