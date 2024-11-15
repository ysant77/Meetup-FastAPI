# Meetup-FastAPI

A FastAPI-based web application designed to manage meetups and events. This project provides functionality for user registration, authentication, event creation, and enrollment, along with strict role-based access control for added security. 

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Unit Testing](#unit-testing)
- [Postman Collection](#postman-collection)

---

## Features

- **User Authentication**: Secure, hashed password storage with JWT-based authentication.
- **Role-Based Access Control**: 
  - `Admin`: Full access, including user management, event creation, updates, and deletions.
  - `Event Organizer`: Can create, update, and manage events they organize.
  - `User`: Can view and enroll in events.
- **Event Management**: 
  - Create events with attributes such as name, date, venue, speaker, and capacity.
  - View and update event details (limited to event organizers and admins).
  - Enroll in events, respecting maximum capacity and schedule conflicts.
- **Conflict Detection**: Prevents users from enrolling in overlapping events.
- **Unit Testing**: Comprehensive test coverage to ensure reliable functionality across user management, event management, and role-based permissions.

---

## Project Structure

This project is organized into separate files and modules for scalability and ease of maintenance:

Meetup-FastAPI/
├── app/
│   ├── __init__.py             # Initializes the app module
│   ├── main.py                 # FastAPI app and API endpoints
│   ├── database.py             # Database setup and session management
│   ├── dependencies.py         # Shared dependencies (e.g., database session, current user)
│   ├── auth.py                 # Authentication logic, including JWT token creation and validation
│   ├── crud.py                 # Basic CRUD operations for database models
│   ├── services.py             # Business logic and service layer for events, users, and enrollments
│   ├── models.py               # SQLAlchemy models for Users, Events, and Enrollments
│   ├── schemas.py              # Pydantic schemas for request/response validation
├── tests/
│   ├── __init__.py             # Initializes the tests module
│   ├── test_auth.py            # Unit tests for authentication and token management
│   ├── test_dependencies.py    # Unit tests for dependency functions, including user retrieval
│   ├── test_enrollments.py     # Unit tests for user enrollment in events
│   ├── test_events.py          # Unit tests for event management
│   ├── test_users.py           # Unit tests for user management and registration
├──  htmlcov                    # HTML Coverage for unit tests
├── .coverage                   # Hidden folder for test coverage generated
├── pytest.ini                  # Pytest configuration file for setting test options and plugins
├── requirements.txt            # requirements file
├── README.md                   # Documentation for the project


---

## Setup Instructions

### Prerequisites

- Python 3.8 or above
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pytest](https://docs.pytest.org/)
- [Postman](https://www.postman.com/)

### Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/Meetup-FastAPI.git
    cd Meetup-FastAPI
    ```

2. **Set Up Virtual Environment**:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Database**:
    Update the `.env` file with your database configurations and run:
    ```bash
    alembic upgrade head  # or any other command to initialize the database
    ```

5. **Run the Application**:
    ```bash
    uvicorn app.main:app --reload
    ```

6. **Access the API Documentation**:
   Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

---

## API Endpoints

Below are some of the key endpoints provided by this application:

- **User Management**:
  - `POST /signup/`: Register a new user.
  - `POST /token/`: Authenticate user and generate a JWT token.
  
- **Event Management**:
  - `POST /events/`: Create a new event (Admin and Organizer only).
  - `GET /events/`: List all events with optional participant data (Admin only).
  - `PUT /events/{event_id}`: Update event details (Admin and Organizer only).
  - `DELETE /events/{event_id}/unenroll`: Unenroll user from an event.

- **Enrollment Management**:
  - `POST /events/{event_id}/enroll/`: Enroll a user in an event.
  - `DELETE /admin/organizers/{organizer_id}`: Remove an event organizer (Admin only).

Refer to the [Postman Collection](#postman-collection) section for detailed examples and request payloads.

---

## Unit Testing

Unit tests cover critical functionalities across the application, including:

- **Authentication**: Validates JWT token generation and user authentication.
- **Role-based Access Control**: Ensures only authorized roles can access specific endpoints (e.g., `Admin` for sensitive operations).
- **CRUD Operations**: Confirms that creation, update, deletion, and listing operations work as expected.
- **Enrollment Management**: Verifies event enrollment, capacity constraints, and conflict detection.

### Running Tests

To run the tests, navigate to the project root directory and execute:

```bash
pytest --cov=app --cov-report=html

---

## Test Coverage

Our test suite ensures high code coverage across key components of the application. It includes test cases for:

- **Authentication** (`test_auth.py`): Verifying token creation and user login functionality.
- **Dependency Injection** (`test_dependencies.py`): Testing utility functions, including user and session retrieval.
- **Event Management** (`test_events.py`): Checking event creation, listing, and updating with permission handling.
- **Enrollment Management** (`test_enrollments.py`): Validating event enrollment, capacity constraints, and conflict detection.
- **User Management** (`test_users.py`): Ensuring smooth user registration and role assignment.

## Postman Collection

To simplify API testing, a Postman collection is available with pre-configured requests. Download it from the link below and import it into Postman.

[Download Postman Collection](https://dummy-link.com/postman-collection)

This collection includes requests for all major endpoints with detailed descriptions, headers, and sample payloads. Use this to quickly test and experiment with the API.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you'd like to improve this project.

## Acknowledgements

- **FastAPI**: For making it easy to build high-performance APIs.
- **SQLAlchemy**: For robust database management.
- **Pytest**: For making unit testing seamless.

Feel free to explore, test, and expand this project to meet your requirements!
