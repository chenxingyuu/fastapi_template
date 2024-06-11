# FastAPI Template

A template project for building a FastAPI application with Tortoise ORM and Aerich for database migrations.

## Features

- FastAPI for building APIs
- Tortoise ORM for database modeling
- Aerich for managing database migrations
- Pydantic for data validation
- Docker and Docker Compose support for containerization
- Role-Based Access Control (RBAC) implemented

## Usage

### Install

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/fastapi-template.git
    cd fastapi-template
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Migrate

1. **Initialize Aerich:**

    ```bash
    aerich init -t app.models.session.TORTOISE_ORM
    ```

2. **Initialize the database:**

    ```bash
    aerich init-db
    ```

3. **Create and apply migrations:**

    ```bash
    aerich migrate
    aerich upgrade
    ```

### Run

1. **Set the configuration file path:**

    On Linux or macOS:
    ```bash
    export CONFIG_FILE_PATH=/path/to/your/config.ini
    ```

    On Windows:
    ```cmd
    set CONFIG_FILE_PATH=C:\path\to\your\config.ini
    ```

2. **Start the FastAPI application:**

    ```bash
    uvicorn app.main:app --reload
    ```

3. **Access the application:**

    Open your browser and navigate to `http://127.0.0.1:8000`.

### Use Docker

1. **Build the Docker image:**

    ```bash
    docker build -t fastapi-template .
    ```

2. **Run the Docker container:**

    ```bash
    docker run -d -p 8000:8000 --name fastapi-template fastapi-template
    ```

3. **Access the application:**

    Open your browser and navigate to `http://127.0.0.1:8000`.

### Use Docker Compose

1. **Start the services:**

    ```bash
    docker-compose up -d
    ```

2. **Access the application:**

    Open your browser and navigate to `http://127.0.0.1:8000`.

3. **Stopping the services:**

    ```bash
    docker-compose down
    ```

## Development

1. **Install pre-commit hooks:**

    ```bash
    pre-commit install
    ```

2. **Run tests:**

    ```bash
    pytest
    ```

3. **Check code formatting:**

    ```bash
    black --check .
    ```

4. **Lint the code:**

    ```bash
    flake8
    ```

5. **Run the application in development mode:**

    ```bash
    uvicorn app.main:app --reload
    ```

## Configuration

Configuration is managed through a `config.ini` file. Make sure to set the `CONFIG_FILE_PATH` environment variable to point to your configuration file before running the application.

Example `config.ini`:

```ini
[app]
PROJECT_NAME = My Custom FastAPI Project
API_V1_STR = /api/v1

[database]
DATABASE_URL = postgres://user:password@localhost/dbname

[security]
SECRET_KEY = your-custom-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

By following this template, you can get your FastAPI application up and running quickly with all necessary features and configurations.