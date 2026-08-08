"""
tests/test_rental.py
=====================
Unit tests for the Vehicle Rental System.

Covers:
    - Car / Bike rental calculation (with and without surcharges)
    - Long-term discount (>7 days)
    - Loyalty discount (returning renter)
    - Late-return penalty
    - Custom exceptions: VehicleNotAvailableError, InvalidRentalDurationError,
      VehicleNotFoundError, VehicleNotRentedError, VehicleAlreadyExistsError
    - VehicleFactory type creation and unknown-type error
    - RentalManager fleet operations (add / remove / search / list)
    - JSON persistence (save + load round-trip)

Run with:
    python -m pytest tests/test_rental.py -v
or:
    python -m unittest tests.test_rental -v
"""

import json
import os
import tempfile
import unittest

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
from rental_system.models import Car, Bike, Vehicle


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

def make_car(seats: int = 4, price: float = 1000.0) -> Car:
    return Car("TEST-CAR-001", "TestBrand", price, seats)

def make_bike(cc: int = 110, price: float = 500.0) -> Bike:
    return Bike("TEST-BIKE-001", "TestBike", price, cc)

def make_manager(tmp_file: str = "") -> RentalManager:
    return RentalManager(data_file=tmp_file or "data/test_fleet.json")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Car pricing
# ─────────────────────────────────────────────────────────────────────────────

class TestCarPricing(unittest.TestCase):

    def test_standard_seats_no_surcharge(self):
        """4 seats → no surcharge; total = 1000 × 3."""
        car = make_car(seats=4)
        self.assertAlmostEqual(car.calculate_rental(3), 3000.0)

    def test_one_extra_seat(self):
        """5 seats → +Rs.100/day; total = 1100 × 3 = 3300."""
        car = make_car(seats=5)
        self.assertAlmostEqual(car.calculate_rental(3), 3300.0)

    def test_four_extra_seats(self):
        """8 seats → +Rs.400/day; total = 1400 × 5 = 7000."""
        car = Car("X", "B", 1000.0, seats=8)
        self.assertAlmostEqual(car.calculate_rental(5), 7000.0)

    def test_long_term_discount_car(self):
        """10 days, standard car → 10% off: 1000 × 10 × 0.9 = 9000."""
        car = make_car(seats=4)
        self.assertAlmostEqual(car.calculate_rental(10), 9000.0)

    def test_no_discount_at_exactly_7_days(self):
        """7 days exactly → no discount."""
        car = make_car(seats=4)
        self.assertAlmostEqual(car.calculate_rental(7), 7000.0)

    def test_discount_at_8_days(self):
        """8 days → discount applies."""
        car = make_car(seats=4)
        self.assertAlmostEqual(car.calculate_rental(8), 1000 * 8 * 0.9)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Bike pricing
# ─────────────────────────────────────────────────────────────────────────────

class TestBikePricing(unittest.TestCase):

    def test_low_cc_no_surcharge(self):
        """110 cc → no surcharge; total = 500 × 5 = 2500."""
        bike = make_bike(cc=110)
        self.assertAlmostEqual(bike.calculate_rental(5), 2500.0)

    def test_exactly_150cc_no_surcharge(self):
        """150 cc → threshold is strictly > 150, no surcharge."""
        bike = make_bike(cc=150)
        self.assertAlmostEqual(bike.calculate_rental(5), 2500.0)

    def test_high_cc_surcharge(self):
        """200 cc → +Rs.50/day; total = 550 × 5 = 2750."""
        bike = make_bike(cc=200)
        self.assertAlmostEqual(bike.calculate_rental(5), 2750.0)

    def test_long_term_discount_bike(self):
        """14 days, high cc → surcharge + 10% off."""
        bike = make_bike(cc=200, price=400)
        expected = (400 + 50) * 14 * 0.9
        self.assertAlmostEqual(bike.calculate_rental(14), expected)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Late-return penalty
# ─────────────────────────────────────────────────────────────────────────────

class TestLatePenalty(unittest.TestCase):

    def test_no_penalty_on_time(self):
        car = make_car()
        self.assertAlmostEqual(car.late_penalty(actual_days=5, planned_days=5), 0.0)

    def test_no_penalty_early_return(self):
        car = make_car()
        self.assertAlmostEqual(car.late_penalty(actual_days=3, planned_days=5), 0.0)

    def test_penalty_two_extra_days(self):
        """2 extra days × 1000 base × 20% = 400."""
        car = make_car(price=1000.0)
        self.assertAlmostEqual(car.late_penalty(actual_days=7, planned_days=5), 400.0)


# ─────────────────────────────────────────────────────────────────────────────
# 4. VehicleFactory
# ─────────────────────────────────────────────────────────────────────────────

class TestVehicleFactory(unittest.TestCase):

    def test_create_car(self):
        car = VehicleFactory.create(
            "Car", vehicle_number="F-001", brand="Ford",
            base_price_per_day=800.0, seats=5
        )
        self.assertIsInstance(car, Car)
        self.assertEqual(car.seats, 5)

    def test_create_bike(self):
        bike = VehicleFactory.create(
            "Bike", vehicle_number="F-002", brand="Honda",
            base_price_per_day=300.0, engine_cc=125
        )
        self.assertIsInstance(bike, Bike)
        self.assertEqual(bike.engine_cc, 125)

    def test_case_insensitive(self):
        car = VehicleFactory.create(
            "CAR", vehicle_number="F-003", brand="Ford",
            base_price_per_day=500.0, seats=4
        )
        self.assertIsInstance(car, Car)

    def test_unknown_type_raises(self):
        with self.assertRaises(UnknownVehicleTypeError):
            VehicleFactory.create("Spaceship", vehicle_number="X")

    def test_cannot_instantiate_vehicle_directly(self):
        """Vehicle is abstract — direct instantiation must raise TypeError."""
        with self.assertRaises(TypeError):
            Vehicle("V-001", "Brand", 500.0)  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# 5. RentalManager — fleet operations
# ─────────────────────────────────────────────────────────────────────────────

class TestRentalManagerFleet(unittest.TestCase):

    def setUp(self):
        self.mgr = make_manager()
        self.car  = make_car()
        self.bike = make_bike()
        self.mgr.add_vehicle(self.car)
        self.mgr.add_vehicle(self.bike)

    def test_add_vehicle(self):
        self.assertEqual(self.mgr.fleet_size(), 2)

    def test_add_duplicate_raises(self):
        with self.assertRaises(VehicleAlreadyExistsError):
            self.mgr.add_vehicle(make_car())   # same number

    def test_list_all(self):
        self.assertEqual(len(self.mgr.list_all()), 2)

    def test_list_available(self):
        self.assertEqual(len(self.mgr.list_available()), 2)

    def test_search_by_brand(self):
        results = self.mgr.search_by_brand("testbrand")
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], Car)

    def test_search_by_type(self):
        self.assertEqual(len(self.mgr.search_by_type("car")), 1)
        self.assertEqual(len(self.mgr.search_by_type("bike")), 1)

    def test_remove_vehicle(self):
        self.mgr.remove_vehicle("TEST-CAR-001")
        self.assertEqual(self.mgr.fleet_size(), 1)

    def test_remove_nonexistent_raises(self):
        with self.assertRaises(VehicleNotFoundError):
            self.mgr.remove_vehicle("NO-SUCH-VEHICLE")


# ─────────────────────────────────────────────────────────────────────────────
# 6. RentalManager — rental workflow
# ─────────────────────────────────────────────────────────────────────────────

class TestRentalWorkflow(unittest.TestCase):

    def setUp(self):
        self.mgr = make_manager()
        self.mgr.add_vehicle(make_car())
        self.mgr.add_vehicle(make_bike())

    def test_rent_vehicle(self):
        cost = self.mgr.rent_vehicle("TEST-CAR-001", "Alice", 3)
        self.assertAlmostEqual(cost, 3000.0)
        vehicle = self.mgr.get_vehicle("TEST-CAR-001")
        self.assertFalse(vehicle.is_available)

    def test_rent_updates_available_list(self):
        self.mgr.rent_vehicle("TEST-CAR-001", "Alice", 3)
        available = self.mgr.list_available()
        numbers = [v.vehicle_number for v in available]
        self.assertNotIn("TEST-CAR-001", numbers)
        self.assertIn("TEST-BIKE-001", numbers)

    def test_rent_unavailable_raises(self):
        self.mgr.rent_vehicle("TEST-CAR-001", "Alice", 3)
        with self.assertRaises(VehicleNotAvailableError):
            self.mgr.rent_vehicle("TEST-CAR-001", "Bob", 2)

    def test_rent_invalid_days_raises(self):
        with self.assertRaises(InvalidRentalDurationError):
            self.mgr.rent_vehicle("TEST-CAR-001", "Alice", 0)

    def test_rent_unknown_vehicle_raises(self):
        with self.assertRaises(VehicleNotFoundError):
            self.mgr.rent_vehicle("GHOST-001", "Alice", 5)

    def test_return_vehicle(self):
        self.mgr.rent_vehicle("TEST-CAR-001", "Alice", 3)
        summary = self.mgr.return_vehicle("TEST-CAR-001", actual_days=3)
        # After renting, Alice is in history (count=1), so return gets 5% loyalty discount
        expected_cost = 3000.0 * 0.95
        self.assertAlmostEqual(summary["rental_cost"], expected_cost)
        self.assertAlmostEqual(summary["late_penalty"], 0.0)
        vehicle = self.mgr.get_vehicle("TEST-CAR-001")
        self.assertTrue(vehicle.is_available)

    def test_return_with_late_penalty(self):
        self.mgr.rent_vehicle("TEST-CAR-001", "Alice", 3)
        summary = self.mgr.return_vehicle("TEST-CAR-001", actual_days=5)
        # 2 extra days × 1000 base × 20% = 400
        self.assertAlmostEqual(summary["late_penalty"], 400.0)

    def test_return_not_rented_raises(self):
        with self.assertRaises(VehicleNotRentedError):
            self.mgr.return_vehicle("TEST-CAR-001", actual_days=3)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Loyalty discount
# ─────────────────────────────────────────────────────────────────────────────

class TestLoyaltyDiscount(unittest.TestCase):

    def setUp(self):
        self.mgr = make_manager()

    def _fresh_car(self, num: str) -> Car:
        c = Car(num, "Brand", 1000.0, seats=4)
        self.mgr.add_vehicle(c)
        return c

    def test_no_loyalty_on_first_rent(self):
        """First rental → no loyalty discount."""
        self._fresh_car("C-001")
        cost = self.mgr.rent_vehicle("C-001", "Bob", 3)
        self.assertAlmostEqual(cost, 3000.0)

    def test_loyalty_on_second_rent(self):
        """Second rental by same renter → 5% off."""
        self._fresh_car("C-001")
        self._fresh_car("C-002")
        self.mgr.rent_vehicle("C-001", "Bob", 3)
        self.mgr.return_vehicle("C-001", actual_days=3)

        cost2 = self.mgr.rent_vehicle("C-002", "Bob", 3)
        expected = 3000.0 * 0.95
        self.assertAlmostEqual(cost2, expected)


# ─────────────────────────────────────────────────────────────────────────────
# 8. JSON persistence
# ─────────────────────────────────────────────────────────────────────────────

class TestPersistence(unittest.TestCase):

    def test_save_and_load_round_trip(self):
        """Fleet saved to JSON and reloaded should match the original."""
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as tf:
            tmp_path = tf.name

        try:
            mgr1 = RentalManager(data_file=tmp_path)
            mgr1.add_vehicle(Car("P-001", "PersistCar", 900.0, seats=5))
            mgr1.add_vehicle(Bike("P-002", "PersistBike", 300.0, engine_cc=200))
            mgr1.save_fleet()

            mgr2 = RentalManager(data_file=tmp_path)
            mgr2.load_fleet()

            self.assertEqual(mgr2.fleet_size(), 2)
            car = mgr2.get_vehicle("P-001")
            self.assertIsInstance(car, Car)
            self.assertEqual(car.seats, 5)

            bike = mgr2.get_vehicle("P-002")
            self.assertIsInstance(bike, Bike)
            self.assertEqual(bike.engine_cc, 200)

        finally:
            os.unlink(tmp_path)

    def test_load_missing_file_is_silent(self):
        """Loading when no file exists should not raise any exception."""
        mgr = RentalManager(data_file="data/nonexistent_fleet.json")
        mgr.load_fleet()   # must not raise
        self.assertEqual(mgr.fleet_size(), 0)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
