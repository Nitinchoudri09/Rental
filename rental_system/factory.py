"""
factory.py
==========
VehicleFactory — creates vehicle instances from a type string.

Open/Closed Principle:
    To add a new vehicle type (e.g., Truck), simply:
        1. Define the Truck class in models.py
        2. Call VehicleFactory.register("Truck", Truck) anywhere at startup
    No existing code needs to change.
"""

from __future__ import annotations

from typing import Any, Type

from rental_system.models import Vehicle
from rental_system.exceptions import UnknownVehicleTypeError


class VehicleFactory:
    """
    Factory class that decouples vehicle creation from the rest of the system.

    Usage:
        vehicle = VehicleFactory.create("Car", vehicle_number="KA-01", ...)
        vehicle = VehicleFactory.create("Bike", vehicle_number="DL-05", ...)

    Registering a new type:
        VehicleFactory.register("Truck", Truck)
    """

    # Registry maps type-string → Vehicle subclass
    _registry: dict[str, Type[Vehicle]] = {}

    @classmethod
    def register(cls, type_name: str, vehicle_class: Type[Vehicle]) -> None:
        """
        Register a new vehicle subclass under a given type string.

        Args:
            type_name:     Case-insensitive label (e.g., 'Car', 'Bike').
            vehicle_class: The Vehicle subclass to instantiate.
        """
        cls._registry[type_name.lower()] = vehicle_class

    @classmethod
    def create(cls, type_name: str, **kwargs: Any) -> Vehicle:
        """
        Instantiate the correct Vehicle subclass.

        Args:
            type_name: Type label (e.g., 'Car', 'Bike'). Case-insensitive.
            **kwargs:  Constructor arguments forwarded to the subclass.

        Returns:
            A fully constructed Vehicle instance.

        Raises:
            UnknownVehicleTypeError: If type_name is not in the registry.
        """
        key = type_name.lower()
        if key not in cls._registry:
            raise UnknownVehicleTypeError(type_name)
        return cls._registry[key](**kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Vehicle:
        """
        Reconstruct a Vehicle from a serialized dict (used by persistence layer).

        The dict must contain a 'type' key matching a registered type string.

        Args:
            data: Dict produced by Vehicle.to_dict().

        Returns:
            Reconstructed Vehicle instance.
        """
        from rental_system.models import RentalRecord

        vehicle_type = data.pop("type")
        is_available = data.pop("is_available", True)
        rental_data = data.pop("current_rental", None)

        vehicle = cls.create(vehicle_type, **data)
        vehicle.is_available = is_available
        if rental_data:
            vehicle.current_rental = RentalRecord.from_dict(rental_data)

        return vehicle

    @classmethod
    def registered_types(cls) -> list[str]:
        """Return a sorted list of all registered type names."""
        return sorted(cls._registry.keys())


# ── Register built-in types ───────────────────────────────────────────────────
# This block runs once when the module is imported.
# New types only need to be added here (or at app startup).

from rental_system.models import Car, Bike  # noqa: E402

VehicleFactory.register("Car", Car)
VehicleFactory.register("Bike", Bike)
