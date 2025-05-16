# Bynder Lottery Assignment

## Task and requirements

**Task:** Create a service that handles a lottery system.

**Requirements:**

- The service will allow anyone to register as a lottery participant.
- Lottery participants can submit as many ballots as they want for any lottery that
isn't yet finished.
- Each day at midnight the lottery event will be considered closed and a random
lottery winner will be selected.
- All users will be able to check the winning ballot for any specific date.
- The service will have to persist the data regarding the lottery.

**Hints:**

- Incorrect domain modeling has been an issue in Bynder's past, we have solved many
company-wide problems by moving towards software guided by Domain Driven Design.
- We prefer simplicity over complexity in our software solutions.
- We value readable and maintainable code.

## Features

- Lottery service supports authentication and role-based authorization
- Anyone can register as a user
- Registered users can submit multiple ballots for any open lottery
- Registered users can view all their submitted ballots
- Admins can create and close lotteries
- Admins can view all submitted ballots for specific lottery but cannot submit ballots themselves
- Closing the lottery triggers random winner selection if there are any ballots
- Registration is not requiered to view all open lotteries, lottery details and winning ballots
- Each lottery has its **unique** closure day (multiple lotteries with the same closure day are not allowed)
- Lottery can be created with any closure day in the future
- Lottery is assigned with random name if not provided
- As soon as the lottery is created, user can submit ballots to this lottery until the lottery is closed
- An automated task runs daily at midnight to close the previous day’s lottery and select a winner
- Data is stored in the SQL database

## Use

### **Run**

```bash
docker compose up --build
```

This starts a lottery service at http://localhost:8000, initializes the database and schedules
the daily task to close lotteries and draw winners.

At first run, the schema is created and the default lottery admin is added.
Admin email and password are set in the `.env` file.
The default values are: `admin@example.com` and `admin_password`.

### **Populate demo data**

```bash
python scripts/populate_demo.py -l 30 -u 10 -b 100 -d YYYY-MM-DD
```

- `-l`: Number of lotteries to create starting with the closure day `-d`, default is 30
- `-u`: Number of users to create, default is 10
- `-b`: Number of ballots per user randomly submitted to the lotteries, default is 100
- `-d`: The closure day of the first created lottery, default is today

For additional options, run:
```bash
python scripts/populate_demo.py --help
```

Closing the lottery and drawing the winner can be manualy triggered by:

```bash
python scripts/close_and_draw.py -d YYYY-MM-DD
```

For additional options, run:
```bash
python scripts/populate_demo.py --help
```

**Note:** `requests` is required to run both scripts.

### **Environment Configuration**

Environmental variables are configured in the `.env` file:

```ini
# Database configuration
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
# Docker container name for PostgreSQL
POSTGRES_HOST=
POSTGRES_PORT=

# Security configuration (JWT)
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=

# Application metadata
PROJECT_NAME=
VERSION=

# Lottery admin settings
LOTTERY_ADMIN_USERNAME=
LOTTERY_ADMIN_EMAIL=
LOTTERY_ADMIN_PASSWORD=
```

### **API endpoints**

- `POST /user/register`:
Register a new user.
Example json payload:
    ```
    {
      "username": "user",
      "email": "user@example.com",
      "password": "password",
    }
    ```

- `POST /auth/login`:
User login (`OAuth2PasswordBearer`).
Expects `username` (user email) and `password` fields.
Return access token. Token validity is set in the `.env` file.

- `GET /lotteries`: Get all open lotteries

- `GET /lotteries/YYYY-MM-DD`: Get lottery details by its closure date

- `GET /lotteries/YYYY-MM-DD/winner`: Get winning ballot for the lottery by its closure date

- `POST /lotteries`: Create a new lottery.
Admin privileges required (expects OAuth 2.0 token).
Example json payload:
    ```
    {
      "name": "My Lottery",
      "closure_date": "YYYY-MM-DD"
    }
    ```

- `POST /lotteries/close_and_draw/?lottery_date=YYYY-MM-DD`:
Close the lottery and draw a winner.
Admin privileges required (expects OAuth 2.0 token).

-  `POST /ballots/?lottery_date=YYYY-MM-DD`:
Submit a new ballot for the lottery by its closure date.
Authentication required (expects OAuth 2.0 token).

-  `GET /ballots/mine:`:
Get all ballots submitted by the current user.
Authentication required (expects OAuth 2.0 token).

-   `GET /ballots/lottery/YYYY-MM-DD`:
Get all ballots submitted for the lottery by its closure date.
Admin privileges required (expects OAuth 2.0 token).

### API Documentation

Once the application is running, visit:

```
http://localhost:8000/docs
```
or
```
http://localhost:8000/redoc
```

## Test

To run the tests:

```bash
chmod +x scripts/test.sh
./scripts/test.sh
```

## Architectural Overview

### Domain-Driven Design (DDD)

This project follows **Domain-Driven Design (DDD)** principles to separate business logic, data access, and API delivery.

### **Domain Entities**

- **User**  
  Represents a registered participant with `email`, `username`, `hashed_password`.

- **Lottery**  
  Represents a lottery event identified by `closure_date` with `name`, `is_closed` status and optionally `winning_ballot_id`.

- **Ballot**  
  Represents a user-submitted ballot for a specific lottery.

### **Domain Services**

- **UserService**  
  Handles user registration and authentication.

- **LotteryService**  
  Manages listing, creation and closure of lotteries.

- **BallotService**  
  Manages user ballot submissions and retrieval of ballots by lottery or user.

### **API Layer**

- **Purpose**:  
  - Defines HTTP endpoints for client interactions.
  - Validates and parses request data using Pydantic models.
  - Maps domain exceptions to HTTP responses.

- **Components**:
  - `/users/register`: Register a new user.
  - `/auth/login`: Obtain an access token.
  - `/lotteries/`: Create, list, or draw a lottery.
  - `/ballots/`: Submit and list ballots.

### **Business Layer**

- **Purpose**:  
  Encapsulates all **business rules** and **state changes**.

- **Responsibilities**:
  - Enforcing user uniqueness.
  - Validating lottery closure conditions.
  - Managing ballot submissions without conflicting states.
  - Handling winner selection logic.

### **Separation of Concerns**

| Layer            | Responsibility                              |
|------------------|---------------------------------------------|
| **API Layer**    | HTTP handling, request/response validation  |
| **Service Layer**| Business logic, state transitions           |
| **Persistence**  | Data storage and retrieval (PostgreSQL)     |

## Technical implementation

### Core Technologies

| Technology            | Purpose                                       |
|-----------------------|-----------------------------------------------|
| **FastAPI**           | Web framework for API layer                   |
| **Pydantic**          | API input/output validation and app settings  |
| **SQLModel**          | ORM and data modeling                         |
| **PostgreSQL**        | Durable data storage                          |
| **Uvicorn**           | ASGI server to run FastAPI                    |
| **bcrypt**            | Secure password hashing                       |
| **JOSE**              | JWT tokens handling                           |
| **unique-namer**      | Generate unique and memorable lottery names   |

### Containerization

Service is containerized using **Docker** and orchestrated with  **Docker Compose**.

### Scheduled Task

Task schedulling is done using **cron** in the container.

### Development and Testing

Service is using **pytest** for testing and **GitHub Actions** for CI/CD.

## Author

Vladislav Neverov
