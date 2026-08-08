"""
car.py
------
Defines the Car subclass, which extends Vehicle.

Pricing Rule:
  - Rentals of 1–6 days  → base price × days
  - Rentals of 7+ days   → 10 % discount applied to the total
"""

from src.vehicle import Vehicle


class Car(Vehicle):
    """
    Represents a rental car.

    Demonstrates:
    - Inheritance      : Extends the Vehicle base class.
    - Method Overriding: Implements calculate_rental_cost() with car-specific logic.
    - Encapsulation    : number_of_seats stored as a private attribute.
    """

    LONG_RENTAL_THRESHOLD: int = 7       # Days required to qualify for discount
    LONG_RENTAL_DISCOUNT: float = 0.10   # 10 % discount for week-long or longer rentals

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        rental_price_per_day: float,
        number_of_seats: int,
    ) -> None:
        """
        Initialize a Car instance.

        Args:
            vehicle_number      : Unique identifier for the car.
            brand               : Manufacturer / brand name.
            rental_price_per_day: Base rental price in ₹ per day.
            number_of_seats     : Passenger seating capacity. Must be ≥ 1.

        Raises:
            ValueError: Propagated from Vehicle, or if number_of_seats < 1.
        """
        super().__init__(vehicle_number, brand, rental_price_per_day)

        if number_of_seats < 1:
            raise ValueError("Number of seats must be at least 1.")

        self._number_of_seats: int = number_of_seats

    # ------------------------------------------------------------------ #
    #  Property                                                            #
    # ------------------------------------------------------------------ #

    @property
    def number_of_seats(self) -> int:
        """Return the seating capacity of the car."""
        return self._number_of_seats

    # ------------------------------------------------------------------ #
    #  Overridden Abstract Methods                                         #
    # ------------------------------------------------------------------ #

    def get_vehicle_type(self) -> str:
        """Return the vehicle type label."""
        return "Car"

    def calculate_rental_cost(self, days: int) -> float:
        """
        Calculate the total rental cost for the car.

        Applies a 10 % discount when the rental period is 7 days or more.

        Args:
            days: Number of rental days. Must be a positive integer.

        Returns:
            Total rental cost in ₹.

        Raises:
            ValueError: If days is not a positive integer.
        """
        if not isinstance(days, int) or days < 1:
            raise ValueError("Number of rental days must be a positive integer.")

        total = self._rental_price_per_day * days

        if days >= self.LONG_RENTAL_THRESHOLD:
            discount = total * self.LONG_RENTAL_DISCOUNT
            total -= discount

        return round(total, 2)

    # ------------------------------------------------------------------ #
    #  Overridden Display                                                  #
    # ------------------------------------------------------------------ #

    def display_details(self) -> str:
        """Return car details including seating capacity and discount note."""
        base = super().display_details()
        discount_note = (
            f"10% discount for {self.LONG_RENTAL_THRESHOLD}+ day rentals"
        )
        return (
            f"{base}\n"
            f"  Seats          : {self._number_of_seats}\n"
            f"  Pricing Note   : {discount_note}"
        )
