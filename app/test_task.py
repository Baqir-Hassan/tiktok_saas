from app.tasks.tasks import ping

if __name__ == "__main__":
    print("Sending a test 'ping' task to the Celery worker...")
    result = ping.delay()
    print("Task sent. Task ID:", result.id)
    print("Waiting for result...")
    print(f"Result: '{result.get(timeout=10)}'")
