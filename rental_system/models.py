from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class RentalRecord:

    renter_name: str
    start_date: str                         
    planned_days: int

    @staticmethod
    def today_str() -> str:

        return datetime.date.today().isoformat()

    def days_elapsed(self) -> int:

        start = datetime.date.fromisoformat(self.start_date)
        return (datetime.date.today() - start).days

    def to_dict(self) -> dict[str, Any]:

        return {
            "renter_name": self.renter_name,
            "start_date": self.start_date,
            "planned_days": self.planned_days,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RentalRecord":

        return cls(
            renter_name=data["renter_name"],
            start_date=data["start_date"],
            planned_days=data["planned_days"],
        )

class Vehicle(ABC):

    LONG_TERM_THRESHOLD: int = 7
    LONG_TERM_DISCOUNT: float = 0.10
    LATE_PENALTY_RATE: float = 0.20      

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
    ) -> None:

        self.vehicle_number: str = vehicle_number
        self.brand: str = brand
        self.base_price_per_day: float = base_price_per_day
        self.is_available: bool = True
        self.current_rental: Optional[RentalRecord] = None

    @abstractmethod
    def calculate_rental(self, days: int) -> float:

    @abstractmethod
    def _type_label(self) -> str:

    @abstractmethod
    def _extra_fields_dict(self) -> dict[str, Any]:

    @abstractmethod
    def _display_extra(self) -> None:

    def _apply_long_term_discount(self, total: float, days: int) -> float:

        if days > self.LONG_TERM_THRESHOLD:
            total *= 1 - self.LONG_TERM_DISCOUNT
        return total

    def late_penalty(self, actual_days: int, planned_days: int) -> float:

        extra = max(0, actual_days - planned_days)
        daily_rate = self.base_price_per_day  
        return extra * daily_rate * self.LATE_PENALTY_RATE

    def display_details(self) -> None:

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

    def to_dict(self) -> dict[str, Any]:

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

        return self._type_label()

class Car(Vehicle):

    EXTRA_SEAT_CHARGE: float = 100.0
    STANDARD_SEATS: int = 4

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
        seats: int,
    ) -> None:

        super().__init__(vehicle_number, brand, base_price_per_day)
        self.seats: int = seats

    def _seat_surcharge_per_day(self) -> float:

        extra = max(0, self.seats - self.STANDARD_SEATS)
        return extra * self.EXTRA_SEAT_CHARGE

    def calculate_rental(self, days: int) -> float:

        daily = self.base_price_per_day + self._seat_surcharge_per_day()
        total = daily * days
        return self._apply_long_term_discount(total, days)

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

class Bike(Vehicle):

    HIGH_CC_THRESHOLD: int = 150
    HIGH_CC_SURCHARGE: float = 50.0

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
        engine_cc: int,
    ) -> None:

        super().__init__(vehicle_number, brand, base_price_per_day)
        self.engine_cc: int = engine_cc

    def _cc_surcharge_per_day(self) -> float:

        return self.HIGH_CC_SURCHARGE if self.engine_cc > self.HIGH_CC_THRESHOLD else 0.0

    def calculate_rental(self, days: int) -> float:

        daily = self.base_price_per_day + self._cc_surcharge_per_day()
        total = daily * days
        return self._apply_long_term_discount(total, days)

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
