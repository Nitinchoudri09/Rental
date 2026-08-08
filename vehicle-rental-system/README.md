# Vehicle Rental System

## Overview
The Vehicle Rental System is a clean, Object-Oriented Python application designed to manage a fleet of vehicles for rent. It demonstrates core OOP principles by managing different types of vehicles (Cars, Bikes), processing rentals, calculating costs with custom logic, and managing vehicle availability.

## Features
- **Fleet Management**: Add and store different types of vehicles in the system.
- **Dynamic Pricing**: Calculates rental costs based on vehicle type and duration, including long-term rental discounts.
- **Availability Tracking**: Prevents double-booking by tracking which vehicles are currently rented.
- **Interactive Menu & Demo**: Includes both an automated demonstration script and an interactive command-line interface.
- **Robust Validation**: Handles missing vehicles, invalid rental days, duplicate IDs, and logical errors gracefully.

## OOP Concepts Used

### 1. Encapsulation
Data is hidden within classes and accessed via public properties or methods.
*Example*: In `Vehicle`, the attribute `_is_available` is protected and modified only via the `is_available` setter property, ensuring invalid types aren't assigned.

### 2. Inheritance
Creating specialized classes based on a general class.
*Example*: `Car` and `Bike` inherit from the `Vehicle` base class. They share attributes like `vehicle_number` but add specific attributes like `number_of_seats` or `engine_capacity_cc`.

### 3. Abstraction
Hiding complex implementation details behind simple interfaces.
*Example*: The `Vehicle` class inherits from `abc.ABC` and defines `calculate_rental_cost()` as an `@abstractmethod`. The `RentalSystem` doesn't need to know *how* the cost is calculated; it just calls the method.

### 4. Polymorphism
The ability of different objects to respond to the same method call in their own way.
*Example*: When `RentalSystem.rent_vehicle()` calls `vehicle.calculate_rental_cost(days)`, it automatically executes the correct discounting logic depending on whether the `vehicle` is a `Car` (10% off for 7+ days) or a `Bike` (5% off for 5+ days).

### 5. Composition
Building complex objects by combining simpler ones.
*Example*: The `RentalSystem` *has a* collection of `Vehicle` objects (stored in a dictionary). It uses them to perform its duties rather than inheriting from them.

## Project Structure
```
vehicle-rental-system/
│
├── README.md               # Project documentation
├── requirements.txt        # Dependencies (empty, stdlib only)
├── .gitignore              # Ignored files for git
├── main.py                 # Application entry point (Demo & CLI)
├── src/
│   ├── __init__.py
│   ├── vehicle.py          # Base abstract class
│   ├── car.py              # Car subclass
│   ├── bike.py             # Bike subclass
│   └── rental_system.py    # System manager class
│
└── tests/
    ├── __init__.py
    └── test_rental_system.py # Unit tests
```

## How to Run

1. **Interactive Mode**:
   ```bash
   python main.py
   ```
2. **Automated Demo Mode**:
   ```bash
   python main.py --demo
   ```

## How to Run Tests

Run the built-in `unittest` module discovery from the project root:
```bash
python -m unittest discover
```

## Sample Output

```text
============================================================
      VEHICLE RENTAL SYSTEM - AUTOMATED DEMO      
============================================================

[1] ADDING VEHICLES TO THE FLEET...
  ✔  Car 'CAR-101' (Toyota Corolla) added successfully.
  ✔  Bike 'BIK-101' (Royal Enfield) added successfully.

[2] DISPLAYING ALL VEHICLES...
──────────────────────────────────────────────────
  Vehicle Rental System  —  Fleet (2 vehicles)
──────────────────────────────────────────────────
  Type           : Car
  Vehicle Number : CAR-101
  Brand          : Toyota Corolla
  Price / Day    : ₹1,500.00
  Status         : Available
  Seats          : 5
  Pricing Note   : 10% discount for 7+ day rentals
──────────────────────────────────────────────────
...
```

## Design Decisions
- **`abc.ABC` Base Class**: Used to enforce that no generic `Vehicle` can be instantiated and that all subclasses implement required pricing logic.
- **Dictionary for Fleet Storage**: `RentalSystem` uses a dictionary (`self._fleet`) keyed by `vehicle_number`. This allows O(1) time complexity when looking up, renting, or returning a vehicle.
- **Type Hints**: Extensive use of Python typing (`-> float`, `-> None`) improves code readability and developer experience in IDEs.
- **No External Libraries**: Ensures the project is highly portable and demonstrates core language proficiency suitable for an interview environment.

## Future Improvements
- **Database Storage**: Replace the in-memory dictionary with SQLite or PostgreSQL for persistence.
- **Customer Management**: Introduce a `Customer` class to track who rented which vehicle.
- **Rental History**: Log transactions (start date, end date, cost) to generate financial reports.
- **Web Interface**: Build a REST API using FastAPI or Flask, and a simple front-end.
