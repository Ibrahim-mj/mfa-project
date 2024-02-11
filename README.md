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
3. Create a `.env` file in the root directory and add the following environment variables:
    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    ALLOWED_HOSTS=[]
    DATABASE_URL=sqlite:///db.sqlite3
    EMAIL_HOST_USER=your_email
    EMAIL_HOST_PASSWORD=your_email_password
    ```
    Set up your email host and password for sending OTP to users, and your SMTP server. You can use [Debug Mail](https://debugmail.io/) to test the email sending functionality.
    Do not forget to generate a new secret key. You can use [Djecrety](https://djecrety.ir/) to generate a new secret key.
4. Run the migrations:
    ```bash
    python manage.py migrate
    ```
5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```
6. Run the server:
    python manage.py runserver 8000
    ```
7. Open the browser and go to `http://127.0.0.1:8000/`
8. The api documentation is available at `http://127.0.0.1:8000/api/schema/swagger-ui/`