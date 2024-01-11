from celery import Celery


class CeleryConfig:
    broker_url = "redis://localhost:6379/0"
    result_backend = "redis://localhost:6379/0"


app = Celery("tasks")
app.config_from_object(CeleryConfig)


@app.task(bind=True, track_started=True)
def add(self, x, y):
    print(f"before adding {x}, {y}")
    total = x + y
    print(f"after adding {x}, {y}, {total}")
    return total
