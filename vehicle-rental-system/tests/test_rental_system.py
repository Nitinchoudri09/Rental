import unittest
from src.car import Car
from src.bike import Bike
from src.rental_system import RentalSystem

class TestVehicleSystem(unittest.TestCase):

    def setUp(self):

        self.system = RentalSystem()
        self.car = Car("C100", "Honda City", 2000, 5)
        self.bike = Bike("B100", "Royal Enfield", 800, 350)

    def test_car_creation_valid(self):
        self.assertEqual(self.car.vehicle_number, "C100")
        self.assertEqual(self.car.brand, "Honda City")
        self.assertEqual(self.car.rental_price_per_day, 2000)
        self.assertEqual(self.car.number_of_seats, 5)
        self.assertTrue(self.car.is_available)

    def test_bike_creation_valid(self):
        self.assertEqual(self.bike.vehicle_number, "B100")
        self.assertEqual(self.bike.engine_capacity_cc, 350)

    def test_vehicle_creation_invalid(self):
        with self.assertRaises(ValueError):
            Car("", "Brand", 1000, 4)
        with self.assertRaises(ValueError):
            Bike("B200", "", 1000, 150)
        with self.assertRaises(ValueError):
            Car("C200", "Brand", -100, 4)
        with self.assertRaises(ValueError):
            Car("C200", "Brand", 1000, 0)
        with self.assertRaises(ValueError):
            Bike("B200", "Brand", 1000, -50)

    def test_car_rental_cost_no_discount(self):

        self.assertEqual(self.car.calculate_rental_cost(3), 6000)

    def test_car_rental_cost_with_discount(self):

        self.assertEqual(self.car.calculate_rental_cost(7), 12600)

    def test_bike_rental_cost_no_discount(self):

        self.assertEqual(self.bike.calculate_rental_cost(3), 2400)

    def test_bike_rental_cost_with_discount(self):

        self.assertEqual(self.bike.calculate_rental_cost(5), 3800)

    def test_invalid_rental_days(self):
        with self.assertRaises(ValueError):
            self.car.calculate_rental_cost(0)
        with self.assertRaises(ValueError):
            self.bike.calculate_rental_cost(-5)

    def test_add_vehicle(self):
        self.system.add_vehicle(self.car)
        self.assertEqual(self.system.total_vehicles, 1)
        found = self.system.find_vehicle("c100") 
        self.assertIsNotNone(found)
        self.assertEqual(found.vehicle_number, "C100")

    def test_duplicate_vehicle_prevention(self):
        self.system.add_vehicle(self.car)
        duplicate_car = Car("C100", "Another Brand", 1500, 4)
        with self.assertRaises(ValueError):
            self.system.add_vehicle(duplicate_car)

    def test_rent_vehicle(self):
        self.system.add_vehicle(self.car)
        cost = self.system.rent_vehicle("C100", 3)
        self.assertEqual(cost, 6000)
        self.assertFalse(self.car.is_available)

    def test_rent_unavailable_vehicle(self):
        self.system.add_vehicle(self.car)
        self.system.rent_vehicle("C100", 3)
        with self.assertRaises(ValueError):
            self.system.rent_vehicle("C100", 2)

    def test_return_vehicle(self):
        self.system.add_vehicle(self.car)
        self.system.rent_vehicle("C100", 3)
        self.assertFalse(self.car.is_available)
        self.system.return_vehicle("C100")
        self.assertTrue(self.car.is_available)

    def test_return_available_vehicle(self):
        self.system.add_vehicle(self.car)
        with self.assertRaises(ValueError):
            self.system.return_vehicle("C100")

    def test_vehicle_not_found(self):
        with self.assertRaises(ValueError):
            self.system.rent_vehicle("XYZ", 3)
        with self.assertRaises(ValueError):
            self.system.return_vehicle("XYZ")

if __name__ == '__main__':
    unittest.main()
