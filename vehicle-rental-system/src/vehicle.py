from abc import ABC, abstractmethod

class Vehicle(ABC):

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        rental_price_per_day: float,
    ) -> None:

        if not vehicle_number or not vehicle_number.strip():
            raise ValueError("Vehicle number cannot be empty.")
        if not brand or not brand.strip():
            raise ValueError("Brand name cannot be empty.")
        if rental_price_per_day <= 0:
            raise ValueError("Rental price per day must be a positive number.")

        self._vehicle_number: str = vehicle_number.strip().upper()
        self._brand: str = brand.strip()
        self._rental_price_per_day: float = rental_price_per_day
        self._is_available: bool = True   

    @property
    def vehicle_number(self) -> str:

        return self._vehicle_number

    @property
    def brand(self) -> str:

        return self._brand

    @property
    def rental_price_per_day(self) -> float:

        return self._rental_price_per_day

    @property
    def is_available(self) -> bool:

        return self._is_available

    @is_available.setter
    def is_available(self, value: bool) -> None:

        if not isinstance(value, bool):
            raise ValueError("Availability must be a boolean value.")
        self._is_available = value

    @abstractmethod
    def calculate_rental_cost(self, days: int) -> float:

        pass

    @abstractmethod
    def get_vehicle_type(self) -> str:

        pass

    def display_details(self) -> str:

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
