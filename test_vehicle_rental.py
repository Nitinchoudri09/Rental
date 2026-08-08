"""
Unit Tests — Vehicle Rental System
====================================
Run with:   python -m pytest test_vehicle_rental.py -v
        or: python -m unittest test_vehicle_rental -v
"""

import unittest
from vehicle_rental import Car, Bike, Vehicle, rent_vehicle
from io import StringIO
import sys


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────

def capture_output(func, *args):
    """Capture stdout printed by a function call."""
    buffer = StringIO()
    sys.stdout = buffer
    func(*args)
    sys.stdout = sys.__stdout__
    return buffer.getvalue()


# ─────────────────────────────────────────────
# Tests: Car
# ─────────────────────────────────────────────

class TestCar(unittest.TestCase):

    def setUp(self):
        """Shared fixtures for all Car tests."""
        self.standard_car = Car("KA-01-AA-0001", "Maruti Alto", 800.0, seats=4)
        self.extra_seat_car = Car("KA-01-AA-0002", "Maruti Swift", 800.0, seats=5)
        self.large_car = Car("KA-01-AA-0003", "Toyota Innova", 1500.0, seats=8)

    # ── Rental price (short-term, no discount) ────

    def test_car_standard_seats_no_surcharge(self):
        """4 seats → no extra charge; total = base × days."""
        cost = self.standard_car.calculate_rental(3)
        self.assertAlmostEqual(cost, 800.0 * 3)

    def test_car_one_extra_seat(self):
        """5 seats → +Rs.100/day; total = (800+100) × 3 = 2700."""
        cost = self.extra_seat_car.calculate_rental(3)
        self.assertAlmostEqual(cost, (800 + 100) * 3)

    def test_car_four_extra_seats(self):
        """8 seats → +Rs.400/day; total = (1500+400) × 5 = 9500."""
        cost = self.large_car.calculate_rental(5)
        self.assertAlmostEqual(cost, (1500 + 400) * 5)

    # ── Long-term discount (> 7 days) ─────────────

    def test_car_no_discount_at_exactly_7_days(self):
        """Exactly 7 days → NO discount (threshold is strictly > 7)."""
        cost = self.standard_car.calculate_rental(7)
        self.assertAlmostEqual(cost, 800.0 * 7)

    def test_car_discount_at_8_days(self):
        """8 days → 10% discount applied."""
        cost = self.standard_car.calculate_rental(8)
        expected = 800.0 * 8 * 0.90
        self.assertAlmostEqual(cost, expected)

    def test_car_discount_long_term_with_extra_seats(self):
        """10 days, 8 seats → surcharge + 10% discount."""
        cost = self.large_car.calculate_rental(10)
        expected = (1500 + 400) * 10 * 0.90
        self.assertAlmostEqual(cost, expected)  # Rs.17,100

    # ── display_details includes seats ────────────

    def test_car_display_shows_seats(self):
        output = capture_output(self.extra_seat_car.display_details)
        self.assertIn("5", output)
        self.assertIn("surcharge", output)

    def test_car_display_no_surcharge_label_for_standard_seats(self):
        output = capture_output(self.standard_car.display_details)
        self.assertNotIn("surcharge", output)


# ─────────────────────────────────────────────
# Tests: Bike
# ─────────────────────────────────────────────

class TestBike(unittest.TestCase):

    def setUp(self):
        self.low_cc_bike = Bike("DL-01-BB-0001", "Honda Activa", 200.0, engine_cc=110)
        self.edge_cc_bike = Bike("DL-01-BB-0002", "Hero Splendor", 200.0, engine_cc=150)
        self.high_cc_bike = Bike("DL-01-BB-0003", "KTM Duke 200", 400.0, engine_cc=200)

    # ── Rental price (short-term, no discount) ────

    def test_bike_low_cc_no_surcharge(self):
        """110 cc → no surcharge; total = 200 × 5 = 1000."""
        cost = self.low_cc_bike.calculate_rental(5)
        self.assertAlmostEqual(cost, 200.0 * 5)

    def test_bike_exactly_150cc_no_surcharge(self):
        """150 cc → threshold is strictly > 150, so NO surcharge."""
        cost = self.edge_cc_bike.calculate_rental(5)
        self.assertAlmostEqual(cost, 200.0 * 5)

    def test_bike_high_cc_surcharge(self):
        """200 cc → +Rs.50/day; total = (400+50) × 5 = 2250."""
        cost = self.high_cc_bike.calculate_rental(5)
        self.assertAlmostEqual(cost, (400 + 50) * 5)

    # ── Long-term discount ────────────────────────

    def test_bike_no_discount_at_7_days(self):
        """Exactly 7 days → no discount."""
        cost = self.low_cc_bike.calculate_rental(7)
        self.assertAlmostEqual(cost, 200.0 * 7)

    def test_bike_discount_at_8_days(self):
        """8 days → 10% discount."""
        cost = self.low_cc_bike.calculate_rental(8)
        self.assertAlmostEqual(cost, 200.0 * 8 * 0.90)

    def test_bike_high_cc_and_long_term(self):
        """14 days + high cc → surcharge + 10% discount."""
        cost = self.high_cc_bike.calculate_rental(14)
        expected = (400 + 50) * 14 * 0.90
        self.assertAlmostEqual(cost, expected)  # Rs.5,670

    # ── display_details includes engine info ──────

    def test_bike_display_shows_engine_cc(self):
        output = capture_output(self.high_cc_bike.display_details)
        self.assertIn("200 cc", output)
        self.assertIn("surcharge", output)

    def test_bike_display_no_surcharge_label_for_low_cc(self):
        output = capture_output(self.low_cc_bike.display_details)
        self.assertNotIn("surcharge", output)


# ─────────────────────────────────────────────
# Tests: Shared discount rule (base class)
# ─────────────────────────────────────────────

class TestDiscountRule(unittest.TestCase):

    def test_discount_threshold_is_7(self):
        self.assertEqual(Vehicle.LONG_TERM_DAYS, 7)

    def test_discount_rate_is_10_percent(self):
        self.assertAlmostEqual(Vehicle.LONG_TERM_DISCOUNT, 0.10)

    def test_boundary_no_discount(self):
        car = Car("X", "Brand", 1000.0, seats=4)
        self.assertAlmostEqual(car.calculate_rental(7), 7000.0)

    def test_boundary_discount_kicks_in(self):
        car = Car("X", "Brand", 1000.0, seats=4)
        self.assertAlmostEqual(car.calculate_rental(8), 7200.0)


# ─────────────────────────────────────────────
# Tests: Abstraction
# ─────────────────────────────────────────────

class TestAbstraction(unittest.TestCase):

    def test_cannot_instantiate_vehicle_directly(self):
        """Vehicle is abstract — direct instantiation must raise TypeError."""
        with self.assertRaises(TypeError):
            Vehicle("X", "Brand", 500.0)  # type: ignore


# ─────────────────────────────────────────────
# Tests: rent_vehicle() polymorphism
# ─────────────────────────────────────────────

class TestRentVehicle(unittest.TestCase):

    def test_rent_car_prints_total(self):
        car = Car("KA-99-ZZ-9999", "Test Car", 500.0, seats=4)
        output = capture_output(rent_vehicle, car, 3)
        self.assertIn("Rs.1,500.00", output)

    def test_rent_bike_prints_total(self):
        bike = Bike("KA-99-ZZ-8888", "Test Bike", 300.0, engine_cc=100)
        output = capture_output(rent_vehicle, bike, 3)
        self.assertIn("Rs.900.00", output)

    def test_rent_vehicle_shows_discount_label(self):
        car = Car("KA-00-AA-0000", "Test Car", 500.0, seats=4)
        output = capture_output(rent_vehicle, car, 10)
        self.assertIn("10%", output)
        self.assertIn("discount", output)

    def test_rent_vehicle_no_discount_label_short_term(self):
        car = Car("KA-00-AA-0001", "Test Car", 500.0, seats=4)
        output = capture_output(rent_vehicle, car, 5)
        self.assertNotIn("discount", output)


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
