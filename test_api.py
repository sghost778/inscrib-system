import requests
import time

def test_api():
    base_url = "http://localhost:5000/api"
    
    # 1. Login
    print("--- 1. Login ---")
    try:
        res = requests.post(f"{base_url}/login", json={"usuario":"admin", "password":"admin123"})
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        token = res.json().get('token')
        if not token:
            print("No token received. Exiting.")
            return
    except Exception as e:
        print(f"Login failed: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Logs
    print("\n--- 2. Get Logs ---")
    try:
        res = requests.get(f"{base_url}/dashboard/logs", headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Logs failed: {e}")

    # 3. Create Student
    print("\n--- 3. Create Student ---")
    try:
        data = {
            "cedula_escolar": "V-99999999",
            "nombres": "Estudiante",
            "apellidos": "Prueba",
            "fecha_nacimiento": "2015-05-15",
            "direccion": "Calle Prueba"
        }
        res = requests.post(f"{base_url}/estudiantes", headers=headers, json=data)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Create student failed: {e}")

if __name__ == "__main__":
    test_api()
