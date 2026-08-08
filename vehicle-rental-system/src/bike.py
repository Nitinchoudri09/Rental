"""
bike.py
-------
Defines the Bike subclass, which extends Vehicle.

Pricing Rule:
  - Rentals of 1–4 days → base price × days
  - Rentals of 5+ days  → 5 % discount applied to the total
"""

from src.vehicle import Vehicle


class Bike(Vehicle):
    """
    Represents a rental bike (motorcycle / scooter).

    Demonstrates:
    - Inheritance      : Extends the Vehicle base class.
    - Method Overriding: Implements calculate_rental_cost() with bike-specific logic.
    - Encapsulation    : engine_capacity_cc stored as a private attribute.
    """

    LONG_RENTAL_THRESHOLD: int = 5      # Days required to qualify for discount
    LONG_RENTAL_DISCOUNT: float = 0.05  # 5 % discount for 5-day or longer rentals

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        rental_price_per_day: float,
        engine_capacity_cc: int,
    ) -> None:
        """
        Initialize a Bike instance.

        Args:
            vehicle_number      : Unique identifier for the bike.
            brand               : Manufacturer / brand name.
            rental_price_per_day: Base rental price in ₹ per day.
            engine_capacity_cc  : Engine displacement in cubic centimetres. Must be > 0.

        Raises:
            ValueError: Propagated from Vehicle, or if engine_capacity_cc ≤ 0.
        """
        super().__init__(vehicle_number, brand, rental_price_per_day)

        if engine_capacity_cc <= 0:
            raise ValueError("Engine capacity must be a positive integer (cc).")

        self._engine_capacity_cc: int = engine_capacity_cc

    # ------------------------------------------------------------------ #
    #  Property                                                            #
    # ------------------------------------------------------------------ #

    @property
    def engine_capacity_cc(self) -> int:
        """Return the engine displacement in cc."""
        return self._engine_capacity_cc

    # ------------------------------------------------------------------ #
    #  Overridden Abstract Methods                                         #
    # ------------------------------------------------------------------ #

    def get_vehicle_type(self) -> str:
        """Return the vehicle type label."""
        return "Bike"

    def calculate_rental_cost(self, days: int) -> float:
        """
        Calculate the total rental cost for the bike.

        Applies a 5 % discount when the rental period is 5 days or more.

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
        """Return bike details including engine capacity and discount note."""
        base = super().display_details()
        discount_note = (
            f"5% discount for {self.LONG_RENTAL_THRESHOLD}+ day rentals"
        )
        return (
            f"{base}\n"
            f"  Engine         : {self._engine_capacity_cc} cc\n"
            f"  Pricing Note   : {discount_note}"
        )
