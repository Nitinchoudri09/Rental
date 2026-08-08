"""
rental_system.py
----------------
Defines the RentalSystem class, which manages the fleet of vehicles.

Demonstrates Composition: RentalSystem *has* a collection of Vehicle objects.
"""

from typing import Dict, List, Optional
from src.vehicle import Vehicle


class RentalSystem:
    """
    Manages a fleet of rental vehicles.

    Responsibilities:
    - Add vehicles to the fleet.
    - Display all available vehicles.
    - Find a vehicle by its unique number.
    - Calculate rental cost for a given vehicle and duration.
    - Rent out a vehicle (mark it unavailable).
    - Accept a returned vehicle (mark it available again).

    Demonstrates:
    - Composition  : Contains Vehicle objects without inheriting from them.
    - Encapsulation: Internal fleet stored as a private dict.
    - Polymorphism : Works with any Vehicle subclass (Car, Bike, …).
    """

    def __init__(self, system_name: str = "Vehicle Rental System") -> None:
        """
        Initialize the RentalSystem.

        Args:
            system_name: Display name shown in menus and reports.
        """
        self._system_name: str = system_name
        # Dict[vehicle_number -> Vehicle] for O(1) lookups
        self._fleet: Dict[str, Vehicle] = {}

    # ------------------------------------------------------------------ #
    #  Property                                                            #
    # ------------------------------------------------------------------ #

    @property
    def system_name(self) -> str:
        """Return the system's display name."""
        return self._system_name

    @property
    def total_vehicles(self) -> int:
        """Return the total number of vehicles in the fleet."""
        return len(self._fleet)

    # ------------------------------------------------------------------ #
    #  Fleet Management                                                    #
    # ------------------------------------------------------------------ #

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """
        Add a vehicle to the fleet.

        Args:
            vehicle: A Vehicle subclass instance to add.

        Raises:
            TypeError : If the argument is not a Vehicle instance.
            ValueError: If a vehicle with the same number already exists.
        """
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
        """Return a list of all vehicles in the fleet."""
        return list(self._fleet.values())

    def get_available_vehicles(self) -> List[Vehicle]:
        """Return only vehicles that are currently available."""
        return [v for v in self._fleet.values() if v.is_available]

    # ------------------------------------------------------------------ #
    #  Look-up                                                             #
    # ------------------------------------------------------------------ #

    def find_vehicle(self, vehicle_number: str) -> Optional[Vehicle]:
        """
        Search for a vehicle by its number (case-insensitive).

        Args:
            vehicle_number: The vehicle number to search for.

        Returns:
            The matching Vehicle, or None if not found.
        """
        if not vehicle_number or not vehicle_number.strip():
            return None
        return self._fleet.get(vehicle_number.strip().upper())

    # ------------------------------------------------------------------ #
    #  Rental Operations                                                   #
    # ------------------------------------------------------------------ #

    def calculate_rental_cost(self, vehicle_number: str, days: int) -> float:
        """
        Calculate the rental cost for a vehicle over a given period.

        Args:
            vehicle_number: The vehicle to price.
            days          : Number of rental days.

        Returns:
            Total rental cost in ₹.

        Raises:
            ValueError: If the vehicle is not found, or if days < 1.
        """
        vehicle = self._get_vehicle_or_raise(vehicle_number)

        if not isinstance(days, int) or days < 1:
            raise ValueError("Number of rental days must be a positive integer.")

        return vehicle.calculate_rental_cost(days)

    def rent_vehicle(self, vehicle_number: str, days: int) -> float:
        """
        Rent out a vehicle for the given number of days.

        Args:
            vehicle_number: Unique number of the vehicle to rent.
            days          : Number of rental days.

        Returns:
            Total rental cost charged in ₹.

        Raises:
            ValueError: If the vehicle is not found, not available, or days < 1.
        """
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
        """
        Accept a returned vehicle and mark it as available again.

        Args:
            vehicle_number: Unique number of the vehicle being returned.

        Raises:
            ValueError: If the vehicle is not found, or was never rented.
        """
        vehicle = self._get_vehicle_or_raise(vehicle_number)

        if vehicle.is_available:
            raise ValueError(
                f"Vehicle '{vehicle_number}' was not rented — nothing to return."
            )

        vehicle.is_available = True

    # ------------------------------------------------------------------ #
    #  Display Helpers                                                     #
    # ------------------------------------------------------------------ #

    def display_all_vehicles(self) -> None:
        """Print full details for every vehicle in the fleet."""
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
        """Print details for vehicles that are currently available."""
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

    # ------------------------------------------------------------------ #
    #  Private Helper                                                      #
    # ------------------------------------------------------------------ #

    def _get_vehicle_or_raise(self, vehicle_number: str) -> Vehicle:
        """
        Retrieve a vehicle or raise ValueError if not found.

        Args:
            vehicle_number: Number to look up.

        Returns:
            The matching Vehicle instance.

        Raises:
            ValueError: If the vehicle number is empty or not in the fleet.
        """
        if not vehicle_number or not vehicle_number.strip():
            raise ValueError("Vehicle number cannot be empty.")

        vehicle = self.find_vehicle(vehicle_number)
        if vehicle is None:
            raise ValueError(
                f"No vehicle with number '{vehicle_number.strip().upper()}' found in the fleet."
            )
        return vehicle
