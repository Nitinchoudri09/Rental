"""
manager.py
==========
RentalManager — the central coordinator of the rental system.

Responsibilities:
    - Maintain the vehicle fleet (add / remove / search)
    - Rent and return vehicles with full validation
    - Track renter history for loyalty discounts
    - Persist fleet state to / from a JSON file
    - Log every transaction using Python's logging module
"""

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


# ─────────────────────────────────────────────────────────────────────────────
# Logging configuration
# ─────────────────────────────────────────────────────────────────────────────

def _setup_logger(log_file: str = "rental.log") -> logging.Logger:
    """
    Configure and return the module-level logger.

    Logs go to both a rotating file and the console (INFO+).

    Args:
        log_file: Path to the log file.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger("RentalSystem")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:          # avoid duplicate handlers on reimport
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler — DEBUG and above
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Console handler — INFO and above
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logger = _setup_logger()


# ─────────────────────────────────────────────────────────────────────────────
# RentalManager
# ─────────────────────────────────────────────────────────────────────────────

class RentalManager:
    """
    Manages the full lifecycle of vehicle rentals.

    Features:
        - Fleet CRUD            : add_vehicle / remove_vehicle
        - Rental workflow       : rent_vehicle / return_vehicle
        - Queries               : list_all / list_available / search_by_brand /
                                  search_by_type / get_vehicle
        - Loyalty discounts     : 5 % off for returning renters
        - Persistence           : save_fleet / load_fleet (JSON)
        - Logging               : every rental/return is logged to file + console
    """

    LOYALTY_DISCOUNT: float = 0.05   # 5 % for returning renters

    def __init__(self, data_file: str = "data/fleet.json") -> None:
        """
        Initialise the manager.

        Args:
            data_file: Path to the JSON persistence file.
        """
        self._fleet: dict[str, Vehicle] = {}          # vehicle_number → Vehicle
        self._renter_history: dict[str, int] = {}     # renter_name → rental count
        self._data_file: str = data_file

    # ── Fleet management ──────────────────────────────────────────────────────

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """
        Add a vehicle to the fleet.

        Args:
            vehicle: Any Vehicle instance.

        Raises:
            VehicleAlreadyExistsError: If vehicle_number is already in fleet.
        """
        if vehicle.vehicle_number in self._fleet:
            raise VehicleAlreadyExistsError(vehicle.vehicle_number)
        self._fleet[vehicle.vehicle_number] = vehicle
        logger.debug("Fleet: added %s (%s)", vehicle.vehicle_number, vehicle.brand)

    def remove_vehicle(self, vehicle_number: str) -> Vehicle:
        """
        Remove and return a vehicle from the fleet.

        Args:
            vehicle_number: Registration ID.

        Returns:
            The removed Vehicle instance.

        Raises:
            VehicleNotFoundError:     If ID not in fleet.
            VehicleNotAvailableError: If vehicle is currently rented.
        """
        vehicle = self._get_or_raise(vehicle_number)
        if not vehicle.is_available:
            raise VehicleNotAvailableError(vehicle_number)
        del self._fleet[vehicle_number]
        logger.info("Fleet: removed %s", vehicle_number)
        return vehicle

    # ── Rental workflow ───────────────────────────────────────────────────────

    def rent_vehicle(
        self,
        vehicle_number: str,
        renter_name: str,
        days: int,
        start_date: Optional[str] = None,
    ) -> float:
        """
        Rent a vehicle to a customer.

        Applies:
            - Seat / cc surcharges (inside Vehicle.calculate_rental)
            - Long-term discount if days > 7
            - Loyalty discount (5 %) if renter has rented before

        Args:
            vehicle_number: Registration ID.
            renter_name:    Customer name (used for history tracking).
            days:           Planned rental duration.
            start_date:     ISO date string; defaults to today.

        Returns:
            Estimated total rental cost in Rs.

        Raises:
            VehicleNotFoundError:       Vehicle ID not in fleet.
            VehicleNotAvailableError:   Vehicle already rented.
            InvalidRentalDurationError: days < 1.
        """
        if days < 1:
            raise InvalidRentalDurationError(days)

        vehicle = self._get_or_raise(vehicle_number)

        if not vehicle.is_available:
            raise VehicleNotAvailableError(vehicle_number)

        # ── Compute cost ──────────────────────────────────────────────────────
        gross = vehicle.calculate_rental(days)
        final = self._apply_loyalty(gross, renter_name)
        discount_applied = gross != final

        # ── Mark rented ───────────────────────────────────────────────────────
        vehicle.is_available = False
        vehicle.current_rental = RentalRecord(
            renter_name=renter_name,
            start_date=start_date or date.today().isoformat(),
            planned_days=days,
        )

        # ── Update history ────────────────────────────────────────────────────
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
        """
        Process the return of a rented vehicle.

        Calculates:
            - Final rental cost (re-computed from actual days)
            - Late penalty if actual_days > planned_days

        Args:
            vehicle_number: Registration ID.
            actual_days:    Actual days kept; defaults to days_elapsed()
                            computed from the start date.

        Returns:
            A summary dict with keys:
                vehicle_number, renter_name, planned_days, actual_days,
                rental_cost, late_penalty, total_cost.

        Raises:
            VehicleNotFoundError:  Vehicle ID not in fleet.
            VehicleNotRentedError: Vehicle not currently rented.
        """
        vehicle = self._get_or_raise(vehicle_number)

        if vehicle.is_available or vehicle.current_rental is None:
            raise VehicleNotRentedError(vehicle_number)

        record = vehicle.current_rental

        # Resolve actual days
        if actual_days is None:
            actual_days = max(record.days_elapsed(), 1)

        renter = record.renter_name
        planned = record.planned_days

        gross = vehicle.calculate_rental(actual_days)
        final = self._apply_loyalty(gross, renter)
        penalty = vehicle.late_penalty(actual_days, planned)
        total = final + penalty

        # ── Mark available ────────────────────────────────────────────────────
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

    # ── Queries ───────────────────────────────────────────────────────────────

    def list_all(self) -> list[Vehicle]:
        """Return all vehicles in the fleet."""
        return list(self._fleet.values())

    def list_available(self) -> list[Vehicle]:
        """Return only vehicles currently available for rent."""
        return [v for v in self._fleet.values() if v.is_available]

    def search_by_brand(self, brand: str) -> list[Vehicle]:
        """
        Search vehicles by brand name (case-insensitive, partial match).

        Args:
            brand: Brand keyword to search.

        Returns:
            List of matching vehicles.
        """
        key = brand.lower()
        return [v for v in self._fleet.values() if key in v.brand.lower()]

    def search_by_type(self, vehicle_type: str) -> list[Vehicle]:
        """
        Filter vehicles by type (e.g., 'Car', 'Bike').

        Args:
            vehicle_type: Type label (case-insensitive).

        Returns:
            List of matching vehicles.
        """
        key = vehicle_type.lower()
        return [v for v in self._fleet.values() if v.type.lower() == key]

    def get_vehicle(self, vehicle_number: str) -> Vehicle:
        """
        Retrieve a vehicle by its registration number.

        Args:
            vehicle_number: Registration ID.

        Returns:
            The Vehicle instance.

        Raises:
            VehicleNotFoundError: If not found.
        """
        return self._get_or_raise(vehicle_number)

    def renter_history(self) -> dict[str, int]:
        """Return the renter history dict (renter_name → rental count)."""
        return dict(self._renter_history)

    def fleet_size(self) -> int:
        """Return the total number of vehicles in the fleet."""
        return len(self._fleet)

    # ── Persistence ───────────────────────────────────────────────────────────

    def save_fleet(self) -> None:
        """
        Persist fleet and renter history to the JSON data file.

        Creates the data directory if it doesn't exist.
        """
        os.makedirs(os.path.dirname(self._data_file) or ".", exist_ok=True)
        payload = {
            "fleet": [v.to_dict() for v in self._fleet.values()],
            "renter_history": self._renter_history,
        }
        with open(self._data_file, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, indent=2)
        logger.debug("Persistence: fleet saved to %s", self._data_file)

    def load_fleet(self) -> None:
        """
        Load fleet and renter history from the JSON data file.

        Silently skips if the file does not yet exist (first run).
        """
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

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_or_raise(self, vehicle_number: str) -> Vehicle:
        """
        Fetch a vehicle or raise VehicleNotFoundError.

        Args:
            vehicle_number: Registration ID.

        Returns:
            The Vehicle instance.

        Raises:
            VehicleNotFoundError: If not in fleet.
        """
        if vehicle_number not in self._fleet:
            raise VehicleNotFoundError(vehicle_number)
        return self._fleet[vehicle_number]

    def _apply_loyalty(self, amount: float, renter_name: str) -> float:
        """
        Apply a 5 % loyalty discount for returning customers.

        A renter qualifies if they appear in the rental history
        (i.e., they have rented at least once before).

        Args:
            amount:      Gross rental cost.
            renter_name: Customer's name.

        Returns:
            Discounted amount.
        """
        if self._renter_history.get(renter_name, 0) > 0:
            return amount * (1 - self.LOYALTY_DISCOUNT)
        return amount
