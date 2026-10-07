import redis, time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.delete("tareas")

for i in range(1, 4):
    tarea = f"tarea-{i}"
    r.lpush("tareas", tarea)
    print(f"[productor] encolé {tarea}")
    time.sleep(1)