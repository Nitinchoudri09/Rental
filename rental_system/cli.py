"""
cli.py
======
RentalCLI — interactive text-based menu for the Vehicle Rental System.

Menu options:
    1. View all vehicles
    2. View available vehicles
    3. Search vehicles
    4. Add vehicle
    5. Rent a vehicle
    6. Return a vehicle
    7. View renter history
    8. Remove vehicle
    9. Save & Exit
"""

from __future__ import annotations

from typing import Optional

from rental_system.exceptions import (
    InvalidRentalDurationError,
    UnknownVehicleTypeError,
    VehicleAlreadyExistsError,
    VehicleNotAvailableError,
    VehicleNotFoundError,
    VehicleNotRentedError,
)
from rental_system.factory import VehicleFactory
from rental_system.manager import RentalManager
from rental_system.models import Vehicle

DIVIDER = "=" * 56
THIN    = "-" * 56


def _header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def _prompt(msg: str, default: str = "") -> str:
    """Prompt the user and strip whitespace. Return default if blank."""
    raw = input(f"  {msg}").strip()
    return raw if raw else default


def _prompt_int(msg: str, min_val: int = 1, max_val: int = 9999) -> Optional[int]:
    """Prompt for an integer within [min_val, max_val]. Returns None on error."""
    raw = _prompt(msg)
    try:
        val = int(raw)
        if val < min_val or val > max_val:
            print(f"  [!] Please enter a number between {min_val} and {max_val}.")
            return None
        return val
    except ValueError:
        print("  [!] Invalid number.")
        return None


def _display_list(vehicles: list[Vehicle], label: str) -> None:
    """Print a list of vehicles with a label, or a 'none found' message."""
    if not vehicles:
        print(f"\n  (No {label} found.)")
        return
    print(f"\n  {len(vehicles)} {label}:\n")
    for v in vehicles:
        v.display_details()
        print(THIN)


class RentalCLI:
    """
    Text-based CLI that wraps RentalManager.

    All user input is validated before being forwarded to the manager.
    Exceptions raised by the manager are caught and shown as friendly messages.
    """

    MENU = (
        "\n  VEHICLE RENTAL SYSTEM",
        DIVIDER,
        "  1. View all vehicles",
        "  2. View available vehicles",
        "  3. Search vehicles",
        "  4. Add a vehicle",
        "  5. Rent a vehicle",
        "  6. Return a vehicle",
        "  7. View renter history",
        "  8. Remove a vehicle",
        "  9. Save & Exit",
        DIVIDER,
    )

    def __init__(self, manager: RentalManager) -> None:
        """
        Initialise the CLI with a RentalManager instance.

        Args:
            manager: The RentalManager to delegate all operations to.
        """
        self._mgr = manager

    # ── Public entry point ────────────────────────────────────────────────────

    def run(self) -> None:
        """Start the interactive menu loop. Exits when user chooses option 9."""
        print("\n  Welcome to the Vehicle Rental System!")
        while True:
            print("\n".join(self.MENU))
            choice = _prompt("Enter choice [1-9]: ")
            self._dispatch(choice)

    # ── Dispatcher ────────────────────────────────────────────────────────────

    def _dispatch(self, choice: str) -> None:
        """Route a menu choice to the appropriate handler."""
        handlers = {
            "1": self._view_all,
            "2": self._view_available,
            "3": self._search,
            "4": self._add_vehicle,
            "5": self._rent,
            "6": self._return,
            "7": self._renter_history,
            "8": self._remove_vehicle,
            "9": self._save_and_exit,
        }
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            print("  [!] Invalid choice. Please enter a number 1–9.")

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _view_all(self) -> None:
        """Display every vehicle in the fleet."""
        _header("ALL VEHICLES")
        _display_list(self._mgr.list_all(), "vehicle(s)")

    def _view_available(self) -> None:
        """Display only vehicles available for rent."""
        _header("AVAILABLE VEHICLES")
        _display_list(self._mgr.list_available(), "available vehicle(s)")

    def _search(self) -> None:
        """Search vehicles by brand keyword or type."""
        _header("SEARCH VEHICLES")
        print("  Search by:")
        print("    B — Brand keyword")
        print("    T — Vehicle type  (Car / Bike / ...)")
        mode = _prompt("Choice [B/T]: ").upper()

        if mode == "B":
            keyword = _prompt("Brand keyword: ")
            if not keyword:
                print("  [!] Keyword cannot be empty.")
                return
            results = self._mgr.search_by_brand(keyword)
            _display_list(results, f"match(es) for brand '{keyword}'")

        elif mode == "T":
            types = ", ".join(t.capitalize() for t in VehicleFactory.registered_types())
            vtype = _prompt(f"Vehicle type ({types}): ")
            if not vtype:
                print("  [!] Type cannot be empty.")
                return
            results = self._mgr.search_by_type(vtype)
            _display_list(results, f"'{vtype}' vehicle(s)")

        else:
            print("  [!] Invalid search mode.")

    def _add_vehicle(self) -> None:
        """Interactively add a new vehicle to the fleet."""
        _header("ADD VEHICLE")
        types = ", ".join(t.capitalize() for t in VehicleFactory.registered_types())
        vtype = _prompt(f"Vehicle type ({types}): ")
        if not vtype:
            print("  [!] Type cannot be empty.")
            return

        num    = _prompt("Vehicle number (e.g. KA-01-AB-1234): ").upper()
        brand  = _prompt("Brand: ")
        price  = _prompt("Base price per day (Rs.): ")

        if not num or not brand or not price:
            print("  [!] All fields are required.")
            return

        try:
            base_price = float(price)
            if base_price <= 0:
                raise ValueError
        except ValueError:
            print("  [!] Invalid price. Enter a positive number.")
            return

        kwargs: dict = dict(
            vehicle_number=num,
            brand=brand,
            base_price_per_day=base_price,
        )

        # Collect type-specific fields
        vtype_lower = vtype.lower()
        if vtype_lower == "car":
            seats = _prompt_int("Number of seats: ", 1, 50)
            if seats is None:
                return
            kwargs["seats"] = seats

        elif vtype_lower == "bike":
            cc = _prompt_int("Engine cc: ", 1, 5000)
            if cc is None:
                return
            kwargs["engine_cc"] = cc

        try:
            vehicle = VehicleFactory.create(vtype, **kwargs)
            self._mgr.add_vehicle(vehicle)
            print(f"\n  [✓] {vtype.capitalize()} '{num}' added successfully.")
        except UnknownVehicleTypeError as e:
            print(f"  [!] {e}")
        except VehicleAlreadyExistsError as e:
            print(f"  [!] {e}")

    def _rent(self) -> None:
        """Rent a vehicle to a customer."""
        _header("RENT A VEHICLE")
        num   = _prompt("Vehicle number: ").upper()
        name  = _prompt("Renter name: ")
        days  = _prompt_int("Number of days: ", 1)

        if not num or not name or days is None:
            print("  [!] All fields are required.")
            return

        try:
            cost = self._mgr.rent_vehicle(num, name, days)
            print(f"\n  [✓] Vehicle '{num}' rented to {name} for {days} day(s).")
            print(f"      Estimated cost: Rs.{cost:,.2f}")
        except VehicleNotFoundError as e:
            print(f"  [!] {e}")
        except VehicleNotAvailableError as e:
            print(f"  [!] {e}")
        except InvalidRentalDurationError as e:
            print(f"  [!] {e}")

    def _return(self) -> None:
        """Process a vehicle return."""
        _header("RETURN A VEHICLE")
        num = _prompt("Vehicle number: ").upper()
        if not num:
            print("  [!] Vehicle number required.")
            return

        use_elapsed = _prompt("Use elapsed days from start date? [Y/n]: ").lower()
        actual_days: Optional[int] = None

        if use_elapsed == "n":
            actual_days = _prompt_int("Actual number of days kept: ", 1)
            if actual_days is None:
                return

        try:
            summary = self._mgr.return_vehicle(num, actual_days)
            print(f"\n  [✓] Vehicle '{num}' returned successfully.")
            print(f"      Renter        : {summary['renter_name']}")
            print(f"      Planned days  : {summary['planned_days']}")
            print(f"      Actual days   : {summary['actual_days']}")
            print(f"      Rental cost   : Rs.{summary['rental_cost']:,.2f}")
            if summary["late_penalty"] > 0:
                print(f"      Late penalty  : Rs.{summary['late_penalty']:,.2f}")
            print(f"      TOTAL         : Rs.{summary['total_cost']:,.2f}")
        except VehicleNotFoundError as e:
            print(f"  [!] {e}")
        except VehicleNotRentedError as e:
            print(f"  [!] {e}")

    def _renter_history(self) -> None:
        """Display all renters and their rental counts."""
        _header("RENTER HISTORY")
        history = self._mgr.renter_history()
        if not history:
            print("  (No rental history yet.)")
            return
        print(f"  {'Renter':<30} {'Rentals':>7}")
        print(THIN)
        for name, count in sorted(history.items(), key=lambda x: -x[1]):
            loyalty = "  [loyalty eligible]" if count > 0 else ""
            print(f"  {name:<30} {count:>7}{loyalty}")

    def _remove_vehicle(self) -> None:
        """Remove a vehicle from the fleet."""
        _header("REMOVE VEHICLE")
        num = _prompt("Vehicle number to remove: ").upper()
        if not num:
            print("  [!] Vehicle number required.")
            return
        confirm = _prompt(f"Remove '{num}'? This cannot be undone. [yes/N]: ").lower()
        if confirm != "yes":
            print("  Cancelled.")
            return
        try:
            self._mgr.remove_vehicle(num)
            print(f"  [✓] Vehicle '{num}' removed from fleet.")
        except VehicleNotFoundError as e:
            print(f"  [!] {e}")
        except VehicleNotAvailableError:
            print(f"  [!] Cannot remove '{num}' — it is currently rented.")

    def _save_and_exit(self) -> None:
        """Save the fleet to disk and exit the program."""
        self._mgr.save_fleet()
        print("\n  Fleet saved. Goodbye!\n")
        raise SystemExit(0)
