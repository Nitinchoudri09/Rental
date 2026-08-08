from typing import Dict, List, Optional
from src.vehicle import Vehicle

class RentalSystem:

    def __init__(self, system_name: str = "Vehicle Rental System") -> None:

        self._system_name: str = system_name

        self._fleet: Dict[str, Vehicle] = {}

    @property
    def system_name(self) -> str:

        return self._system_name

    @property
    def total_vehicles(self) -> int:

        return len(self._fleet)

    def add_vehicle(self, vehicle: Vehicle) -> None:

        if not isinstance(vehicle, Vehicle):
            raise TypeError("Only Vehicle instances can be added to the fleet.")

        number = vehicle.vehicle_number
        if number in self._fleet:
            raise ValueError(
                f"Vehicle '{number}' already exists in the fleet. "
                "Each vehicle must have a unique number."
            )

        self._fleet[number] = vehicle
        print(f"  [+] {vehicle.get_vehicle_type()} '{number}' ({vehicle.brand}) added successfully.")

    def get_all_vehicles(self) -> List[Vehicle]:

        return list(self._fleet.values())

    def get_available_vehicles(self) -> List[Vehicle]:

        return [v for v in self._fleet.values() if v.is_available]

    def find_vehicle(self, vehicle_number: str) -> Optional[Vehicle]:

        if not vehicle_number or not vehicle_number.strip():
            return None
        return self._fleet.get(vehicle_number.strip().upper())

    def calculate_rental_cost(self, vehicle_number: str, days: int) -> float:

        vehicle = self._get_vehicle_or_raise(vehicle_number)

        if not isinstance(days, int) or days < 1:
            raise ValueError("Number of rental days must be a positive integer.")

        return vehicle.calculate_rental_cost(days)

    def rent_vehicle(self, vehicle_number: str, days: int) -> float:

        vehicle = self._get_vehicle_or_raise(vehicle_number)

        if not vehicle.is_available:
            raise ValueError(
                f"Vehicle '{vehicle_number}' is currently rented out and not available."
            )

        if not isinstance(days, int) or days < 1:
            raise ValueError("Number of rental days must be a positive integer.")

        cost = vehicle.calculate_rental_cost(days)
        vehicle.is_available = False
        return cost

    def return_vehicle(self, vehicle_number: str) -> None:

        vehicle = self._get_vehicle_or_raise(vehicle_number)

        if vehicle.is_available:
            raise ValueError(
                f"Vehicle '{vehicle_number}' was not rented — nothing to return."
            )

        vehicle.is_available = True

    def display_all_vehicles(self) -> None:

        if not self._fleet:
            print("  (No vehicles in the fleet.)")
            return

        print(f"\n{'-' * 50}")
        print(f"  {self._system_name}  -  Fleet ({self.total_vehicles} vehicles)")
        print(f"{'-' * 50}")
        for vehicle in self._fleet.values():
            print(vehicle.display_details())
            print(f"{'-' * 50}")

    def display_available_vehicles(self) -> None:

        available = self.get_available_vehicles()
        if not available:
            print("  (No vehicles currently available.)")
            return

        print(f"\n{'-' * 50}")
        print(f"  Available Vehicles  ({len(available)} of {self.total_vehicles})")
        print(f"{'-' * 50}")
        for vehicle in available:
            print(vehicle.display_details())
            print(f"{'-' * 50}")

    def _get_vehicle_or_raise(self, vehicle_number: str) -> Vehicle:

        if not vehicle_number or not vehicle_number.strip():
            raise ValueError("Vehicle number cannot be empty.")

        vehicle = self.find_vehicle(vehicle_number)
        if vehicle is None:
            raise ValueError(
                f"No vehicle with number '{vehicle_number.strip().upper()}' found in the fleet."
            )
        return vehicle
