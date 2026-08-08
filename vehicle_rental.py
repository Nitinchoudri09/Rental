from abc import ABC, abstractmethod

class Vehicle(ABC):

    LONG_TERM_DAYS: int = 7           
    LONG_TERM_DISCOUNT: float = 0.10  

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
    ) -> None:
        self.vehicle_number: str = vehicle_number
        self.brand: str = brand
        self.base_price_per_day: float = base_price_per_day

    @abstractmethod
    def calculate_rental(self, days: int) -> float:

    def _apply_long_term_discount(self, total: float, days: int) -> float:

        if days > self.LONG_TERM_DAYS:
            total *= (1 - self.LONG_TERM_DISCOUNT)
        return total

    def display_details(self) -> None:

        print(f"  Vehicle Number : {self.vehicle_number}")
        print(f"  Brand          : {self.brand}")
        print(f"  Base Price/Day : Rs.{self.base_price_per_day:.2f}")

class Car(Vehicle):

    EXTRA_SEAT_CHARGE: float = 100.0  
    STANDARD_SEATS: int = 4           

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
        seats: int,
    ) -> None:
        super().__init__(vehicle_number, brand, base_price_per_day)
        self.seats: int = seats

    def _extra_seat_charge_per_day(self) -> float:

        extra_seats = max(0, self.seats - self.STANDARD_SEATS)
        return extra_seats * self.EXTRA_SEAT_CHARGE

    def calculate_rental(self, days: int) -> float:

        daily_rate = self.base_price_per_day + self._extra_seat_charge_per_day()
        total = daily_rate * days
        return self._apply_long_term_discount(total, days)

    def display_details(self) -> None:

        super().display_details()
        extra = self._extra_seat_charge_per_day()
        extra_info = (
            f"  (+Rs.{extra:.0f}/day surcharge for "
            f"{self.seats - self.STANDARD_SEATS} extra seat(s))"
            if extra > 0
            else ""
        )
        print(f"  Seats          : {self.seats}{extra_info}")

class Bike(Vehicle):

    HIGH_CC_THRESHOLD: int = 150     
    HIGH_CC_SURCHARGE: float = 50.0  

    def __init__(
        self,
        vehicle_number: str,
        brand: str,
        base_price_per_day: float,
        engine_cc: int,
    ) -> None:
        super().__init__(vehicle_number, brand, base_price_per_day)
        self.engine_cc: int = engine_cc

    def _high_cc_surcharge_per_day(self) -> float:

        return self.HIGH_CC_SURCHARGE if self.engine_cc > self.HIGH_CC_THRESHOLD else 0.0

    def calculate_rental(self, days: int) -> float:

        daily_rate = self.base_price_per_day + self._high_cc_surcharge_per_day()
        total = daily_rate * days
        return self._apply_long_term_discount(total, days)

    def display_details(self) -> None:

        super().display_details()
        surcharge = self._high_cc_surcharge_per_day()
        surcharge_info = (
            f"  (+Rs.{surcharge:.0f}/day high-cc surcharge)"
            if surcharge > 0
            else ""
        )
        print(f"  Engine         : {self.engine_cc} cc{surcharge_info}")

def rent_vehicle(vehicle: Vehicle, days: int) -> None:

    total = vehicle.calculate_rental(days)
    discount_applied = days > Vehicle.LONG_TERM_DAYS

    print("=" * 54)
    print(f"  {type(vehicle).__name__} Rental  |  {days} Day(s)")
    print("=" * 54)
    vehicle.display_details()
    print(f"  Rental Days    : {days}")
    if discount_applied:
        print(f"  Discount       : {Vehicle.LONG_TERM_DISCOUNT:.0%} long-term discount applied!")
    print(f"  Total Cost     : Rs.{total:,.2f}")
    print()

if __name__ == "__main__":

    fleet: list[Vehicle] = [

        Car(
            vehicle_number="KA-01-AB-1234",
            brand="Maruti Swift",
            base_price_per_day=800.0,
            seats=5,    
        ),
        Car(
            vehicle_number="MH-12-CD-5678",
            brand="Toyota Innova",
            base_price_per_day=1500.0,
            seats=8,    
        ),

        Bike(
            vehicle_number="DL-05-EF-9012",
            brand="Honda Activa",
            base_price_per_day=200.0,
            engine_cc=110,   
        ),
        Bike(
            vehicle_number="TN-09-GH-3456",
            brand="KTM Duke 200",
            base_price_per_day=400.0,
            engine_cc=200,   
        ),
    ]

    rental_plan: list[tuple[Vehicle, int]] = [
        (fleet[0], 3),   
        (fleet[1], 10),  
        (fleet[2], 5),   
        (fleet[3], 14),  
    ]

    print()
    print("=" * 54)
    print("        VEHICLE RENTAL SYSTEM")
    print("=" * 54)
    print()

    for vehicle, days in rental_plan:
        rent_vehicle(vehicle, days)
