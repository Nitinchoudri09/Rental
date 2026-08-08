class VehicleNotFoundError(Exception):

    def __init__(self, vehicle_number: str) -> None:
        super().__init__(f"Vehicle '{vehicle_number}' not found in fleet.")
        self.vehicle_number = vehicle_number

class VehicleNotAvailableError(Exception):

    def __init__(self, vehicle_number: str) -> None:
        super().__init__(
            f"Vehicle '{vehicle_number}' is currently unavailable (already rented)."
        )
        self.vehicle_number = vehicle_number

class InvalidRentalDurationError(Exception):

    def __init__(self, days: int) -> None:
        super().__init__(
            f"Invalid rental duration: {days} day(s). Must be at least 1."
        )
        self.days = days

class VehicleAlreadyExistsError(Exception):

    def __init__(self, vehicle_number: str) -> None:
        super().__init__(
            f"Vehicle '{vehicle_number}' already exists in the fleet."
        )
        self.vehicle_number = vehicle_number

class VehicleNotRentedError(Exception):

    def __init__(self, vehicle_number: str) -> None:
        super().__init__(
            f"Vehicle '{vehicle_number}' is not currently rented."
        )
        self.vehicle_number = vehicle_number

class UnknownVehicleTypeError(Exception):

    def __init__(self, vehicle_type: str) -> None:
        super().__init__(
            f"Unknown vehicle type: '{vehicle_type}'. "
            f"Register it via VehicleFactory.register()."
        )
        self.vehicle_type = vehicle_type
