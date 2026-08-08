"""
exceptions.py
=============
Custom exceptions for the Vehicle Rental System.
Following SOLID principles, all error types are defined here so
other modules import them without circular dependencies.
"""


class VehicleNotFoundError(Exception):
    """Raised when a vehicle with the given number is not in the fleet."""

    def __init__(self, vehicle_number: str) -> None:
        super().__init__(f"Vehicle '{vehicle_number}' not found in fleet.")
        self.vehicle_number = vehicle_number


class VehicleNotAvailableError(Exception):
    """Raised when a vehicle is already rented out."""

    def __init__(self, vehicle_number: str) -> None:
        super().__init__(
            f"Vehicle '{vehicle_number}' is currently unavailable (already rented)."
        )
        self.vehicle_number = vehicle_number


class InvalidRentalDurationError(Exception):
    """Raised when rental days is zero or negative."""

    def __init__(self, days: int) -> None:
        super().__init__(
            f"Invalid rental duration: {days} day(s). Must be at least 1."
        )
        self.days = days


class VehicleAlreadyExistsError(Exception):
    """Raised when adding a vehicle whose number already exists in the fleet."""

    def __init__(self, vehicle_number: str) -> None:
        super().__init__(
            f"Vehicle '{vehicle_number}' already exists in the fleet."
        )
        self.vehicle_number = vehicle_number


class VehicleNotRentedError(Exception):
    """Raised when returning a vehicle that is not currently rented."""

    def __init__(self, vehicle_number: str) -> None:
        super().__init__(
            f"Vehicle '{vehicle_number}' is not currently rented."
        )
        self.vehicle_number = vehicle_number


class UnknownVehicleTypeError(Exception):
    """Raised by VehicleFactory when an unregistered type string is given."""

    def __init__(self, vehicle_type: str) -> None:
        super().__init__(
            f"Unknown vehicle type: '{vehicle_type}'. "
            f"Register it via VehicleFactory.register()."
        )
        self.vehicle_type = vehicle_type
