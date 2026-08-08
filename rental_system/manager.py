from __future__ import annotations

import json
import logging
import os
from datetime import date
from typing import Optional

from rental_system.exceptions import (
    InvalidRentalDurationError,
    VehicleAlreadyExistsError,
    VehicleNotAvailableError,
    VehicleNotFoundError,
    VehicleNotRentedError,
)
from rental_system.factory import VehicleFactory
from rental_system.models import RentalRecord, Vehicle

def _setup_logger(log_file: str = "rental.log") -> logging.Logger:

    logger = logging.getLogger("RentalSystem")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:          
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = _setup_logger()

class RentalManager:

    LOYALTY_DISCOUNT: float = 0.05   

    def __init__(self, data_file: str = "data/fleet.json") -> None:

        self._fleet: dict[str, Vehicle] = {}          
        self._renter_history: dict[str, int] = {}     
        self._data_file: str = data_file

    def add_vehicle(self, vehicle: Vehicle) -> None:

        if vehicle.vehicle_number in self._fleet:
            raise VehicleAlreadyExistsError(vehicle.vehicle_number)
        self._fleet[vehicle.vehicle_number] = vehicle
        logger.debug("Fleet: added %s (%s)", vehicle.vehicle_number, vehicle.brand)

    def remove_vehicle(self, vehicle_number: str) -> Vehicle:

        vehicle = self._get_or_raise(vehicle_number)
        if not vehicle.is_available:
            raise VehicleNotAvailableError(vehicle_number)
        del self._fleet[vehicle_number]
        logger.info("Fleet: removed %s", vehicle_number)
        return vehicle

    def rent_vehicle(
        self,
        vehicle_number: str,
        renter_name: str,
        days: int,
        start_date: Optional[str] = None,
    ) -> float:

        if days < 1:
            raise InvalidRentalDurationError(days)

        vehicle = self._get_or_raise(vehicle_number)

        if not vehicle.is_available:
            raise VehicleNotAvailableError(vehicle_number)

        gross = vehicle.calculate_rental(days)
        final = self._apply_loyalty(gross, renter_name)
        discount_applied = gross != final

        vehicle.is_available = False
        vehicle.current_rental = RentalRecord(
            renter_name=renter_name,
            start_date=start_date or date.today().isoformat(),
            planned_days=days,
        )

        self._renter_history[renter_name] = (
            self._renter_history.get(renter_name, 0) + 1
        )

        logger.info(
            "RENTED  | %s → %s | %d day(s) | Rs.%.2f%s",
            vehicle_number,
            renter_name,
            days,
            final,
            " [loyalty discount]" if discount_applied else "",
        )
        return final

    def return_vehicle(
        self,
        vehicle_number: str,
        actual_days: Optional[int] = None,
    ) -> dict:

        vehicle = self._get_or_raise(vehicle_number)

        if vehicle.is_available or vehicle.current_rental is None:
            raise VehicleNotRentedError(vehicle_number)

        record = vehicle.current_rental

        if actual_days is None:
            actual_days = max(record.days_elapsed(), 1)

        renter = record.renter_name
        planned = record.planned_days

        gross = vehicle.calculate_rental(actual_days)
        final = self._apply_loyalty(gross, renter)
        penalty = vehicle.late_penalty(actual_days, planned)
        total = final + penalty

        vehicle.is_available = True
        vehicle.current_rental = None

        logger.info(
            "RETURNED| %s ← %s | actual %d day(s) | "
            "rental Rs.%.2f | penalty Rs.%.2f | total Rs.%.2f",
            vehicle_number,
            renter,
            actual_days,
            final,
            penalty,
            total,
        )

        return {
            "vehicle_number": vehicle_number,
            "renter_name": renter,
            "planned_days": planned,
            "actual_days": actual_days,
            "rental_cost": final,
            "late_penalty": penalty,
            "total_cost": total,
        }

    def list_all(self) -> list[Vehicle]:

        return list(self._fleet.values())

    def list_available(self) -> list[Vehicle]:

        return [v for v in self._fleet.values() if v.is_available]

    def search_by_brand(self, brand: str) -> list[Vehicle]:

        key = brand.lower()
        return [v for v in self._fleet.values() if key in v.brand.lower()]

    def search_by_type(self, vehicle_type: str) -> list[Vehicle]:

        key = vehicle_type.lower()
        return [v for v in self._fleet.values() if v.type.lower() == key]

    def get_vehicle(self, vehicle_number: str) -> Vehicle:

        return self._get_or_raise(vehicle_number)

    def renter_history(self) -> dict[str, int]:

        return dict(self._renter_history)

    def fleet_size(self) -> int:

        return len(self._fleet)

    def save_fleet(self) -> None:

        os.makedirs(os.path.dirname(self._data_file) or ".", exist_ok=True)
        payload = {
            "fleet": [v.to_dict() for v in self._fleet.values()],
            "renter_history": self._renter_history,
        }
        with open(self._data_file, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, indent=2)
        logger.debug("Persistence: fleet saved to %s", self._data_file)

    def load_fleet(self) -> None:

        if not os.path.exists(self._data_file):
            logger.debug("Persistence: no data file found — starting fresh.")
            return

        with open(self._data_file, encoding="utf-8") as fp:
            payload = json.load(fp)

        self._fleet.clear()
        for raw in payload.get("fleet", []):
            try:
                vehicle = VehicleFactory.from_dict(raw)
                self._fleet[vehicle.vehicle_number] = vehicle
            except Exception as exc:
                logger.warning("Skipped corrupt fleet entry: %s", exc)

        self._renter_history = payload.get("renter_history", {})
        logger.info(
            "Persistence: loaded %d vehicle(s) from %s",
            len(self._fleet),
            self._data_file,
        )

    def _get_or_raise(self, vehicle_number: str) -> Vehicle:

        if vehicle_number not in self._fleet:
            raise VehicleNotFoundError(vehicle_number)
        return self._fleet[vehicle_number]

    def _apply_loyalty(self, amount: float, renter_name: str) -> float:

        if self._renter_history.get(renter_name, 0) > 0:
            return amount * (1 - self.LOYALTY_DISCOUNT)
        return amount
