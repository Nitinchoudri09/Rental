"""
rental_system/__init__.py
=========================
Package initialisation — exposes the public API surface.
"""

from rental_system.models import Vehicle, Car, Bike, RentalRecord
from rental_system.factory import VehicleFactory
from rental_system.manager import RentalManager
from rental_system.cli import RentalCLI
from rental_system import exceptions

__all__ = [
    "Vehicle",
    "Car",
    "Bike",
    "RentalRecord",
    "VehicleFactory",
    "RentalManager",
    "RentalCLI",
    "exceptions",
]
