import unittest
from vehicle_rental import Car, Bike, Vehicle, rent_vehicle
from io import StringIO
import sys

def capture_output(func, *args):

    buffer = StringIO()
    sys.stdout = buffer
    func(*args)
    sys.stdout = sys.__stdout__
    return buffer.getvalue()

class TestCar(unittest.TestCase):

    def setUp(self):

        self.standard_car = Car("KA-01-AA-0001", "Maruti Alto", 800.0, seats=4)
        self.extra_seat_car = Car("KA-01-AA-0002", "Maruti Swift", 800.0, seats=5)
        self.large_car = Car("KA-01-AA-0003", "Toyota Innova", 1500.0, seats=8)

    def test_car_standard_seats_no_surcharge(self):

        cost = self.standard_car.calculate_rental(3)
        self.assertAlmostEqual(cost, 800.0 * 3)

    def test_car_one_extra_seat(self):

        cost = self.extra_seat_car.calculate_rental(3)
        self.assertAlmostEqual(cost, (800 + 100) * 3)

    def test_car_four_extra_seats(self):

        cost = self.large_car.calculate_rental(5)
        self.assertAlmostEqual(cost, (1500 + 400) * 5)

    def test_car_no_discount_at_exactly_7_days(self):

        cost = self.standard_car.calculate_rental(7)
        self.assertAlmostEqual(cost, 800.0 * 7)

    def test_car_discount_at_8_days(self):

        cost = self.standard_car.calculate_rental(8)
        expected = 800.0 * 8 * 0.90
        self.assertAlmostEqual(cost, expected)

    def test_car_discount_long_term_with_extra_seats(self):

        cost = self.large_car.calculate_rental(10)
        expected = (1500 + 400) * 10 * 0.90
        self.assertAlmostEqual(cost, expected)  

    def test_car_display_shows_seats(self):
        output = capture_output(self.extra_seat_car.display_details)
        self.assertIn("5", output)
        self.assertIn("surcharge", output)

    def test_car_display_no_surcharge_label_for_standard_seats(self):
        output = capture_output(self.standard_car.display_details)
        self.assertNotIn("surcharge", output)

class TestBike(unittest.TestCase):

    def setUp(self):
        self.low_cc_bike = Bike("DL-01-BB-0001", "Honda Activa", 200.0, engine_cc=110)
        self.edge_cc_bike = Bike("DL-01-BB-0002", "Hero Splendor", 200.0, engine_cc=150)
        self.high_cc_bike = Bike("DL-01-BB-0003", "KTM Duke 200", 400.0, engine_cc=200)

    def test_bike_low_cc_no_surcharge(self):

        cost = self.low_cc_bike.calculate_rental(5)
        self.assertAlmostEqual(cost, 200.0 * 5)

    def test_bike_exactly_150cc_no_surcharge(self):

        cost = self.edge_cc_bike.calculate_rental(5)
        self.assertAlmostEqual(cost, 200.0 * 5)

    def test_bike_high_cc_surcharge(self):

        cost = self.high_cc_bike.calculate_rental(5)
        self.assertAlmostEqual(cost, (400 + 50) * 5)

    def test_bike_no_discount_at_7_days(self):

        cost = self.low_cc_bike.calculate_rental(7)
        self.assertAlmostEqual(cost, 200.0 * 7)

    def test_bike_discount_at_8_days(self):

        cost = self.low_cc_bike.calculate_rental(8)
        self.assertAlmostEqual(cost, 200.0 * 8 * 0.90)

    def test_bike_high_cc_and_long_term(self):

        cost = self.high_cc_bike.calculate_rental(14)
        expected = (400 + 50) * 14 * 0.90
        self.assertAlmostEqual(cost, expected)  

    def test_bike_display_shows_engine_cc(self):
        output = capture_output(self.high_cc_bike.display_details)
        self.assertIn("200 cc", output)
        self.assertIn("surcharge", output)

    def test_bike_display_no_surcharge_label_for_low_cc(self):
        output = capture_output(self.low_cc_bike.display_details)
        self.assertNotIn("surcharge", output)

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

class TestAbstraction(unittest.TestCase):

    def test_cannot_instantiate_vehicle_directly(self):

        with self.assertRaises(TypeError):
            Vehicle("X", "Brand", 500.0)  

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

if __name__ == "__main__":
    unittest.main(verbosity=2)
