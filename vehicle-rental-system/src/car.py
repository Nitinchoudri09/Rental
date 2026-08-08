from src.vehicle import Vehicle

class Car(Vehicle):

    LONG_RENTAL_THRESHOLD: int = 7       
    LONG_RENTAL_DISCOUNT: float = 0.10   

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        rental_price_per_day: float,
        number_of_seats: int,
    ) -> None:

        super().__init__(vehicle_number, brand, rental_price_per_day)

        if number_of_seats < 1:
            raise ValueError("Number of seats must be at least 1.")

        self._number_of_seats: int = number_of_seats

    @property
    def number_of_seats(self) -> int:

        return self._number_of_seats

    def get_vehicle_type(self) -> str:

        return "Car"

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
            f"10% discount for {self.LONG_RENTAL_THRESHOLD}+ day rentals"
        )
        return (
            f"{base}\n"
            f"  Seats          : {self._number_of_seats}\n"
            f"  Pricing Note   : {discount_note}"
        )
