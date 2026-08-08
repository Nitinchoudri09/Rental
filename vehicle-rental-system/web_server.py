import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import our backend logic
from src.car import Car
from src.bike import Bike
from src.rental_system import RentalSystem

# Initialize and prepopulate the rental system
rental_system = RentalSystem()
rental_system.add_vehicle(Car("CAR-101", "Toyota Corolla", 1500, 5))
rental_system.add_vehicle(Car("CAR-202", "Honda Innova", 2500, 7))
rental_system.add_vehicle(Bike("BIK-101", "Royal Enfield", 800, 350))
rental_system.add_vehicle(Bike("BIK-202", "Yamaha R15", 1000, 155))


class APIRequestHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler to serve both static files and our REST API.
    """
    
    def __init__(self, *args, **kwargs):
        # Serve files from the 'public' directory
        super().__init__(*args, directory="public", **kwargs)

    def do_GET(self):
        """Handle GET requests for static files and /api/vehicles."""
        parsed_path = urlparse(self.path)
        
        # API Route: GET /api/vehicles
        if parsed_path.path == '/api/vehicles':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Serialize fleet data to JSON
            vehicles = []
            for v in rental_system.get_all_vehicles():
                v_data = {
                    "vehicle_number": v.vehicle_number,
                    "type": v.get_vehicle_type(),
                    "brand": v.brand,
                    "price_per_day": v.rental_price_per_day,
                    "is_available": v.is_available,
                }
                # Add subclass-specific data
                if isinstance(v, Car):
                    v_data["specs"] = f"{v.number_of_seats} Seats"
                elif isinstance(v, Bike):
                    v_data["specs"] = f"{v.engine_capacity_cc} cc"
                
                vehicles.append(v_data)
                
            response = json.dumps({"vehicles": vehicles})
            self.wfile.write(response.encode('utf-8'))
            return
            
        # Fallback to serving static files from /public
        return super().do_GET()

    def do_POST(self):
        """Handle POST requests for renting and returning vehicles."""
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON data")
            return

        # API Route: POST /api/rent
        if parsed_path.path == '/api/rent':
            v_num = data.get('vehicle_number')
            days = data.get('days')
            
            try:
                days = int(days)
                cost = rental_system.rent_vehicle(v_num, days)
                self._send_json(200, {
                    "success": True, 
                    "message": f"Successfully rented for {days} days.",
                    "cost": cost
                })
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        # API Route: POST /api/return
        if parsed_path.path == '/api/return':
            v_num = data.get('vehicle_number')
            
            try:
                rental_system.return_vehicle(v_num)
                self._send_json(200, {
                    "success": True, 
                    "message": f"Vehicle '{v_num}' successfully returned."
                })
            except Exception as e:
                self._send_json(400, {"success": False, "error": str(e)})
            return

        # Handle unknown POST routes
        self._send_json(404, {"error": "Endpoint not found"})

    def _send_json(self, status_code, data_dict):
        """Helper to send JSON responses."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data_dict).encode('utf-8'))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIRequestHandler)
    print(f"🚀 Server running on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("Server stopped.")

if __name__ == '__main__':
    run_server()
