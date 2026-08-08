from src.vehicle import Vehicle

class Bike(Vehicle):

    LONG_RENTAL_THRESHOLD: int = 5      
    LONG_RENTAL_DISCOUNT: float = 0.05  

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        rental_price_per_day: float,
        engine_capacity_cc: int,
    ) -> None:

        super().__init__(vehicle_number, brand, rental_price_per_day)

        if engine_capacity_cc <= 0:
            raise ValueError("Engine capacity must be a positive integer (cc).")

        self._engine_capacity_cc: int = engine_capacity_cc

    @property
    def engine_capacity_cc(self) -> int:

        return self._engine_capacity_cc

    def get_vehicle_type(self) -> str:

        return "Bike"

    def calculate_rental_cost(self, days: int) -> float:

        if not isinstance(days, int) or days < 1:
            raise ValueError("Number of rental days must be a positive integer.")

        total = self._rental_price_per_day * days

        if days >= self.LONG_RENTAL_THRESHOLD:
            discount = total * self.LONG_RENTAL_DISCOUNT
            total -= discount

        return round(total, 2)

    def display_details(self) -> str:

        base = super().display_details()
        discount_note = (
            f"5% discount for {self.LONG_RENTAL_THRESHOLD}+ day rentals"
        )
        return (
            f"{base}\n"
            f"  Engine         : {self._engine_capacity_cc} cc\n"
            f"  Pricing Note   : {discount_note}"
        )
