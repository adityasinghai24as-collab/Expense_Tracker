from locust import HttpUser, task, between

class ExpenseTrackerUser(HttpUser):
    # Simulate a user waiting between 1 and 5 seconds between requests
    wait_time = between(1, 5)

    @task(3)
    def check_health(self):
        """Hit the health endpoint (fast)"""
        self.client.get("/health")

    @task(1)
    def check_db_health(self):
        """Hit the DB health endpoint (tests DB connection pool)"""
        self.client.get("/health/db")
        
    @task(2)
    def fetch_categories(self):
        """Hit the categories endpoint (tests database read performance)"""
        self.client.get("/categories")
