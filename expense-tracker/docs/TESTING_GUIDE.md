# Testing Guide

This guide covers all the testing frameworks and methodologies used in the Expense Tracker project. We currently employ two types of testing: **Unit Testing** (via Pytest) and **Load Testing** (via Locust).

## 1. Unit Testing (Pytest)

Unit tests verify that individual endpoints and functions behave correctly under various conditions.

### Setup and Architecture
- **Framework**: `pytest` combined with `pytest-asyncio` for native async support.
- **HTTP Client**: `httpx.AsyncClient` is used to simulate HTTP requests against our FastAPI backend.
- **Database Strategy**: We test against a real PostgreSQL database. To keep tests fast and prevent data pollution, `tests/conftest.py` wraps every test in a **nested database transaction**. When a test finishes, the transaction is immediately rolled back, leaving the database pristine.
- **Mocking**: We use Python's built-in `unittest.mock.patch` to mock external side-effects (such as `BackgroundTasks` or sending emails via Resend). This ensures tests are hermetic and run instantly without hanging the event loop.

### How to Run Unit Tests
Make sure you are in the `backend` directory and your virtual environment is active.
```bash
cd backend
pytest -v
```
*The `-v` flag provides verbose output, showing the name and status of each individual test.*

### Writing New Tests
1. Create a new file in the `backend/tests/` directory starting with `test_` (e.g., `test_expenses.py`).
2. Add `@pytest.mark.asyncio` above any async test function.
3. Inject the `client` fixture to make HTTP requests, or the `db_session` fixture to query the test database directly.

---

## 2. Load Testing (Locust)

Load testing verifies that our application and database connection pooling can handle thousands of concurrent users without dropping requests or crashing.

### Setup and Architecture
- **Framework**: `Locust`
- **Script**: `backend/load_tests/locustfile.py` defines the behavior of a "swarm" of virtual users.
- **Database Optimization**: Our SQLAlchemy `async_engine` is optimized with `pool_size=20` and `max_overflow=10` to manage high concurrency. Query logging (`echo`) is disabled outside of development to prevent console bottlenecks.

### How to Run Load Tests
Make sure your backend server is running! Then, open a new terminal:
```bash
cd backend
locust -f load_tests/locustfile.py
```
1. Open your browser and navigate to `http://localhost:8089`.
2. Enter the number of users to simulate (e.g., `1000`).
3. Enter the spawn rate (e.g., `50` users per second).
4. Enter the host (e.g., `http://localhost:8000`).
5. Click **Start swarming** and watch the real-time statistics and charts!
