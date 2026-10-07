import redis

def main():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    print(r.ping())  # True — confirma que la conexión funciona

    r.delete("cola_demo")  # empieza limpio
    r.lpush("cola_demo", "A")  # LPUSH = insertar al INICIO de la lista
    r.lpush("cola_demo", "B")
    r.lpush("cola_demo", "C")

    print(r.lrange("cola_demo", 0, -1))  # ['C', 'B', 'A'] — ver la lista completa, sin sacar nada

    print(r.rpop("cola_demo"))  # 'A' — RPOP saca del FINAL → el primero que entró, FIFO
    print(r.rpop("cola_demo"))  # 'B'
    print(r.rpop("cola_demo"))  # 'C'
    print(r.rpop("cola_demo"))  # None — lista vacía, Redis no lanza error, devuelve None


if __name__ == "__main__":
    main()
