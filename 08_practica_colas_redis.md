# Práctica guiada: colas reales con Python y Redis

Práctica complementaria a [3.2 Colas](02_colas.md). Hasta ahora construiste colas que viven en la memoria de un solo programa — en cuanto el proceso termina, la cola desaparece, y solo ese proceso puede usarla. **Redis** resuelve ambas limitaciones: es una base de datos en memoria que vive en su propio proceso (o servidor), así que la cola **persiste** y puede ser compartida por **varios programas distintos** — exactamente como funcionan las colas de tareas reales (Celery, Sidekiq, AWS SQS) detrás de aplicaciones en producción.

> Verificado ejecutando cada paso de esta práctica contra un servidor Redis real (Docker, Redis 7) con `redis-py`, y también contra un RabbitMQ real (Docker) con `pika` para la sección comparativa — incluido el patrón productor/consumidor bloqueante (con timestamps reales) y el enrutamiento por patrón de RabbitMQ. Kafka se documenta por referencia oficial, sin ejecutarse en este sandbox (requiere un clúster más pesado) — queda marcado explícitamente donde corresponde.

## ¿Qué es Redis, exactamente?

**Redis** (*REmote DIctionary Server*) es un servidor de estructuras de datos en memoria: un programa aparte que corre en segundo plano (como `smbd` en la práctica de Samba, o `crond` en la de Cron) y que guarda todo en **RAM**, no en un archivo en disco como SQLite o Postgres. Eso es lo que lo hace extremadamente rápido — leer de RAM es miles de veces más rápido que leer de disco — pero también lo que explica **por qué necesitas pensar en la persistencia** como algo aparte, no automático.

### Arquitectura: cliente-servidor sobre TCP

Redis **no es una librería que importas** — es un **proceso independiente** al que tu programa se conecta por red (aunque sea la misma máquina), igual que te conectas a una base de datos. Por eso dos procesos Python totalmente distintos (tu `productor.py` y tu `consumidor.py`) pueden compartir la misma cola: ambos son solo **clientes** hablándole al mismo servidor.

```
┌─────────────────┐                              ┌──────────────────────────────┐
│  productor.py     │                              │       Servidor Redis           │
│  (proceso Python)  │ ──── TCP, puerto 6379 ────► │  (proceso aparte, en su propia │
└─────────────────┘                              │   memoria RAM)                  │
                                                     │                                  │
┌─────────────────┐                              │  clave "tareas" → [ C, B, A ]   │
│  consumidor.py     │                              │  clave "cola_prioridad" → {...} │
│  (proceso Python)  │ ──── TCP, puerto 6379 ────► │                                  │
└─────────────────┘                              └──────────────────────────────┘
                                                              │
                                                     (opcional) RDB/AOF
                                                              ▼
                                                        ┌───────────┐
                                                        │  disco      │
                                                        └───────────┘
```

Cada vez que llamas `r.lpush(...)` o `r.rpop(...)` en Python, lo que realmente pasa es: tu programa **envía un mensaje de texto por la red** (ej. literalmente los bytes `LPUSH tareas tarea-1`) al proceso de Redis, que lo ejecuta y responde — igual que un navegador le pide una página a un servidor web. `redis-py` solo te ahorra escribir esos mensajes a mano.

### ¿Dónde quedan los datos si Redis se reinicia?

Por defecto, **en ningún lado fuera de la RAM** — si el proceso de Redis muere sin haber guardado nada a disco, los datos se pierden. Esto lo verificamos de dos formas distintas:

```python
# Experimento 1 — Redis SIN volumen de disco
r.set("clave_importante", "este dato vive solo en RAM")
print(r.get("clave_importante"))   # 'este dato vive solo en RAM'

# ...se destruye el contenedor y se crea uno nuevo (simula un reinicio real)...

print(r.get("clave_importante"))   # None — el dato desapareció, estaba solo en RAM
```

```python
# Experimento 2 — Redis CON volumen de disco + guardado explícito
r.set("clave_importante", "este dato SI se guarda en disco")
r.bgsave()   # BGSAVE: escribe un snapshot (RDB) a disco en segundo plano

# ...se destruye el contenedor y se crea uno nuevo, pero reutilizando el mismo volumen...

print(r.get("clave_importante"))   # 'este dato SI se guarda en disco' — sí sobrevivió
```

**Checkpoint real de esta práctica:** el primer experimento devolvió `None` tras recrear el contenedor; el segundo (con `-v` montando una carpeta del host a `/data`, más `bgsave()`) devolvió el valor intacto. Esa diferencia — RAM pura vs. RAM + snapshot a disco — es la decisión de diseño más importante que tomas al usar Redis en un proyecto real: ¿puedo darme el lujo de perder estos datos si el servidor se cae, o no?

| Mecanismo | Qué hace | Cuándo usarlo |
|---|---|---|
| Sin persistencia (por defecto) | Todo vive solo en RAM | Caché, datos desechables, colas de tareas de vida muy corta |
| **RDB** (snapshot) | Guarda una "foto" completa de los datos cada cierto tiempo, o con `bgsave()` manual | Buen balance — pierdes como máximo los cambios desde el último snapshot |
| **AOF** (*Append Only File*) | Registra **cada comando de escritura** en un log, como el journal de un sistema de archivos | Máxima durabilidad — casi nada se pierde, a cambio de más uso de disco |

### ¿Por qué no hay condiciones de carrera entre el productor y el consumidor?

Redis ejecuta los comandos **uno a la vez**, en un único hilo (por eso un servidor Redis típico usa un solo núcleo de CPU para procesar comandos). Si dos clientes mandan `lpush` casi al mismo tiempo, Redis los encola internamente y los ejecuta en algún orden, pero **nunca a medias** — no existe el escenario de la condición de carrera que viste en Sistemas Operativos 2.5, donde dos hilos leen el mismo valor antes de que cualquiera escriba. Cada comando de Redis es **atómico** por diseño.

### Diagrama: la secuencia completa de `BRPOP` bloqueante (Paso 4)

```
Tiempo →

consumidor.py:  brpop("tareas")
                      │
                      │  (bloqueado, 0% CPU, esperando — NO está en un bucle preguntando)
                      │
productor.py:         │        lpush("tareas", "tarea-1")
                      │                  │
                      ▼                  ▼
                 Redis despierta al consumidor en el MISMO instante
                      │
                      ▼
consumidor.py:  recibe ("tareas", "tarea-1") → imprime "procesando tarea-1"
                      │
                      │  vuelve a bloquearse esperando la siguiente
                      ▼
                 brpop("tareas")  ...se repite con tarea-2, tarea-3...
```

Esto es exactamente el mismo mecanismo que ya conoces de las colas de un sistema operativo: un proceso bloqueado (Sistemas Operativos, 2.2) no consume CPU mientras espera — el planificador lo ignora hasta que el evento que espera (en este caso, un `lpush`) realmente ocurre.

## Por qué Redis y no solo `collections.deque`

| | `deque` (Unidad 3) | Cola en Redis |
|---|---|---|
| Dónde vive | En la memoria de un solo proceso Python | En un servidor aparte, con su propia memoria |
| Quién puede usarla | Solo ese proceso | Cualquier proceso/máquina que se conecte a Redis |
| Sobrevive a un reinicio del programa | No | Sí (mientras Redis siga corriendo) |
| Caso de uso típico | Un algoritmo dentro de un solo script (BFS, etc.) | Repartir trabajo entre varios *workers*, comunicar microservicios |

La operación en sí sigue siendo FIFO — lo que cambia es **dónde** vive la cola y **quién** puede tocarla.

## Requisitos previos

- Docker instalado.
- Python 3 con `uv` o `pip`.

## Paso 1 — Levantar un servidor Redis real

```bash
docker run -d --name redis-practica -p 6379:6379 redis:7-alpine
docker logs redis-practica
```

**Checkpoint esperado:** el log debe terminar con `Ready to accept connections tcp`.

## Paso 2 — Instalar el cliente Python

```bash
pip install redis
# o, con uv:
uv add redis
```

## Paso 3 — Las listas de Redis *son* colas (y pilas) de fábrica

Una **lista de Redis** es, por dentro, la misma lista doblemente enlazada que construiste en 3.3 — por eso insertar/eliminar en cualquiera de los dos extremos es O(1). El comando que uses decide si la usas como cola o como pila:

```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
print(r.ping())   # True — confirma que la conexión funciona

r.delete("cola_demo")          # empieza limpio
r.lpush("cola_demo", "A")      # LPUSH = insertar al INICIO de la lista
r.lpush("cola_demo", "B")
r.lpush("cola_demo", "C")

print(r.lrange("cola_demo", 0, -1))   # ['C', 'B', 'A'] — ver la lista completa, sin sacar nada

print(r.rpop("cola_demo"))   # 'A' — RPOP saca del FINAL → el primero que entró, FIFO
print(r.rpop("cola_demo"))   # 'B'
print(r.rpop("cola_demo"))   # 'C'
print(r.rpop("cola_demo"))   # None — lista vacía, Redis no lanza error, devuelve None
```

**Checkpoint esperado:** el primer `rpop()` debe devolver `'A'` — el primer elemento insertado, confirmando FIFO. Si usaras `lpop()` (sacar también del inicio) en vez de `rpop()`, estarías implementando una **pila** (LIFO) con los mismos dos comandos de inserción.

| Quieres... | Insertar con | Sacar con |
|---|---|---|
| Cola (FIFO) | `lpush` | `rpop` |
| Pila (LIFO) | `lpush` | `lpop` |

## Paso 4 — El problema de "esperar a que llegue algo": `BRPOP`

Si un *worker* necesita esperar a que aparezca trabajo, la opción ingenua es preguntar en bucle (`while True: tarea = r.rpop(...)`) — eso desperdicia CPU revisando una y otra vez una cola vacía. Redis ofrece **`brpop`** (*blocking RPOP*): el proceso se bloquea sin consumir CPU hasta que algo llegue, o hasta un tiempo límite.

**Archivo `consumidor.py`:**
```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

for _ in range(3):
    resultado = r.brpop("tareas", timeout=10)   # bloquea hasta 10s esperando una tarea
    if resultado is None:
        print("timeout, no llegó nada")
        break
    _, tarea = resultado    # brpop devuelve (nombre_de_la_lista, valor)
    print(f"[consumidor] procesando {tarea}")
```

**Archivo `productor.py`:**
```python
import redis, time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.delete("tareas")

for i in range(1, 4):
    tarea = f"tarea-{i}"
    r.lpush("tareas", tarea)
    print(f"[productor] encolé {tarea}")
    time.sleep(1)
```

**Pruébalo en dos terminales** (el orden importa — arranca primero el consumidor):

```bash
# Terminal 1
python consumidor.py

# Terminal 2 (ábrela mientras la 1 sigue corriendo)
python productor.py
```

**Checkpoint esperado:** el consumidor imprime `"procesando tarea-1"` casi al mismo instante en que el productor imprime `"encolé tarea-1"` — no tuvo que sondear, Redis lo despertó en cuanto llegó el dato. Verificado en esta práctica con timestamps reales: la diferencia entre el `print` del productor y el del consumidor fue de milisegundos, no del intervalo de un bucle de sondeo.

## Paso 5 — Bonus: cola de prioridad con *Sorted Sets*

Una cola FIFO normal no sirve cuando algunos elementos deben atenderse antes que otros sin importar el orden de llegada (ej. un ticket "urgente" que llegó después de uno "normal"). Redis resuelve esto con un **Sorted Set**: cada elemento tiene un *score* numérico, y siempre puedes sacar el de menor score primero.

```python
r.delete("cola_prioridad")
r.zadd("cola_prioridad", {
    "ticket-normal-1": 5,
    "ticket-urgente": 1,     # score más bajo = se atiende primero
    "ticket-normal-2": 5,
    "ticket-vip": 2,
})

while True:
    resultado = r.zpopmin("cola_prioridad")   # saca y elimina el de menor score
    if not resultado:
        break
    ticket, score = resultado[0]
    print(f"atendiendo {ticket} (prioridad {score})")
```

**Checkpoint esperado:**
```
atendiendo ticket-urgente (prioridad 1.0)
atendiendo ticket-vip (prioridad 2.0)
atendiendo ticket-normal-1 (prioridad 5.0)
atendiendo ticket-normal-2 (prioridad 5.0)
```

Entre dos elementos con el mismo score (`ticket-normal-1` y `ticket-normal-2`), Redis los desempata por orden lexicográfico — en la práctica, esto es lo más cerca de una "cola FIFO con prioridades" que puedes construir sin escribir tu propia estructura híbrida.

## Paso 6 — Limpieza

```bash
docker stop redis-practica
docker rm redis-practica
```

---

## Qué acabas de comprobar, en términos de la teoría (3.2)

| Lo que hiciste | Concepto que confirma |
|---|---|
| `lrange` mostró la lista completa en Redis | Una lista de Redis es, por dentro, la misma lista ligada de 3.3 — aquí persistida en otro proceso. |
| `rpop` sacó los elementos en el mismo orden en que entraron | FIFO funciona idéntico, sin importar si la cola vive en tu script o en un servidor aparte. |
| `brpop` despertó exactamente cuando llegó la tarea, sin sondeo | La misma idea de "esperar eficientemente" que resuelve el planificador de un sistema operativo al bloquear un proceso (Sistemas Operativos, 2.2) en vez de hacerlo girar en un bucle vacío. |
| `zpopmin` rompió el orden FIFO a propósito | Prueba de que FIFO es una **elección de diseño**, no una ley física — cuando el problema lo pide (prioridades), se cambia de estructura. |

## Más allá de Redis: dónde encajan RabbitMQ y Kafka

Redis es un buen punto de entrada porque sus colas son solo listas con comandos familiares — pero en la industria, cuando el problema es específicamente "mensajería entre sistemas", suele usarse una herramienta **diseñada para eso**: RabbitMQ o Kafka. Los tres resuelven "mover datos de un productor a un consumidor de forma confiable", pero con modelos de entrega radicalmente distintos.

### RabbitMQ — un cartero con reglas de enrutamiento

RabbitMQ es un **message broker** tradicional que habla el protocolo **AMQP**. La diferencia clave frente a una lista de Redis: en Redis, un mensaje lo consume **el primero que haga `rpop`** — se acabó, nadie más lo ve. En RabbitMQ, un mismo mensaje puede entregarse a **varias colas distintas** según reglas de enrutamiento, sin que el productor sepa cuántos consumidores hay ni cómo se llaman.

```python
import pika

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
canal = conn.channel()

# Un "exchange" tipo topic enruta por patrón — no es una cola, es un repartidor de correo
canal.exchange_declare(exchange="eventos", exchange_type="topic")

canal.queue_declare(queue="cola_pagos")
canal.queue_declare(queue="cola_auditoria")

canal.queue_bind(exchange="eventos", queue="cola_pagos", routing_key="pago.*")
canal.queue_bind(exchange="eventos", queue="cola_auditoria", routing_key="#")  # "#" = todo

canal.basic_publish(exchange="eventos", routing_key="pago.creado", body="Pago 123 creado")
canal.basic_publish(exchange="eventos", routing_key="usuario.creado", body="Usuario 456 creado")
```

**Verificado:** el mensaje `"Pago 123 creado"` llegó a **ambas** colas (coincide con el patrón `pago.*` de `cola_pagos`, y con `#` de `cola_auditoria`, que recibe todo); `"Usuario 456 creado"` solo llegó a `cola_auditoria`. Ese enrutamiento por patrón — sin que el código del productor conozca a los consumidores — es exactamente lo que una lista de Redis no ofrece de fábrica.

**Cuándo usarlo:** cuando necesitas **garantías de entrega** (confirmaciones/`ack`, reintentos, colas de mensajes muertos) y **enrutamiento flexible** entre microservicios — ej. un pedido de e-commerce que debe notificar a facturación, inventario y envíos al mismo tiempo, cada uno con su propia cola.

### Kafka — un registro que no se borra

> Nota: a diferencia de Redis y RabbitMQ (verificados arriba con contenedores reales), Kafka requiere un clúster más pesado de levantar (broker + metadatos) — lo siguiente sigue la documentación oficial de Apache Kafka, sin ejecutarse en este sandbox.

Kafka resuelve un problema distinto: no es un "buzón que se vacía al leer", es un **log distribuido** — los mensajes (llamados *eventos*) se **anexan** a un *topic* y **no se borran** al ser leídos. Varios consumidores pueden leer el mismo *topic* de forma independiente, cada uno llevando su propio marcador de "hasta dónde ya leí" (*offset*).

```python
# Conceptual — sintaxis real de kafka-python, no ejecutada aquí
from kafka import KafkaProducer, KafkaConsumer

productor = KafkaProducer(bootstrap_servers="localhost:9092")
productor.send("pagos", b"Pago 123 creado")

consumidor = KafkaConsumer("pagos", bootstrap_servers="localhost:9092", group_id="facturacion")
for mensaje in consumidor:
    print(mensaje.value)   # puede releerse después, el mensaje sigue ahí
```

**La diferencia que más importa:** en Redis/RabbitMQ, una vez que alguien consume el mensaje, se va. En Kafka, el mensaje queda en el *topic* durante un tiempo configurable (horas, días, o para siempre) — un consumidor nuevo que se conecte mañana puede **reprocesar el historial completo** desde el principio. Por eso Kafka se usa para *streaming* de datos a gran escala (clics de usuarios, métricas, logs) donde el volumen es enorme y distintos equipos quieren leer el mismo flujo de eventos para cosas distintas (analítica, alertas, entrenamiento de modelos), no solo "repartir trabajo una vez".

Un *topic* de Kafka también se divide en **particiones** — cada partición mantiene **su propio** orden FIFO (la misma garantía que ya verificaste con `rpop`), pero el orden solo está garantizado *dentro* de una partición, no entre todas — el precio que paga por poder escalar a millones de mensajes por segundo repartiendo la carga entre varios discos/máquinas.

### Comparación lado a lado

| | Redis (listas) | RabbitMQ | Kafka |
|---|---|---|---|
| Modelo | Cola simple | *Message broker* con enrutamiento | Log distribuido (*streaming*) |
| El mensaje se borra al leerlo | Sí | Sí (tras `ack`) | No — persiste según retención configurada |
| Un mensaje a varios consumidores | No, sin Pub/Sub aparte | Sí, vía *exchanges* y *bindings* | Sí, cada *consumer group* lee todo el *topic* |
| Reproducir el historial | No | No | Sí — es su característica central |
| Orden garantizado | Siempre (una sola lista) | Por cola | Solo dentro de cada partición |
| Mejor para... | Prototipos, colas simples, caché | Microservicios con reglas de enrutamiento y garantías de entrega | Streaming de eventos a gran escala, analítica en tiempo real |
| Qué tan pesado es operarlo | Ligero | Medio | Pesado (requiere más infraestructura) |

**La pregunta que decide cuál usar:** ¿necesitas que el mensaje desaparezca una vez atendido (Redis/RabbitMQ), o necesitas que el historial completo quede disponible para quien quiera leerlo después (Kafka)? Esa sola pregunta descarta dos de las tres opciones en la mayoría de los casos reales.

## Actividades de aprendizaje

- Modifica el Paso 4 para tener **dos consumidores** corriendo al mismo tiempo (dos terminales con `consumidor.py`) y un solo productor — observa que cada tarea la procesa **solo uno** de los dos consumidores, nunca ambos (así es como Redis reparte trabajo entre varios *workers* en producción).
- Implementa una cola circular de tamaño fijo (3.3) usando `LPUSH` + `LTRIM` (`r.ltrim("lista", 0, N-1)` después de cada inserción) para quedarte solo con los N elementos más recientes — el mismo comportamiento del `BufferCircular` de la Unidad 3, pero persistido en Redis.
- Investiga qué pasa si dos productores hacen `lpush` al mismo tiempo sobre la misma lista — ¿Redis garantiza que no se pierda ningún elemento? (pista: Redis procesa comandos uno a la vez, de forma atómica, por diseño).
- Compara el tiempo de `rpop` sobre una lista con 10 elementos contra una con 1,000,000 — ¿sigue siendo O(1), como predice la teoría de listas ligadas?
