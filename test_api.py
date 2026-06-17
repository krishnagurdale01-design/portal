import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:8080/api/enquiries"

def run_test(name, func):
    print(f"Running test: {name}...", end=" ")
    try:
        func()
        print("PASSED")
        return True
    except Exception as e:
        print("FAILED")
        print(f"Error: {e}")
        return False

def make_request(url, method="GET", data=None):
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=req_data, method=method)
    req.add_header("Content-Type", "application/json")
    
    with urllib.request.urlopen(req) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body) if body else None

def test_get_enquiries():
    status, data = make_request(BASE_URL)
    assert status == 200, f"Expected 200, got {status}"
    assert isinstance(data, list), "Expected list of enquiries"
    assert len(data) >= 0, "Expected at least 0 enquiries"

def test_create_enquiry():
    payload = {
        "name": "Test Student",
        "parent": "Test Parent",
        "email": "test@srigowthami.edu",
        "phone": "9999999999",
        "course": "B.Tech Computer Science & Engineering",
        "campus": "Main Campus",
        "marks": 95,
        "status": "Pending",
        "staff": "Dr. K. Raghavan",
        "notes": "Testing backend API integrations."
    }
    status, data = make_request(BASE_URL, method="POST", data=payload)
    assert status == 200, f"Expected 200, got {status}"
    assert "id" in data, "Created item should contain id"
    assert data["name"] == "Test Student"
    
    # Store ID globally to use in update/delete tests
    global test_enquiry_id
    test_enquiry_id = data["id"]

def test_update_enquiry():
    assert test_enquiry_id is not None, "Test ID must be initialized"
    url = f"{BASE_URL}/{test_enquiry_id}"
    payload = {
        "status": "Shortlisted",
        "staff": "Prof. S. Laxmi",
        "notes": "Verified candidate credentials."
    }
    status, data = make_request(url, method="PUT", data=payload)
    assert status == 200, f"Expected 200, got {status}"
    assert data["status"] == "Shortlisted"
    assert data["staff"] == "Prof. S. Laxmi"

def test_delete_enquiry():
    assert test_enquiry_id is not None, "Test ID must be initialized"
    url = f"{BASE_URL}/{test_enquiry_id}"
    status, data = make_request(url, method="DELETE")
    assert status == 200, f"Expected 200, got {status}"
    assert data["status"] == "success"

def test_restore_database():
    url = f"{BASE_URL}/restore"
    status, data = make_request(url, method="POST")
    assert status == 200, f"Expected 200, got {status}"
    assert data["status"] == "success"
    assert len(data["data"]) == 5, f"Expected 5 entries after reset, got {len(data['data'])}"

if __name__ == "__main__":
    test_enquiry_id = None
    
    tests = [
        ("GET /api/enquiries", test_get_enquiries),
        ("POST /api/enquiries", test_create_enquiry),
        ("PUT /api/enquiries/{id}", test_update_enquiry),
        ("DELETE /api/enquiries/{id}", test_delete_enquiry),
        ("POST /api/enquiries/restore", test_restore_database),
    ]
    
    success = True
    for name, func in tests:
        if not run_test(name, func):
            success = False
            
    if not success:
        sys.exit(1)
    else:
        print("\nAll API integration tests passed successfully!")
