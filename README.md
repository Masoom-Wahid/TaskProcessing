# Project Setup Guide

Follow these steps to set up and run the project using Docker.

---

## 1. Set Up Environment Variables

Change the `.env.prod` file to  `.env` file in the root directory of the project and fill in the required variables:

```plaintext
SECRET_KEY=
EMAIL=
EMAIL_PASSWORD=
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
```

- **`SECRET_KEY`**: Generate a secret key by running:
  ```bash
  python get_secret.py
  ```
  Copy the output and paste it into the `SECRET_KEY` field.

- **`EMAIL`**: Your email address.
- **`EMAIL_PASSWORD`**: Your email app password.
- **`POSTGRES_DB`**: Your PostgreSQL database name.
- **`POSTGRES_USER`**: Your PostgreSQL username.
- **`POSTGRES_PASSWORD`**: Your PostgreSQL password.

---

## 2. Run Docker Compose

Start the application using Docker Compose:

```bash
docker-compose up
```

This will build and start the containers for the application and PostgreSQL database.

---