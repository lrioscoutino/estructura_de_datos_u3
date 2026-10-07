import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

for _ in range(3):
    resultado = r.brpop("tareas", timeout=10)   # bloquea hasta 10s esperando una tarea
    if resultado is None:
        print("timeout, no llegó nada")
        break
    _, tarea = resultado    # brpop devuelve (nombre_de_la_lista, valor)
    print(f"[consumidor] procesando {tarea}")