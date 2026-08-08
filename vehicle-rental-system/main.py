import sys
from src.car import Car
from src.bike import Bike
from src.rental_system import RentalSystem

def run_demo(system: RentalSystem):
    print("=" * 60)
    print("      VEHICLE RENTAL SYSTEM - AUTOMATED DEMO      ")
    print("=" * 60)

    # 1. Create and Add Vehicles
    print("\n[1] ADDING VEHICLES TO THE FLEET...")
    car1 = Car("CAR-101", "Toyota Corolla", 1500, 5)
    car2 = Car("CAR-202", "Honda Innova", 2500, 7)
    bike1 = Bike("BIK-101", "Royal Enfield", 800, 350)
    bike2 = Bike("BIK-202", "Yamaha R15", 1000, 155)

    system.add_vehicle(car1)
    system.add_vehicle(car2)
    system.add_vehicle(bike1)
    system.add_vehicle(bike2)

    # 2. Display Fleet
    print("\n[2] DISPLAYING ALL VEHICLES...")
    system.display_all_vehicles()

    # 3. Calculate Rental Cost
    print("\n[3] CALCULATING RENTAL COSTS (Estimates)...")
    cost_car = system.calculate_rental_cost("CAR-101", 3)
    cost_bike_discount = system.calculate_rental_cost("BIK-101", 6)
    print(f"  Cost for CAR-101 (3 days) : ₹{cost_car}")
    print(f"  Cost for BIK-101 (6 days) : ₹{cost_bike_discount} (includes 5% discount)")

    # 4. Rent a Vehicle
    print("\n[4] RENTING A VEHICLE...")
    print("  Renting CAR-101 for 3 days...")
    actual_cost = system.rent_vehicle("CAR-101", 3)
    print(f"  Success! Total charged: ₹{actual_cost}")

    # 5. Show Unavailable Status
    print("\n[5] VERIFYING AVAILABILITY STATUS...")
    system.display_all_vehicles()

    # 6. Attempt Invalid Operations
    print("\n[6] ATTEMPTING INVALID OPERATIONS (Error Handling)...")
    try:
        print("  Attempting to rent CAR-101 again...")
        system.rent_vehicle("CAR-101", 2)
    except ValueError as e:
        print(f"  Expected Error caught: {e}")

    try:
        print("  Attempting to return an already available vehicle (BIK-101)...")
        system.return_vehicle("BIK-101")
    except ValueError as e:
        print(f"  Expected Error caught: {e}")
        
    try:
        print("  Attempting to find non-existent vehicle...")
        system.rent_vehicle("GHOST-999", 1)
    except ValueError as e:
        print(f"  Expected Error caught: {e}")

    # 7. Return the Vehicle
    print("\n[7] RETURNING VEHICLE...")
    print("  Returning CAR-101...")
    system.return_vehicle("CAR-101")
    
    print("\n[8] FINAL FLEET STATUS...")
    system.display_all_vehicles()
    print("\n--- END OF DEMO ---")


def run_interactive_menu(system: RentalSystem):
    while True:
        print("\n" + "=" * 40)
        print("   VEHICLE RENTAL SYSTEM MENU")
        print("=" * 40)
        print("1. Display all vehicles")
        print("2. Display available vehicles")
        print("3. Rent a vehicle")
        print("4. Return a vehicle")
        print("5. Calculate estimated rental cost")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ").strip()
        
        try:
            if choice == '1':
                system.display_all_vehicles()
            elif choice == '2':
                system.display_available_vehicles()
            elif choice == '3':
                v_num = input("Enter vehicle number to rent: ")
                days = int(input("Enter number of days: "))
                cost = system.rent_vehicle(v_num, days)
                print(f"\nSuccess! Vehicle rented. Total cost: ₹{cost}")
            elif choice == '4':
                v_num = input("Enter vehicle number to return: ")
                system.return_vehicle(v_num)
                print(f"\nSuccess! Vehicle '{v_num}' returned.")
            elif choice == '5':
                v_num = input("Enter vehicle number: ")
                days = int(input("Enter number of days: "))
                cost = system.calculate_rental_cost(v_num, days)
                print(f"\nEstimated cost for {days} days: ₹{cost}")
            elif choice == '6':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError as e:
            print(f"\nError: {e}")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    rental_system = RentalSystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo(rental_system)
    else:
        # Pre-populate for interactive mode
        rental_system.add_vehicle(Car("CAR-001", "Maruti Swift", 1200, 5))
        rental_system.add_vehicle(Bike("BIK-001", "Bajaj Pulsar", 600, 150))
        
        print("Welcome! Run 'python main.py --demo' for the automated demonstration.")
        run_interactive_menu(rental_system)
