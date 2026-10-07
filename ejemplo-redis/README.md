# Ejemplo Redis: cola con listas

Práctica de una cola FIFO usando listas de Redis (`LPUSH` + `RPOP`) desde Python, con RedisInsight para ver los datos.

## Requisitos

- Docker
- [uv](https://docs.astral.sh/uv/) (gestor de proyectos Python)

## 1. Crear la red de Docker

```bash
docker network create redis-net
```

Esta red permite que RedisInsight encuentre a Redis por su nombre, `redis-practica`.

## 2. Levantar Redis

```bash
docker run -d --name redis-practica --network redis-net -p 6379:6379 redis:7-alpine
```

- `--network redis-net`: conecta el contenedor a la red del paso 1.
- `-p 6379:6379`: publica el puerto para que el código Python llegue a Redis por `localhost:6379`.

Comprobar que responde:

```bash
docker exec -it redis-practica redis-cli ping
```

Debe responder `PONG`.

## 3. Levantar RedisInsight

```bash
docker run -d --name redisinsight --network redis-net -p 5540:5540 redis/redisinsight:latest
```

## 4. Conectar RedisInsight a Redis

1. Abrir http://localhost:5540 y aceptar los términos.
2. Pulsar **Add Redis database**.
3. Llenar así:
   - **Host:** `redis-practica`. No usar `localhost`, porque dentro del contenedor de RedisInsight `localhost` es el propio RedisInsight.
   - **Port:** `6379`
   - Usuario y contraseña vacíos.
4. Pulsar **Add Redis Database**.

## 5. Crear el proyecto Python

```bash
uv init ejemplo-redis
cd ejemplo-redis
uv add redis
```

Poner en `main.py` el código de la cola y ejecutarlo:

```bash
uv run main.py
```

Salida esperada:

```
True
['C', 'B', 'A']
A
B
C
None
```

## 6. Ver los datos en RedisInsight

Al terminar, el script saca todos los elementos, así que la clave `cola_demo` queda vacía y Redis la borra. Por eso no aparece en RedisInsight. Para verla, abrir la pestaña **Workbench** o **CLI** de RedisInsight y ejecutar:

```
LPUSH cola_demo A B C
LRANGE cola_demo 0 -1
```

Después ir a **Browser**: aparecerá la clave `cola_demo` de tipo *list*.

## 7. Productor y consumidor

Patrón productor/consumidor con dos programas separados que se comunican por la lista `tareas`:

- `productor.py`: vacía la lista `tareas` y encola `tarea-1`, `tarea-2` y `tarea-3` con `LPUSH`, una por segundo.
- `consumidor.py`: espera tareas con `BRPOP` y las procesa conforme llegan, hasta 3. Si pasan 10 segundos sin recibir nada, imprime `timeout, no llegó nada` y termina.

`BRPOP` es la versión bloqueante de `RPOP`: si la lista está vacía no devuelve `None` al instante, sino que espera a que llegue algo (hasta el `timeout`). Así el consumidor no tiene que preguntar en bucle si hay tareas.

Ejecutar en dos terminales, **primero el consumidor**:

```bash
# Terminal 1
uv run consumidor.py
```

```bash
# Terminal 2 (antes de que pasen 10 segundos)
uv run productor.py
```

Salida del productor:

```
[productor] encolé tarea-1
[productor] encolé tarea-2
[productor] encolé tarea-3
```

Salida del consumidor, que aparece a la vez, una línea por segundo:

```
[consumidor] procesando tarea-1
[consumidor] procesando tarea-2
[consumidor] procesando tarea-3
```

Si se ejecuta primero el productor, las tareas quedan guardadas en Redis y el consumidor las procesa todas de inmediato al arrancar.

## Resumen de conexiones

| Desde | Dirección de Redis |
|---|---|
| Código Python (en el equipo) | `localhost:6379` |
| RedisInsight (en Docker) | `redis-practica:6379` |

## Si algo falla

- **El nombre del contenedor ya está en uso:** ya existe un contenedor con ese nombre. Arrancarlo con `docker start redis-practica redisinsight` en vez de crearlo otra vez.
- **RedisInsight no conecta:** revisar que los dos contenedores estén en la red con `docker network inspect redis-net`.
