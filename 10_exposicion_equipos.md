# Exposición por equipos — Unidad 3: Estructuras lineales

Cada equipo expone **lo que ya está documentado y verificado en este repositorio** — no se investiga nada externo. La exposición debe incluir una **demo en vivo** corriendo el código real (no solo diapositivas): se ejecuta, se muestra la salida, y se explica qué significa.

## Equipos y material

**Equipo 1 — Pilas: representación, notaciones y balanceo**
Material: [01_pilas.md](01_pilas.md)
Qué debe cubrir:
- Representación en memoria de una pila (arreglo vs. enlazada) y las operaciones básicas (`push`/`pop`/`peek`).
- Las tres notaciones: infija, prefija y postfija — con la demo de `evaluar_prefija()` corriendo en vivo.
- El algoritmo de balanceo de paréntesis y la conversión infija→postfija (shunting-yard).
Tiempo: 12-15 min.

**Equipo 2 — Colas: representación, tipos y BFS**
Material: [02_colas.md](02_colas.md)
Qué debe cubrir:
- Representación en memoria (arreglo circular vs. enlazada con dos punteros frente/final).
- Tipos de cola: simple, circular, bicola — con el wraparound circular corriendo en vivo.
- BFS usando una cola como estructura base — demo recorriendo un grafo de ejemplo.
Tiempo: 12-15 min.

**Equipo 3 — Listas simples vs. doblemente ligadas**
Material: [03_listas_simples.md](03_listas_simples.md), [04_listas_doblemente_ligadas.md](04_listas_doblemente_ligadas.md)
Qué debe cubrir:
- Inserción, búsqueda y eliminación en lista simple — con el flowchart de `eliminar` (caso cabeza/medio/no encontrado).
- Por qué la lista doble logra O(1) en ambos extremos y la simple no.
- Demo en vivo de `insertar_final` y `eliminar` de nodo intermedio, mostrando el diagrama de punteros paso a paso.
Tiempo: 12-15 min.

**Equipo 4 — Listas circulares y usos reales**
Material: [05_listas_circulares.md](05_listas_circulares.md)
Qué debe cubrir:
- Cómo funciona una lista circular (sin `None` al final) y el caso especial de eliminar el único nodo.
- La tabla de usos reales: blockchain, caché LRU, Round Robin — explicar **por qué** cada uno usa esta estructura y no otra.
Tiempo: 10-12 min.

**Equipo 5 — Pilas y colas aplicadas: historial de navegador + descargas**
Material: [07_practica_pilas_colas.md](07_practica_pilas_colas.md)
Qué debe cubrir:
- Demo en vivo del historial de navegador implementado con pila (atrás/adelante).
- Demo en vivo de la cola de descargas (orden de llegada, cancelación).
- Conectar cada demo con la estructura de datos exacta que la hace posible.
Tiempo: 12-15 min.

**Equipo 6 — Redis como cola real: arquitectura y comparación**
Material: [08_practica_colas_redis.md](08_practica_colas_redis.md)
Qué debe cubrir:
- Arquitectura cliente-servidor de Redis y por qué la ejecución de comandos es atómica (un solo hilo).
- Demo en vivo: persistencia RDB/AOF (el experimento de perder datos sin volumen vs. conservarlos con volumen).
- Cola de prioridad con `ZADD`/`ZPOPMIN`, y la tabla comparativa Redis vs. RabbitMQ vs. Kafka.
Tiempo: 15 min.

**Equipo 7 — Worker pools, colas etiquetadas y el problema C10K**
Material: [09_practica_workers_colas_etiquetadas.md](09_practica_workers_colas_etiquetadas.md)
Qué debe cubrir:
- La analogía del mesero (síncrono vs. asíncrono) y por qué nació la asincronía (problema C10K, línea de tiempo `select()`→`epoll`→nginx→Node.js→`asyncio`).
- Demo en vivo: escalado de 1→2→4 workers con `asyncio.Queue` (medido, no teórico).
- Demo en vivo: colas etiquetadas por prioridad con `BRPOP` en Redis real.
Tiempo: 15 min.

## Estructura sugerida de cada exposición (igual para todos)

1. **Qué problema resuelve** la estructura/técnica (2 min).
2. **Cómo funciona por dentro** — el mecanismo, no solo la definición (3-4 min).
3. **Demo en vivo** corriendo el código real del repositorio (5-7 min, el corazón de la exposición).
4. **Conclusión**: en qué situación real se usaría esto y en cuál no (1-2 min).

## Entregables

1. Exposición siguiendo la estructura de arriba.
2. Demo en vivo — si algo falla en el momento, se explica el error y se diagnostica frente al grupo (no se penaliza fallar, se penaliza no saber por qué falló).
3. El código corrido debe ser **exactamente** el del archivo del repositorio correspondiente a su equipo — no una reescritura.

## Evaluación sugerida

| Criterio | Peso | Qué se revisa |
|---|---|---|
| Dominio del mecanismo (no solo la definición) | 30% | El equipo explica *por qué* funciona así, no solo *qué* hace |
| Demo en vivo funcionando | 30% | Evidencia de que de verdad corrieron el código — la parte que no se puede fingir |
| Manejo de un fallo en vivo | 15% | Si algo truena, qué tan bien diagnostican el problema frente al grupo |
| Conexión con un caso de uso real | 15% | Explican cuándo sí y cuándo no usar esa estructura, con criterio, no de memoria |
| Claridad y tiempo | 10% | Se ajustan al tiempo asignado, todos los integrantes participan |
