from app.auth import create_access_token
from app.schemas import EventCreate
from app import services as service

def test_enroll_user_in_event(client, db_session):
    # Ensure an event exists in the database
    event_data = EventCreate(
        name="Test Event",
        date="2025-12-01T10:00:00",
        venue="Main Hall",
        room="Room A",
        speaker="Dr. Smith",
        description="A test event",
        max_pax=50
    )
    service.create_event(db_session, event_data, organizer_id=1)  # Use valid organizer ID

    # Register and log in a user to get a valid token
    user_data = {
        "name": "Test User",
        "email": "test_user@example.com",
        "password": "securepassword",
        "role": "user"
    }
    client.post("/signup/", json=user_data)
    token = create_access_token({"sub": "test_user@example.com"})

    # Attempt to enroll user in event with valid token
    response = client.post("/events/1/enroll/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Enrollment successful"

def test_event_capacity(client, db_session):
    # Ensure an event exists in the database
    event_data = EventCreate(
        name="Capacity Test Event",
        date="2025-12-01T10:00:00",
        venue="Main Hall",
        room="Room A",
        speaker="Dr. Smith",
        description="A test event for capacity",
        max_pax=5
    )
    # Create the event with a valid organizer ID
    organizer_data = {
        "name": "Organizer User",
        "email": "organizer@example.com",
        "password": "securepassword",
        "role": "event_organizer"
    }
    client.post("/signup/", json=organizer_data)
    response = client.post("/token/", data={"username": "organizer@example.com", "password": "securepassword"})
    organizer_token = response.json().get("access_token")
    organizer_id = 1  # This should match the registered organizer's ID in your database

    created_event = service.create_event(db_session, event_data, organizer_id=organizer_id)

    # Register multiple users and log them in to get tokens
    for i in range(5):
        email = f"user_{i}@example.com"
        user_data = {"name": f"User {i}", "email": email, "password": "securepassword", "role": "user"}
        client.post("/signup/", json=user_data)
        # Obtain token via login
        response = client.post("/token/", data={"username": email, "password": "securepassword"})
        token = response.json().get("access_token")
        # Enroll each user in the event
        client.post(f"/events/{created_event.id}/enroll/", headers={"Authorization": f"Bearer {token}"})

    # Attempt one more enrollment, expecting failure due to capacity
    final_user_data = {"name": "Final User", "email": "final_user@example.com", "password": "securepassword", "role": "user"}
    client.post("/signup/", json=final_user_data)
    final_response = client.post("/token/", data={"username": "final_user@example.com", "password": "securepassword"})
    final_token = final_response.json().get("access_token")
    final_enroll_response = client.post(f"/events/{created_event.id}/enroll/", headers={"Authorization": f"Bearer {final_token}"})
    assert final_enroll_response.status_code == 400
    assert final_enroll_response.json()["detail"] == "Enrollment failed (conflict or capacity reached)"

def test_unenroll_user(client, db_session):
    # Ensure an event exists in the database
    event_data = EventCreate(
        name="Unenroll Test Event",
        date="2025-12-01T10:00:00",
        venue="Main Hall",
        room="Room A",
        speaker="Dr. Smith",
        description="A test event for unenrollment",
        max_pax=50
    )
    
    # Register an organizer and retrieve their ID
    organizer_data = {
        "name": "Organizer User",
        "email": "organizer@example.com",
        "password": "securepassword",
        "role": "event_organizer"
    }
    response = client.post("/signup/", json=organizer_data)
    organizer_id = response.json().get("id")
    client.post("/token/", data={"username": "organizer@example.com", "password": "securepassword"})

    # Create the event with the valid organizer ID
    event = service.create_event(db_session, event_data, organizer_id=organizer_id)
    assert event is not None, "Event creation failed due to a scheduling conflict"

    # Register and enroll a user
    user_data = {
        "name": "Test User",
        "email": "test_user@example.com",
        "password": "securepassword",
        "role": "user"
    }
    client.post("/signup/", json=user_data)
    response = client.post("/token/", data={"username": "test_user@example.com", "password": "securepassword"})
    token = response.json().get("access_token")

    # Enroll the user in the event
    client.post(f"/events/{event.id}/enroll/", headers={"Authorization": f"Bearer {token}"})

    # Unenroll the user from the event
    response = client.delete(f"/events/{event.id}/unenroll", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "Unenrollment failed unexpectedly"

