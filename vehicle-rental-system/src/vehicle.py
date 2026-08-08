"""
vehicle.py
----------
Defines the abstract base Vehicle class.

All vehicle types (Car, Bike, etc.) must inherit from this class
and implement the abstract methods.
"""

from abc import ABC, abstractmethod


class Vehicle(ABC):
    """
    Abstract base class representing a generic rental vehicle.

    Demonstrates:
    - Abstraction  : Abstract methods force subclasses to define their own behavior.
    - Encapsulation: Attributes are stored as private and accessed via properties.
    """

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        rental_price_per_day: float,
    ) -> None:
        """
        Initialize a Vehicle instance.

        Args:
            vehicle_number      : Unique identifier for the vehicle (e.g. 'MH12AB1234').
            brand               : Manufacturer / brand name (e.g. 'Honda').
            rental_price_per_day: Base rental price in ₹ per day. Must be positive.

        Raises:
            ValueError: If vehicle_number is empty, brand is empty,
                        or rental_price_per_day is not positive.
        """
        if not vehicle_number or not vehicle_number.strip():
            raise ValueError("Vehicle number cannot be empty.")
        if not brand or not brand.strip():
            raise ValueError("Brand name cannot be empty.")
        if rental_price_per_day <= 0:
            raise ValueError("Rental price per day must be a positive number.")

        # Private attributes — access through properties
        self._vehicle_number: str = vehicle_number.strip().upper()
        self._brand: str = brand.strip()
        self._rental_price_per_day: float = rental_price_per_day
        self._is_available: bool = True   # All vehicles start as available

    # ------------------------------------------------------------------ #
    #  Properties (Encapsulation)                                          #
    # ------------------------------------------------------------------ #

    @property
    def vehicle_number(self) -> str:
        """Return the vehicle's unique number."""
        return self._vehicle_number

    @property
    def brand(self) -> str:
        """Return the vehicle's brand."""
        return self._brand

    @property
    def rental_price_per_day(self) -> float:
        """Return the base rental price per day."""
        return self._rental_price_per_day

    @property
    def is_available(self) -> bool:
        """Return True if the vehicle is available for rent."""
        return self._is_available

    @is_available.setter
    def is_available(self, value: bool) -> None:
        """Set the availability status of the vehicle."""
        if not isinstance(value, bool):
            raise ValueError("Availability must be a boolean value.")
        self._is_available = value

    # ------------------------------------------------------------------ #
    #  Abstract Methods (Abstraction + Polymorphism)                       #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def calculate_rental_cost(self, days: int) -> float:
        """
        Calculate the total rental cost for the given number of days.

        Subclasses must override this to apply their own pricing logic.

        Args:
            days: Number of rental days. Must be a positive integer.

        Returns:
            Total rental cost in ₹.
        """
        pass

    @abstractmethod
    def get_vehicle_type(self) -> str:
        """Return a human-readable string describing the vehicle type."""
        pass

    # ------------------------------------------------------------------ #
    #  Shared / Concrete Methods                                           #
    # ------------------------------------------------------------------ #

    def display_details(self) -> str:
        """
        Return a formatted string with the vehicle's details.

        Subclasses can call super().display_details() and append
        their own type-specific information.
        """
        availability = "Available" if self._is_available else "Rented Out"
        return (
            f"  Type           : {self.get_vehicle_type()}\n"
            f"  Vehicle Number : {self._vehicle_number}\n"
            f"  Brand          : {self._brand}\n"
            f"  Price / Day    : ₹{self._rental_price_per_day:,.2f}\n"
            f"  Status         : {availability}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"vehicle_number='{self._vehicle_number}', "
            f"brand='{self._brand}', "
            f"rental_price_per_day={self._rental_price_per_day})"
        )
