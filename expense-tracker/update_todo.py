import os

file_path = r"e:\visualStudioProjects\Portfolio Projects\Expense Tracker\expense-tracker\TODO.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    ("### 1.1 Environment Setup\n-", "### 1.1 Environment Setup\n#### Task 1 — Environment Setup\n-"),
    ("### 1.2 Run the Backend Server\n-", "### 1.2 Run the Backend Server\n#### Task 2 — Run the Backend Server\n-"),
    ("### 1.3 Understand the Backend Structure\n-", "### 1.3 Understand the Backend Structure\n#### Task 3 — Understand the Backend Structure\n-"),
    ("### 2.1 Start the Database with Docker\n-", "### 2.1 Start the Database with Docker\n#### Task 4 — Start the Database with Docker\n-"),
    ("### 2.2 Create a `.env` File for Local Development\n-", "### 2.2 Create a `.env` File for Local Development\n#### Task 5 — Create a `.env` File for Local Development\n-"),
    ("Open `backend/app/database.py`. You will complete **Tasks 1-6** in order.", "Open `backend/app/database.py`. You will complete **Tasks 6-11** in order."),
    ("#### Task 1 — Database Configuration (URL Construction)", "#### Task 6 — Database Configuration (URL Construction)"),
    ("#### Task 2 — Create the Async Engine and Session Factory", "#### Task 7 — Create the Async Engine and Session Factory"),
    ("#### Task 3 — Implement `get_db()` (Dependency Injection)", "#### Task 8 — Implement `get_db()` (Dependency Injection)"),
    ("#### Task 4 — Implement `check_db_connection()` (Async Health Check)", "#### Task 9 — Implement `check_db_connection()` (Async Health Check)"),
    ("#### Task 5 — Implement `check_db_connection_sync()` (Sync Health Check)", "#### Task 10 — Implement `check_db_connection_sync()` (Sync Health Check)"),
    ("#### Task 6 — Implement `init_db()` (Table Creation)", "#### Task 11 — Implement `init_db()` (Table Creation)"),
    ("### 2.4 Verify End-to-End Database Connection\n-", "### 2.4 Verify End-to-End Database Connection\n#### Task 12 — Verify End-to-End Database Connection\n-"),
    ("### 3.1 Install Auth Dependencies\n-", "### 3.1 Install Auth Dependencies\n#### Task 13 — Install Auth Dependencies\n-"),
    ("#### Task 10 — Update User Model for Auth", "#### Task 14 — Update User Model for Auth"),
    ("#### Task 11 — Auth Request/Response Schemas", "#### Task 15 — Auth Request/Response Schemas"),
    ("#### Task 12 — Create `backend/app/auth.py`", "#### Task 16 — Create `backend/app/auth.py`"),
    ("#### Task 13 — Create Auth Middleware / Dependency", "#### Task 17 — Create Auth Middleware / Dependency"),
    ("#### Task 14 — Create Auth Endpoints", "#### Task 18 — Create Auth Endpoints"),
    ("#### Task 15 — Auth Context and Token Management", "#### Task 19 — Auth Context and Token Management"),
    ("#### Task 16 — Login and Register Pages", "#### Task 20 — Login and Register Pages"),
    ("#### Task 17 — Verify Authentication End-to-End", "#### Task 21 — Verify Authentication End-to-End"),
    ("#### Task 18 — User Endpoints", "#### Task 22 — User Endpoints"),
    ("#### Task 19 — Expense Endpoints", "#### Task 23 — Expense Endpoints"),
    ("#### Task 20 — Error Handling", "#### Task 24 — Error Handling"),
    ("#### Task 21 — Category Endpoints", "#### Task 25 — Category Endpoints"),
    ("#### Task 22 — Security Headers", "#### Task 26 — Security Headers"),
    ("### 4.6 Verify with Swagger\n-", "### 4.6 Verify with Swagger\n#### Task 27 — Verify with Swagger\n-"),
    ("### 5.1 Get the Frontend Running\n-", "### 5.1 Get the Frontend Running\n#### Task 28 — Get the Frontend Running\n-"),
    ("### 5.2 Implement the Backend Health Check (Task 7)", "### 5.2 Implement the Backend Health Check\n#### Task 29 — Implement the Backend Health Check"),
    ("- [ ] Complete **Task 7**:", "- [ ] Complete **Task 29**:"),
    ("#### Task 25 — Setup Feature Flags Context", "#### Task 30 — Setup Feature Flags Context"),
    ("#### Task 26 — Build the Core Pages", "#### Task 31 — Build the Core Pages"),
    ("#### Task 27 — Add Client-Side Routing", "#### Task 32 — Add Client-Side Routing"),
    ("#### Task 28 — Create a Reusable API Service Layer", "#### Task 33 — Create a Reusable API Service Layer"),
    ("#### Task 29 — Verify Docker Compose Works", "#### Task 34 — Verify Docker Compose Works"),
    ("#### Task 30 — Add Frontend to Docker Compose", "#### Task 35 — Add Frontend to Docker Compose"),
    ("#### Task 31 — Terraform Deployment", "#### Task 36 — Terraform Deployment"),
    ("#### Task 32 — Backend Feature Flags", "#### Task 37 — Backend Feature Flags"),
    ("#### Task 33 — Production Hardening", "#### Task 38 — Production Hardening"),
    ("#### Task 34 — Backend Tests", "#### Task 39 — Backend Tests"),
    ("#### Task 35 — Frontend Tests", "#### Task 40 — Frontend Tests"),
    ("#### Task 36 — Load Testing", "#### Task 41 — Load Testing"),
    ("#### Task 37 — CI Pipeline", "#### Task 42 — CI Pipeline"),
    ("#### Task 38 — CD Pipeline", "#### Task 43 — CD Pipeline"),
    ("#### Task 39 — Branch Protection", "#### Task 44 — Branch Protection"),
    ("#### Task 23 — Observability", "#### Task 45 — Observability"),
    ("#### Task 24 — Rate Limiting", "#### Task 46 — Rate Limiting"),
    ("#### Task 40 — Performance & Caching", "#### Task 47 — Performance & Caching"),
    ("#### Task 41 — Incident Response", "#### Task 48 — Incident Response"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("TODO.md updated successfully.")
