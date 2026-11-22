import logging

from locust import HttpUser, LoadTestShape, task

# Locust configures logging (level set by --loglevel) and writes to stderr,
# so these messages show up in the GitHub Actions job log.
logger = logging.getLogger("locustfile")


class JsonPlaceHolder(HttpUser):

    host = 'https://jsonplaceholder.typicode.com'

    @task
    def add_post(self):
        req_body = {
            'title': 'foo',
            'body': 'bar',
            'userId': 1
        }
        try:
            with self.client.post('/posts', json=req_body, catch_response=True) as response:
                # status_code 0 means the request never got a response
                # (connection error, timeout, DNS failure, ...).
                if response.status_code == 0:
                    logger.error("POST /posts got no response: %s", response.error)
                    response.failure(f"No response: {response.error}")
                    return

                if response.status_code != 201:
                    logger.warning(
                        "POST /posts returned %s (expected 201): %s",
                        response.status_code, response.text[:200],
                    )
                    response.failure(f"Unexpected status {response.status_code}")
                    return

                try:
                    data = response.json()
                except ValueError:
                    logger.error("POST /posts returned invalid JSON: %s", response.text[:200])
                    response.failure("Invalid JSON in response")
                    return

                if 'id' not in data:
                    logger.warning("POST /posts response has no 'id' field: %s", data)
                    response.failure("Response missing 'id'")
                    return

                logger.debug("POST /posts created post id=%s", data['id'])
                response.success()
        except Exception:
            # Anything unexpected in our own code: log the traceback and keep
            # the simulated user running instead of killing it.
            logger.exception("Unexpected error in add_post")


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
