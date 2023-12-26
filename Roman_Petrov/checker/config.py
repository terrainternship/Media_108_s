# celeryconfig.py
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Europe/Dublin"
enable_utc = True
container_address = "whisper"
container_ports = [9000]
worker_max_tasks_per_child = 5
worker_prefetch_multiplier = 10
