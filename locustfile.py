from locust import HttpUser, LoadTestShape, task


class JsonPlaceHolder(HttpUser):

    host = 'https://jsonplaceholder.typicode.com'
    @task
    def add_post(self):
        req_body = {
            'title': 'foo',
            'body': 'bar',
            'userId': 1
        }
        with self.client.post('/posts', json=req_body, catch_response=True) as response:
           if response.status_code == 201:
              response.success()


class StagesShape(LoadTestShape):
    """Run three one-minute stages, then stop the test automatically."""

    # Duration is the cumulative stage end time in seconds from test start.
    # Users is the target concurrent user count; spawn_rate is users per second.
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},
        {"duration": 120, "users": 20, "spawn_rate": 2},
        {"duration": 180, "users": 10, "spawn_rate": 2},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]

        return None
