"""
Vehicle Rental System
=====================
A polymorphic OOP-based rental system supporting Cars, Bikes,
and any future vehicle types (e.g., Truck) with minimal changes.
"""

from abc import ABC, abstractmethod


# ─────────────────────────────────────────────
# Abstract Base Class
# ─────────────────────────────────────────────

class Vehicle(ABC):
    """Abstract base class representing a rentable vehicle."""

    LONG_TERM_DAYS: int = 7           # Threshold for long-term discount
    LONG_TERM_DISCOUNT: float = 0.10  # 10% discount

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
    ) -> None:
        self.vehicle_number: str = vehicle_number
        self.brand: str = brand
        self.base_price_per_day: float = base_price_per_day

    @abstractmethod
    def calculate_rental(self, days: int) -> float:
        """
        Calculate the total rental cost for the given number of days.
        Subclasses must override this method.
        """

    def _apply_long_term_discount(self, total: float, days: int) -> float:
        """Apply a 10% discount when rental exceeds 7 days."""
        if days > self.LONG_TERM_DAYS:
            total *= (1 - self.LONG_TERM_DISCOUNT)
        return total

    def display_details(self) -> None:
        """Print common vehicle information."""
        print(f"  Vehicle Number : {self.vehicle_number}")
        print(f"  Brand          : {self.brand}")
        print(f"  Base Price/Day : Rs.{self.base_price_per_day:.2f}")


# ─────────────────────────────────────────────
# Subclass: Car
# ─────────────────────────────────────────────

class Car(Vehicle):
    """
    A car with a configurable number of seats.
    Extra charge: Rs.100/day for each seat beyond 4.
    """

    EXTRA_SEAT_CHARGE: float = 100.0  # Rs. per extra seat per day
    STANDARD_SEATS: int = 4           # Seats included in base price

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
        seats: int,
    ) -> None:
        super().__init__(vehicle_number, brand, base_price_per_day)
        self.seats: int = seats

    # ── helpers ───────────────────────────────

    def _extra_seat_charge_per_day(self) -> float:
        """Return the additional daily charge due to extra seats."""
        extra_seats = max(0, self.seats - self.STANDARD_SEATS)
        return extra_seats * self.EXTRA_SEAT_CHARGE

    # ── core method ───────────────────────────

    def calculate_rental(self, days: int) -> float:
        """Total = (base + seat surcharge) x days, with long-term discount."""
        daily_rate = self.base_price_per_day + self._extra_seat_charge_per_day()
        total = daily_rate * days
        return self._apply_long_term_discount(total, days)

    # ── display ───────────────────────────────

    def display_details(self) -> None:
        """Print Car-specific details in addition to common info."""
        super().display_details()
        extra = self._extra_seat_charge_per_day()
        extra_info = (
            f"  (+Rs.{extra:.0f}/day surcharge for "
            f"{self.seats - self.STANDARD_SEATS} extra seat(s))"
            if extra > 0
            else ""
        )
        print(f"  Seats          : {self.seats}{extra_info}")


# ─────────────────────────────────────────────
# Subclass: Bike
# ─────────────────────────────────────────────

class Bike(Vehicle):
    """
    A bike with engine capacity in cc.
    Extra charge: Rs.50/day if engine_cc > 150.
    """

    HIGH_CC_THRESHOLD: int = 150     # cc limit before surcharge
    HIGH_CC_SURCHARGE: float = 50.0  # Rs. per day

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
        engine_cc: int,
    ) -> None:
        super().__init__(vehicle_number, brand, base_price_per_day)
        self.engine_cc: int = engine_cc

    # ── helpers ───────────────────────────────

    def _high_cc_surcharge_per_day(self) -> float:
        """Return the daily surcharge for high-displacement engines."""
        return self.HIGH_CC_SURCHARGE if self.engine_cc > self.HIGH_CC_THRESHOLD else 0.0

    # ── core method ───────────────────────────

    def calculate_rental(self, days: int) -> float:
        """Total = (base + cc surcharge) x days, with long-term discount."""
        daily_rate = self.base_price_per_day + self._high_cc_surcharge_per_day()
        total = daily_rate * days
        return self._apply_long_term_discount(total, days)

    # ── display ───────────────────────────────

    def display_details(self) -> None:
        """Print Bike-specific details in addition to common info."""
        super().display_details()
        surcharge = self._high_cc_surcharge_per_day()
        surcharge_info = (
            f"  (+Rs.{surcharge:.0f}/day high-cc surcharge)"
            if surcharge > 0
            else ""
        )
        print(f"  Engine         : {self.engine_cc} cc{surcharge_info}")


# ─────────────────────────────────────────────
# Polymorphic rental function
# ─────────────────────────────────────────────

def rent_vehicle(vehicle: Vehicle, days: int) -> None:
    """
    Works with ANY Vehicle subtype.
    Prints the vehicle's details and the computed rental cost.
    """
    total = vehicle.calculate_rental(days)
    discount_applied = days > Vehicle.LONG_TERM_DAYS

    print("=" * 54)
    print(f"  {type(vehicle).__name__} Rental  |  {days} Day(s)")
    print("=" * 54)
    vehicle.display_details()
    print(f"  Rental Days    : {days}")
    if discount_applied:
        print(f"  Discount       : {Vehicle.LONG_TERM_DISCOUNT:.0%} long-term discount applied!")
    print(f"  Total Cost     : Rs.{total:,.2f}")
    print()


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

if __name__ == "__main__":

    # ── Fleet definition ──────────────────────

    fleet: list[Vehicle] = [
        # Cars
        Car(
            vehicle_number="KA-01-AB-1234",
            brand="Maruti Swift",
            base_price_per_day=800.0,
            seats=5,    # 1 extra seat  → +Rs.100/day
        ),
        Car(
            vehicle_number="MH-12-CD-5678",
            brand="Toyota Innova",
            base_price_per_day=1500.0,
            seats=8,    # 4 extra seats → +Rs.400/day
        ),
        # Bikes
        Bike(
            vehicle_number="DL-05-EF-9012",
            brand="Honda Activa",
            base_price_per_day=200.0,
            engine_cc=110,   # <= 150 cc  → no surcharge
        ),
        Bike(
            vehicle_number="TN-09-GH-3456",
            brand="KTM Duke 200",
            base_price_per_day=400.0,
            engine_cc=200,   # > 150 cc   → +Rs.50/day
        ),
    ]

    # ── Rental scenarios ──────────────────────
    # (vehicle, days) — includes short-term and long-term rentals

    rental_plan: list[tuple[Vehicle, int]] = [
        (fleet[0], 3),   # Maruti Swift  — 3 days   (no discount)
        (fleet[1], 10),  # Toyota Innova — 10 days  (10% discount)
        (fleet[2], 5),   # Honda Activa  — 5 days   (no discount)
        (fleet[3], 14),  # KTM Duke 200  — 14 days  (10% discount)
    ]

    print()
    print("=" * 54)
    print("        VEHICLE RENTAL SYSTEM")
    print("=" * 54)
    print()

    for vehicle, days in rental_plan:
        rent_vehicle(vehicle, days)
