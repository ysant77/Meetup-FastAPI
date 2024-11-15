from app.auth import create_access_token

def test_create_event_as_admin(client, db_session):
    # Register an admin and get a valid token
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "securepassword",
        "role": "admin"
    }
    client.post("/signup/", json=admin_data)
    token = create_access_token({"sub": "admin@example.com"})

    # Create event with valid admin token
    response = client.post("/events/", json={
        "name": "Test Event",
        "date": "2025-12-01T10:00:00",
        "venue": "Main Hall",
        "room": "Room A",
        "speaker": "Dr. Smith",
        "description": "A test event",
        "max_pax": 50
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Event"

def test_list_events(client, db_session):
    # Register an admin user and log in to get a valid token
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "securepassword",
        "role": "admin"
    }
    client.post("/signup/", json=admin_data)
    response = client.post("/token/", data={"username": "admin@example.com", "password": "securepassword"})
    token = response.json().get("access_token")

    # Request the list of events as admin
    response = client.get("/events/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_update_event(client, db_session):
    # Register an admin user and log in to get a valid token
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "securepassword",
        "role": "admin"
    }
    client.post("/signup/", json=admin_data)
    response = client.post("/token/", data={"username": "admin@example.com", "password": "securepassword"})
    token = response.json().get("access_token")

    # Create an event
    event_data = {
        "name": "Test Event",
        "date": "2025-12-01T10:00:00",
        "venue": "Main Hall",
        "room": "Room A",
        "speaker": "Dr. Smith",
        "description": "A test event",
        "max_pax": 50
    }
    client.post("/events/", json=event_data, headers={"Authorization": f"Bearer {token}"})

    # Update the event
    update_data = {
        "name": "Updated Event Name",
        "date": "2025-12-01T10:00:00",
        "venue": "Main Hall",
        "room": "Room A",
        "speaker": "Dr. John",
        "description": "Updated description",
        "max_pax": 100
    }
    response = client.put("/events/1", json=update_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

