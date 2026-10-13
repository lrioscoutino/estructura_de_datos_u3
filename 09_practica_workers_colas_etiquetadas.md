# Práctica guiada: workers concurrentes y colas etiquetadas (asíncrono)

Esta práctica continúa directamente la de [Redis y colas](08_practica_colas_redis.md): ahí viste **una** cola con **un** consumidor. En un sistema real casi nunca es así — hay **varios workers** procesando en paralelo, y las tareas suelen venir **etiquetadas por prioridad o tipo** (ej. "urgente" vs "normal" vs "baja", o "emails" vs "reportes" vs "notificaciones"). Esto es exactamente lo que hacen por dentro sistemas como Celery, Sidekiq o las colas de AWS SQS con *dead-letter queues*.

Requisito: Python 3, librería `redis` (`uv pip install redis` o `pip install redis`), y un Redis real corriendo (reutilizamos el contenedor de la práctica anterior: `docker start redis-practica`).

---

## Antes de empezar: qué significa "asíncrono" (para explicar en clase)

Esta sección es la que el docente puede usar para introducir el tema antes de que el estudiante toque código. Sin esto, `async`/`await` se memorizan como sintaxis mágica — con esto, tienen una razón concreta de por qué existen.

### El problema que resuelve lo asíncrono

Imagina un mesero que atiende **una mesa a la vez**: toma la orden, va a la cocina, **se queda parado esperando** a que el platillo esté listo, lo lleva, y solo entonces atiende la siguiente mesa. Si hay 10 mesas, el restaurante es lentísimo — no porque el mesero trabaje poco, sino porque pasa la mayor parte del tiempo **esperando sin hacer nada útil**.

Un mesero asíncrono hace otra cosa: toma la orden de la mesa 1, la manda a la cocina, y **mientras se cocina**, atiende a la mesa 2, luego a la mesa 3 — y cuando la cocina avisa que el platillo 1 está listo, lo va a entregar. Nunca se queda parado esperando: siempre que algo está "en espera" (la cocina cocinando), aprovecha ese tiempo para atender otra cosa.

Ese "algo en espera" en programación casi siempre es **entrada/salida (E/S)**: esperar una respuesta de red (una API, una base de datos), esperar que el disco termine de escribir, esperar que Redis responda. El CPU, durante esa espera, no está haciendo ningún cálculo — está parado. La programación asíncrona existe para que, durante esas esperas, el programa pueda **atender otra tarea** en vez de quedarse parado.

### Los tres términos que hay que distinguir

| Término | Qué es, en una frase | Analogía del restaurante |
|---|---|---|
| **Corutina** (`async def`) | Una función especial que puede "pausarse" en un punto de espera y dejar que otra corutina corra mientras tanto. | Una orden de mesa: se puede "pausar" en el punto de "esperando a la cocina". |
| **`await`** | El punto exacto donde una corutina dice "aquí voy a esperar algo — mientras tanto, que corra alguien más". | El momento en que el mesero deja la orden en la cocina y va a atender otra mesa. |
| **Event loop (bucle de eventos)** | El "mesero" real: el componente que decide, en cada momento, cuál corutina pausada ya puede seguir porque lo que esperaba ya llegó. `asyncio.run()` es quien lo arranca. | El mesero mismo, decidiendo a qué mesa atender según quién ya tiene su platillo listo. |

Una pieza clave que se presta a confusión: **todo esto corre en un solo hilo, un solo CPU a la vez**. No hay dos meseros — hay un mesero muy eficiente que nunca se queda parado. Por eso en el Paso 1 de esta práctica, cuando decimos "4 workers", no son 4 procesadores trabajando en paralelo de verdad — son 4 corutinas que se van turnando el único hilo cada vez que una de ellas llega a un `await` y "cede el paso".

### Por qué sí funciona el ejemplo de esta práctica (y cuándo NO funcionaría)

En el Paso 1, cada "tarea" hace `await asyncio.sleep(0.2)` — eso simula una espera de E/S (como esperar la respuesta de una API). Como ninguna tarea necesita el CPU *de verdad* durante esos 0.2 segundos, el mesero (event loop) puede atender a las otras 3 tareas durante exactamente esa ventana de tiempo libre. Por eso 4 "workers" terminan en una cuarta parte del tiempo: **no están calculando en paralelo, están aprovechando los huecos de espera de los demás.**

Si en cambio cada tarea fuera un cálculo pesado de verdad (por ejemplo, sumar un millón de números), no habría ningún hueco de espera que aprovechar — el CPU estaría ocupado todo el tiempo con una sola tarea, y `asyncio` **no ayudaría en nada** (de hecho, varias corutinas compitiendo por el mismo hilo para cálculo puro pueden ser hasta más lentas que hacerlo todo en orden). Para ese caso se necesita paralelismo real con varios procesos (`multiprocessing`), no concurrencia con un solo hilo.

**Resumen para el pizarrón:**

| | ¿Para qué sirve? | Ejemplo típico |
|---|---|---|
| `asyncio` (un hilo, corutinas) | Muchas tareas que **esperan** mucho y calculan poco (E/S) | Servir miles de conexiones de red, consultar una API, leer/escribir en Redis |
| `threading` (varios hilos, un CPU por el GIL en Python) | Parecido a asyncio para E/S, pero con librerías que no son `async` | Leer varios archivos con una librería vieja que no soporta `await` |
| `multiprocessing` (varios procesos, varios CPUs) | Tareas que **calculan** mucho (CPU), poco o nada de espera | Procesar imágenes, cálculos científicos, compresión de archivos |

Con esta base, el Paso 1 deja de ser "until syntax funciona, no sé por qué" y pasa a ser una comprobación concreta de algo que ya se explicó: *si las tareas son de espera (E/S), más corutinas concurrentes reducen el tiempo casi proporcionalmente — y eso es justo lo que vas a medir.*

---

## Paso 1 — Worker pool con `asyncio`: ¿cuánto ayuda agregar más workers?

### El problema

Un solo worker procesa las tareas una por una. Si cada tarea tarda un tiempo fijo en completarse (por ejemplo, porque espera una respuesta de red), agregar más workers que trabajen **concurrentemente** debería reducir el tiempo total casi proporcionalmente — pero "debería" hay que comprobarlo, no asumirlo.

### Lo que vas a construir

```python
import asyncio
import time

async def worker(nombre, cola, resultados):
    while True:
        tarea = await cola.get()
        if tarea is None:
            cola.task_done()
            break
        inicio = time.monotonic()
        await asyncio.sleep(0.2)  # simula trabajo de E/S (ej. llamar a una API)
        duracion = time.monotonic() - inicio
        resultados.append((nombre, tarea, duracion))
        cola.task_done()

async def correr_con_n_workers(n_workers, n_tareas):
    cola = asyncio.Queue()
    for i in range(n_tareas):
        cola.put_nowait(f"tarea_{i}")
    resultados = []

    tareas_worker = [
        asyncio.create_task(worker(f"worker_{w}", cola, resultados))
        for w in range(n_workers)
    ]

    inicio = time.monotonic()
    await cola.join()  # espera a que se procesen todas las tareas
    duracion_total = time.monotonic() - inicio

    for _ in range(n_workers):
        cola.put_nowait(None)  # señal de apagado para cada worker
    await asyncio.gather(*tareas_worker)

    return duracion_total, resultados

async def main():
    for n_workers in [1, 2, 4]:
        duracion, resultados = await correr_con_n_workers(n_workers, n_tareas=8)
        reparto = {}
        for nombre, _, _ in resultados:
            reparto[nombre] = reparto.get(nombre, 0) + 1
        print(f"workers={n_workers}  tiempo_total={duracion:.3f}s  reparto={reparto}")

asyncio.run(main())
```

### Salida real (verificada)

```
workers=1  tiempo_total=1.608s  reparto={'worker_0': 8}
workers=2  tiempo_total=0.803s  reparto={'worker_0': 4, 'worker_1': 4}
workers=4  tiempo_total=0.401s  reparto={'worker_0': 2, 'worker_1': 2, 'worker_2': 2, 'worker_3': 2}
```

### Qué acaba de pasar

Con 8 tareas de 0.2s cada una: 1 worker tarda ~1.6s (8 × 0.2), 2 workers ~0.8s (la mitad), 4 workers ~0.4s (la cuarta parte). El reparto de tareas también es parejo: cada worker tomó exactamente su parte proporcional porque todos piden de la **misma cola compartida** (`asyncio.Queue`) — nadie se queda sin trabajo mientras otro worker está ocioso, a diferencia de si hubieras repartido las tareas de antemano con `tarea[i % n_workers]`.

Esto funciona tan limpio aquí porque `asyncio.sleep()` simula E/S (esperar una red, un disco) — el truco del `async/await` es que mientras un worker *espera*, el CPU puede atender a los demás. Si la tarea fuera cómputo puro (sin esperar nada, ej. calcular algo pesado), `asyncio` por sí solo **no** ayudaría — ahí se necesitarían procesos reales (`multiprocessing`), no corutinas.

### Ejercicio para ti

Cambia `n_tareas` a `20` y agrega `n_workers=8` a la lista. ¿La mejora de 4→8 workers es tan grande como la de 1→2? ¿Por qué el beneficio de agregar más workers no es infinito?

---

## Paso 2 — Colas etiquetadas por prioridad con Redis (verificado contra un Redis real)

### El problema

No todas las tareas son igual de urgentes. Un worker que atiende "lo que le toque" sin ningún criterio puede quedarse procesando algo trivial mientras una alerta crítica espera en la fila. La solución es tener **varias colas, una por etiqueta**, y que el worker siempre revise primero las de mayor prioridad.

### Lo que vas a construir

```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.flushdb()

COLAS_POR_PRIORIDAD = ["cola:urgente", "cola:normal", "cola:baja"]

# Productor: mete tareas etiquetadas con distinta prioridad, sin ningun orden particular
tareas = [
    ("cola:normal", "enviar_reporte_mensual"),
    ("cola:baja", "limpiar_logs_viejos"),
    ("cola:urgente", "alerta_servidor_caido"),
    ("cola:normal", "generar_factura"),
    ("cola:urgente", "notificar_pago_rechazado"),
    ("cola:baja", "optimizar_indices"),
]

for cola, tarea in tareas:
    r.lpush(cola, tarea)
    print(f"productor -> {cola}: {tarea}")

print()
print("=== Worker etiquetado: siempre revisa urgente antes que normal antes que baja ===")

# BRPOP acepta varias listas y devuelve la primera que tenga datos,
# respetando el orden de los argumentos -> asi se implementa prioridad real
while True:
    resultado = r.brpop(COLAS_POR_PRIORIDAD, timeout=1)
    if resultado is None:
        break
    cola_atendida, tarea = resultado
    print(f"worker procesa [{cola_atendida}] {tarea}")
```

### Salida real (verificada)

```
productor -> cola:normal: enviar_reporte_mensual
productor -> cola:baja: limpiar_logs_viejos
productor -> cola:urgente: alerta_servidor_caido
productor -> cola:normal: generar_factura
productor -> cola:urgente: notificar_pago_rechazado
productor -> cola:baja: optimizar_indices

=== Worker etiquetado: siempre revisa urgente antes que normal antes que baja ===
worker procesa [cola:urgente] alerta_servidor_caido
worker procesa [cola:urgente] notificar_pago_rechazado
worker procesa [cola:normal] enviar_reporte_mensual
worker procesa [cola:normal] generar_factura
worker procesa [cola:baja] limpiar_logs_viejos
worker procesa [cola:baja] optimizar_indices
```

### Qué acaba de pasar — el detalle que hay que entender bien

El productor metió las 6 tareas **en un orden mezclado** (normal, baja, urgente, normal, urgente, baja). Sin embargo, el worker las atendió agrupadas estrictamente por prioridad: primero **las dos** de `cola:urgente`, luego **las dos** de `cola:normal`, y al final **las dos** de `cola:baja` — exactamente en el orden en que aparecen en la lista `COLAS_POR_PRIORIDAD` que le pasamos a `BRPOP`.

Esto es la clave: `BRPOP` revisa las listas **en el orden en que se las das**, y devuelve el primer elemento que encuentra en la primera lista no vacía. No es que Redis "sepa" que `urgente` es más importante — es que tú codificaste esa prioridad en el orden de los argumentos. Si invirtieras el orden (`["cola:baja", "cola:normal", "cola:urgente"]`), lo urgente se atendería al final — este es exactamente el tipo de bug silencioso que pasa en producción si alguien reordena una lista de configuración sin entender qué hace.

### Ejercicio para ti

Agrega una cuarta cola `cola:critica` **al principio** de `COLAS_POR_PRIORIDAD` y mete una tarea ahí a la mitad de la lista `tareas`. Sin correr el código, predice en qué orden la va a atender el worker. Luego corre y comprueba.

---

## Paso 3 — Juntando todo: pool de workers asíncronos sobre colas etiquetadas

### El problema

Esto es lo más parecido a un sistema de colas real (Celery, Sidekiq, BullMQ): **varios workers corriendo al mismo tiempo**, todos escuchando las **mismas colas etiquetadas por prioridad**, compitiendo por tomar la siguiente tarea disponible.

### Lo que vas a construir

```python
import asyncio
import time
import redis.asyncio as aredis

COLAS_POR_PRIORIDAD = ["cola:urgente", "cola:normal", "cola:baja"]

async def worker(nombre, cliente, log):
    while True:
        resultado = await cliente.brpop(COLAS_POR_PRIORIDAD, timeout=1)
        if resultado is None:
            break
        cola_bytes, tarea = resultado
        inicio = time.monotonic()
        await asyncio.sleep(0.15)  # simula el trabajo real (I/O: enviar email, llamar API, etc.)
        duracion = time.monotonic() - inicio
        log.append((nombre, cola_bytes, tarea, duracion))

async def main():
    cliente = aredis.Redis(host="localhost", port=6379, decode_responses=True)
    await cliente.flushdb()

    tareas = [
        ("cola:normal", "enviar_reporte_mensual"),
        ("cola:baja", "limpiar_logs_viejos"),
        ("cola:urgente", "alerta_servidor_caido"),
        ("cola:normal", "generar_factura"),
        ("cola:urgente", "notificar_pago_rechazado"),
        ("cola:baja", "optimizar_indices"),
        ("cola:urgente", "fuga_de_memoria_detectada"),
        ("cola:normal", "sincronizar_inventario"),
    ]
    for cola, tarea in tareas:
        await cliente.lpush(cola, tarea)

    log = []
    inicio_total = time.monotonic()
    workers = [asyncio.create_task(worker(f"worker_{i}", cliente, log)) for i in range(3)]
    await asyncio.gather(*workers)
    duracion_total = time.monotonic() - inicio_total

    print(f"3 workers concurrentes, {len(tareas)} tareas, tiempo total={duracion_total:.3f}s\n")
    for nombre, cola, tarea, dur in log:
        print(f"  {nombre} <- [{cola}] {tarea}  ({dur:.3f}s)")

    await cliente.aclose()

asyncio.run(main())
```

### Salida real (verificada)

```
3 workers concurrentes, 8 tareas, tiempo total=1.533s

  worker_0 <- [cola:urgente] alerta_servidor_caido  (0.151s)
  worker_1 <- [cola:urgente] notificar_pago_rechazado  (0.151s)
  worker_2 <- [cola:urgente] fuga_de_memoria_detectada  (0.151s)
  worker_0 <- [cola:normal] enviar_reporte_mensual  (0.151s)
  worker_1 <- [cola:normal] generar_factura  (0.151s)
  worker_2 <- [cola:normal] sincronizar_inventario  (0.151s)
  worker_0 <- [cola:baja] limpiar_logs_viejos  (0.151s)
  worker_1 <- [cola:baja] optimizar_indices  (0.151s)
```

### Qué acaba de pasar

Con las 3 tareas `urgente`, los tres workers las toman **al mismo tiempo** (una cada uno) y las procesan en paralelo — por eso tardan ~0.15s en total para esas tres, no 0.45s. Lo mismo pasa con las 3 de `normal`. Al final quedan solo 2 de `baja`, así que solo 2 workers trabajan y el tercero se queda sin nada que hacer en esa ronda.

Fíjate en el tiempo total reportado (~1.53s): es más alto de lo que esperarías solo sumando el trabajo real (3 rondas × 0.15s ≈ 0.45s). La diferencia viene de `timeout=1` en `BRPOP` — cuando la cola ya está vacía, cada worker se queda **esperando hasta 1 segundo completo** antes de rendirse y terminar. Esto no es un error: es el mismo tipo de parámetro de configuración que existe en cualquier sistema de colas real, y es exactamente el tipo de detalle que hay que medir, no asumir — por eso esta práctica, como las anteriores, se verifica corriendo el código de verdad en vez de describir "cómo debería comportarse".

Este patrón — N workers, M colas etiquetadas por prioridad, cada worker compitiendo por la siguiente tarea disponible — es, con detalles de implementación distintos, exactamente cómo funcionan por dentro Celery (con colas de RabbitMQ o Redis), Sidekiq (Redis) y las colas gestionadas de AWS/GCP.

### Ejercicio para ti

Baja `timeout=1` a `timeout=0.1` en los tres workers y vuelve a correr. ¿Cuánto baja el tiempo total reportado? Relaciona esto con una decisión real: ¿qué desventaja tendría un `timeout` demasiado bajo en un sistema de colas de producción? (Pista: piensa en cuántas veces por segundo cada worker terminaría preguntándole a Redis "¿hay algo nuevo?" si no hay nada que procesar.)

---

## Resumen de lo que cubriste

| Concepto | Dónde lo viste |
|---|---|
| Worker pool concurrente | Paso 1 — escalado casi lineal de 1→2→4 workers sobre una cola compartida (`asyncio.Queue`) |
| Colas etiquetadas / por prioridad | Paso 2 — `BRPOP` sobre varias listas de Redis, el orden de los argumentos define la prioridad real |
| Asíncrono + etiquetado combinados | Paso 3 — pool de workers `asyncio` compitiendo por tareas en colas de Redis etiquetadas, el patrón detrás de Celery/Sidekiq |
