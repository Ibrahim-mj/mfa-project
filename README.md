# Django Authentication Project

This is a Django project that implements custom user authentication using email and password, JWT authentication, and 2-factor authentication using OTP.

## Features

- Users can register account
- Admin can approve users account
- Users should be able to login using MFA to a protected route
- Custom user model with email as the unique identifier
- Custom authentication backend that authenticates users based on email and password
- JWT authentication
- Permission classes to control access to views

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/Ibrahim-mj/mfa-project.git
    ```
2. Install the requirements:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the migrations:
    ```bash
    python manage.py migrate
    ```
4. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```
5. Run the server:
    ```bash
    python manage.py runserver 8000
    ```
6. Open the browser and go to `http://127.0.0.1:8000/`
7. The api documentation is available at `http://127.0.0.1:8000/api/schema/swagger-ui/`