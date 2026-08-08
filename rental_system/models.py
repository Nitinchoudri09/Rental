"""
models.py
=========
Vehicle domain models.

Hierarchy:
    Vehicle (ABC)
    ├── Car
    └── Bike

Any new vehicle type (e.g., Truck) should be added here and registered
with VehicleFactory — no other existing file needs to change.
"""

from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Rental record (stored inside each vehicle when rented)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RentalRecord:
    """Captures the state of an active rental."""

    renter_name: str
    start_date: str                         # ISO-8601 date string  YYYY-MM-DD
    planned_days: int

    @staticmethod
    def today_str() -> str:
        """Return today's date as an ISO-8601 string."""
        return datetime.date.today().isoformat()

    def days_elapsed(self) -> int:
        """Return the number of calendar days since the rental started."""
        start = datetime.date.fromisoformat(self.start_date)
        return (datetime.date.today() - start).days

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for JSON persistence."""
        return {
            "renter_name": self.renter_name,
            "start_date": self.start_date,
            "planned_days": self.planned_days,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RentalRecord":
        """Deserialize from a plain dict."""
        return cls(
            renter_name=data["renter_name"],
            start_date=data["start_date"],
            planned_days=data["planned_days"],
        )


# ─────────────────────────────────────────────────────────────────────────────
# Abstract base class
# ─────────────────────────────────────────────────────────────────────────────

class Vehicle(ABC):
    """
    Abstract base class for all rentable vehicles.

    Subclasses must implement:
        - calculate_rental(days)          → price computation
        - _type_label() → str             → human-readable type name
        - _extra_fields_dict() → dict     → subclass-specific fields for JSON
        - _display_extra()                → prints subclass-specific info

    Shared pricing rules applied here:
        - Long-term discount: 10 % when days > 7
        - Loyalty discount  : 5 % when the renter has rented before
          (applied by RentalManager, not here)
    """

    LONG_TERM_THRESHOLD: int = 7
    LONG_TERM_DISCOUNT: float = 0.10
    LATE_PENALTY_RATE: float = 0.20      # 20 % of daily rate per extra day

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
    ) -> None:
        """
        Initialize a vehicle.

        Args:
            vehicle_number: Unique registration identifier.
            brand:          Manufacturer / model name.
            base_price_per_day: Daily base rental price in Rs.
        """
        self.vehicle_number: str = vehicle_number
        self.brand: str = brand
        self.base_price_per_day: float = base_price_per_day
        self.is_available: bool = True
        self.current_rental: Optional[RentalRecord] = None

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def calculate_rental(self, days: int) -> float:
        """
        Compute the gross rental cost for *days* days (before loyalty discount).

        Subclasses apply their own surcharges and then call
        ``_apply_long_term_discount(total, days)``.

        Args:
            days: Number of rental days (must be >= 1).

        Returns:
            Total cost in Rs.
        """

    @abstractmethod
    def _type_label(self) -> str:
        """Return a short type string, e.g. 'Car' or 'Bike'."""

    @abstractmethod
    def _extra_fields_dict(self) -> dict[str, Any]:
        """Return subclass-specific fields for JSON serialization."""

    @abstractmethod
    def _display_extra(self) -> None:
        """Print subclass-specific attributes."""

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _apply_long_term_discount(self, total: float, days: int) -> float:
        """
        Apply a 10 % discount when rental days exceed the long-term threshold.

        Args:
            total: Gross cost before discount.
            days:  Number of rental days.

        Returns:
            Discounted total.
        """
        if days > self.LONG_TERM_THRESHOLD:
            total *= 1 - self.LONG_TERM_DISCOUNT
        return total

    def late_penalty(self, actual_days: int, planned_days: int) -> float:
        """
        Compute the late-return penalty for days returned beyond the plan.

        Args:
            actual_days:  Actual number of days the vehicle was kept.
            planned_days: Originally planned rental duration.

        Returns:
            Penalty amount in Rs. (0.0 if returned on time or early).
        """
        extra = max(0, actual_days - planned_days)
        daily_rate = self.base_price_per_day  # use base rate for penalty
        return extra * daily_rate * self.LATE_PENALTY_RATE

    # ── Display ───────────────────────────────────────────────────────────────

    def display_details(self) -> None:
        """Print a formatted summary of this vehicle."""
        status = "Available" if self.is_available else "Rented"
        print(f"  [{self._type_label()}] {self.vehicle_number} — {self.brand}")
        print(f"    Base Price/Day : Rs.{self.base_price_per_day:.2f}")
        print(f"    Status         : {status}")
        self._display_extra()
        if self.current_rental:
            r = self.current_rental
            print(
                f"    Rented by      : {r.renter_name} "
                f"(from {r.start_date}, {r.planned_days} days planned)"
            )

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize this vehicle to a JSON-compatible dict."""
        return {
            "type": self._type_label(),
            "vehicle_number": self.vehicle_number,
            "brand": self.brand,
            "base_price_per_day": self.base_price_per_day,
            "is_available": self.is_available,
            "current_rental": (
                self.current_rental.to_dict() if self.current_rental else None
            ),
            **self._extra_fields_dict(),
        }

    @property
    def type(self) -> str:
        """Alias for _type_label(), used by the factory."""
        return self._type_label()


# ─────────────────────────────────────────────────────────────────────────────
# Car
# ─────────────────────────────────────────────────────────────────────────────

class Car(Vehicle):
    """
    A passenger car.

    Pricing surcharge:
        Rs.100 / day for each seat beyond 4 (the standard).

    Attributes:
        seats: Total passenger seat count including the driver.
    """

    EXTRA_SEAT_CHARGE: float = 100.0
    STANDARD_SEATS: int = 4

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
        seats: int,
    ) -> None:
        """
        Initialize a Car.

        Args:
            vehicle_number:     Unique registration ID.
            brand:              Manufacturer / model name.
            base_price_per_day: Base daily rental price.
            seats:              Total seat count.
        """
        super().__init__(vehicle_number, brand, base_price_per_day)
        self.seats: int = seats

    # ── Pricing ───────────────────────────────────────────────────────────────

    def _seat_surcharge_per_day(self) -> float:
        """Return the daily surcharge due to extra seats."""
        extra = max(0, self.seats - self.STANDARD_SEATS)
        return extra * self.EXTRA_SEAT_CHARGE

    def calculate_rental(self, days: int) -> float:
        """
        Compute gross rental cost including seat surcharge and long-term discount.

        Formula:
            total = (base_price + seat_surcharge) * days
            if days > 7: total *= 0.90

        Args:
            days: Rental duration in days.

        Returns:
            Total cost in Rs.
        """
        daily = self.base_price_per_day + self._seat_surcharge_per_day()
        total = daily * days
        return self._apply_long_term_discount(total, days)

    # ── Abstract implementations ──────────────────────────────────────────────

    def _type_label(self) -> str:
        return "Car"

    def _extra_fields_dict(self) -> dict[str, Any]:
        return {"seats": self.seats}

    def _display_extra(self) -> None:
        surcharge = self._seat_surcharge_per_day()
        extra_note = (
            f"  (+Rs.{surcharge:.0f}/day for "
            f"{self.seats - self.STANDARD_SEATS} extra seat(s))"
            if surcharge > 0
            else ""
        )
        print(f"    Seats          : {self.seats}{extra_note}")


# ─────────────────────────────────────────────────────────────────────────────
# Bike
# ─────────────────────────────────────────────────────────────────────────────

class Bike(Vehicle):
    """
    A motorcycle or scooter.

    Pricing surcharge:
        Rs.50 / day if engine displacement exceeds 150 cc.

    Attributes:
        engine_cc: Engine displacement in cubic centimetres.
    """

    HIGH_CC_THRESHOLD: int = 150
    HIGH_CC_SURCHARGE: float = 50.0

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
        engine_cc: int,
    ) -> None:
        """
        Initialize a Bike.

        Args:
            vehicle_number:     Unique registration ID.
            brand:              Manufacturer / model name.
            base_price_per_day: Base daily rental price.
            engine_cc:          Engine displacement in cc.
        """
        super().__init__(vehicle_number, brand, base_price_per_day)
        self.engine_cc: int = engine_cc

    # ── Pricing ───────────────────────────────────────────────────────────────

    def _cc_surcharge_per_day(self) -> float:
        """Return the daily surcharge for high-displacement engines."""
        return self.HIGH_CC_SURCHARGE if self.engine_cc > self.HIGH_CC_THRESHOLD else 0.0

    def calculate_rental(self, days: int) -> float:
        """
        Compute gross rental cost including cc surcharge and long-term discount.

        Formula:
            total = (base_price + cc_surcharge) * days
            if days > 7: total *= 0.90

        Args:
            days: Rental duration in days.

        Returns:
            Total cost in Rs.
        """
        daily = self.base_price_per_day + self._cc_surcharge_per_day()
        total = daily * days
        return self._apply_long_term_discount(total, days)

    # ── Abstract implementations ──────────────────────────────────────────────

    def _type_label(self) -> str:
        return "Bike"

    def _extra_fields_dict(self) -> dict[str, Any]:
        return {"engine_cc": self.engine_cc}

    def _display_extra(self) -> None:
        surcharge = self._cc_surcharge_per_day()
        extra_note = (
            f"  (+Rs.{surcharge:.0f}/day high-cc surcharge)"
            if surcharge > 0
            else ""
        )
        print(f"    Engine         : {self.engine_cc} cc{extra_note}")
