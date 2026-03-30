import traceback
import os
from app import create_app

app = create_app()

def test_all_templates():
    with app.test_client() as client:
        routes_to_test = [
            '/',
            '/login',
            '/register',
            '/productos/',
            '/clientes/',
        ]
        
        errors = 0
        for route in routes_to_test:
            try:
                resp = client.get(route)
                if resp.status_code == 500:
                    errors += 1
                    print(f"[FAIL] {route} returned 500")
                else:
                    print(f"[OK] {route} returned {resp.status_code}")
            except Exception as e:
                errors += 1
                print(f"[FAIL Exception] {route} -> {e}")
                
        print(f"Total errors: {errors}")

if __name__ == '__main__':
    test_all_templates()
