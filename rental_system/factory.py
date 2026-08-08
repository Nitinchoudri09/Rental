from __future__ import annotations

from typing import Any, Type

from rental_system.models import Vehicle
from rental_system.exceptions import UnknownVehicleTypeError

class VehicleFactory:

    _registry: dict[str, Type[Vehicle]] = {}

    @classmethod
    def register(cls, type_name: str, vehicle_class: Type[Vehicle]) -> None:

        cls._registry[type_name.lower()] = vehicle_class

    @classmethod
    def create(cls, type_name: str, **kwargs: Any) -> Vehicle:

        key = type_name.lower()
        if key not in cls._registry:
            raise UnknownVehicleTypeError(type_name)
        return cls._registry[key](**kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Vehicle:

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

        return sorted(cls._registry.keys())

from rental_system.models import Car, Bike  

VehicleFactory.register("Car", Car)
VehicleFactory.register("Bike", Bike)
