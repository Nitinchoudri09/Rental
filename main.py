"""
main.py
=======
Entry point for the Vehicle Rental System.

On startup:
    1. Loads persisted fleet data (if any) from data/fleet.json
    2. Seeds a demo fleet if no data exists yet
    3. Launches the interactive CLI
"""

from __future__ import annotations

from rental_system.factory import VehicleFactory
from rental_system.manager import RentalManager
from rental_system.models import Car, Bike
from rental_system.cli import RentalCLI


# ─────────────────────────────────────────────────────────────────────────────
# Pre-seeded demo fleet
# ─────────────────────────────────────────────────────────────────────────────

DEMO_FLEET = [
    # Cars
    Car(
        vehicle_number="KA-01-AB-1234",
        brand="Maruti Swift",
        base_price_per_day=800.0,
        seats=5,          # 1 extra seat → +Rs.100/day
    ),
    Car(
        vehicle_number="MH-12-CD-5678",
        brand="Toyota Innova",
        base_price_per_day=1500.0,
        seats=8,          # 4 extra seats → +Rs.400/day
    ),
    Car(
        vehicle_number="DL-03-EF-0011",
        brand="Hyundai Creta",
        base_price_per_day=1200.0,
        seats=5,
    ),
    # Bikes
    Bike(
        vehicle_number="DL-05-GH-9012",
        brand="Honda Activa 6G",
        base_price_per_day=200.0,
        engine_cc=110,    # ≤ 150 cc → no surcharge
    ),
    Bike(
        vehicle_number="TN-09-IJ-3456",
        brand="KTM Duke 200",
        base_price_per_day=400.0,
        engine_cc=200,    # > 150 cc → +Rs.50/day
    ),
    Bike(
        vehicle_number="RJ-14-KL-7890",
        brand="Royal Enfield Classic 350",
        base_price_per_day=500.0,
        engine_cc=350,    # > 150 cc → +Rs.50/day
    ),
]


def _seed_fleet(manager: RentalManager) -> None:
    """Add demo vehicles to the manager (skip if already loaded from file)."""
    for vehicle in DEMO_FLEET:
        try:
            manager.add_vehicle(vehicle)
        except Exception:
            pass   # already exists from saved data — ignore


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

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
