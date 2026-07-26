# Observability Guide (Grafana, Loki, Promtail)

This guide explains how to use the local **PLG (Promtail, Loki, Grafana)** observability stack that is configured via Docker Compose to monitor and debug the Expense Tracker application.

## 1. How the Stack Works

*   **Promtail**: Scrapes local logs from your Docker containers (specifically `backend` and `postgres`). It attaches labels (like `container_name`) and ships the logs to Loki.
*   **Loki**: The highly scalable log database. It indexes the labels and stores the log text.
*   **Grafana**: The visualization dashboard UI where you can query, view, and analyze the logs stored in Loki.

---

## 2. Accessing Grafana

1. **Start the Stack**: Ensure your Docker Compose environment is running. Open your terminal in the `expense-tracker` root directory and run:
   ```bash
   docker compose up -d
   ```
2. **Open Grafana**: Open your web browser and navigate to: **[http://localhost:3000](http://localhost:3000)**
3. **Login Details**: Grafana is configured for seamless local development. You do **not** need to log in! It uses anonymous authentication (`GF_AUTH_ANONYMOUS_ENABLED=true`), dropping you straight into the dashboard with Admin privileges.

---

## 3. Querying Logs in Grafana (Step-by-Step)

The best way to view your logs is using the **Explore** view in Grafana.

### Step 1: Open the Explore View
1. Look at the left-hand sidebar in Grafana.
2. Click on the **Explore** icon (it looks like a compass 🧭).

### Step 2: Select Your Data Source
1. Look at the top-left corner of the Explore page.
2. Click the dropdown menu and select **Loki** (it is pre-configured for you).

### Step 3: Write a Query using LogQL
You can search your logs using **LogQL** (Loki Query Language). Type these into the main query bar and press `Shift + Enter` (or click the blue "Run query" button):

*   **View all Backend API logs:**
    ```logql
    {container_name="expense-tracker-backend"}
    ```
*   **View all Database (Postgres) logs:**
    ```logql
    {container_name="expense-tracker-postgres"}
    ```
*   **Search for errors in the backend:**
    *(The `|=` operator means "contains")*
    ```logql
    {container_name="expense-tracker-backend"} |= "error"
    ```
*   **Track a specific user or action:**
    ```logql
    {container_name="expense-tracker-backend"} |= "/auth/login"
    ```

### Step 4: Using the Visual Log Browser (No Code Required)
If you don't want to write LogQL manually, use the visual builder:
1. Click the **Log browser** button (next to the query input bar).
2. A menu will appear. Under **"1. Select labels"**, choose `container_name`.
3. Under **"2. Select values"**, choose the container you want to inspect (e.g., `expense-tracker-backend`).
4. Click the blue **Show logs** button. Your logs will appear in real-time below!

---

## 4. Setting up a Persistent Dashboard (Optional)

While the "Explore" tab is great for ad-hoc debugging, you can create a permanent dashboard:

1. Click the **Dashboards** icon in the sidebar (four squares) and click **New Dashboard**.
2. Click **Add visualization**.
3. Select **Loki** as the data source.
4. Enter your query, for example: `{container_name="expense-tracker-backend"}`
5. On the right-hand panel, under "Panel options", give it a title like "Backend Logs".
6. Click **Save** in the top right corner.

---

## 5. Troubleshooting the Stack

*   **No logs appearing?**
    *   Verify Promtail is running: `docker ps | grep promtail`
    *   Check Promtail logs for connection errors: `docker logs expense-tracker-promtail`
*   **Grafana won't load?**
    *   Verify Grafana is running and port `3000` is not blocked by another service.
