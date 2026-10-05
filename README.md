# Unidad 3 — Estructuras lineales

**Materia:** Estructura de Datos (AED-1026)
**Grupo:** S3C — Aula ED12
**Horario:** Lunes 19:00–21:00 · Martes 20:00–21:00 · Miércoles 19:00–21:00
**Lenguaje:** Python 3

Sigue el temario oficial: después de [Unidad 1](../estructura_de_datos_u1/README.md) (introducción, TDA, complejidad) y Unidad 2 (recursividad — pendiente), esta unidad construye las primeras estructuras reales basadas en **nodos y punteros** — pilas, colas y listas, la base de todo lo que viene en árboles y grafos.

## Contenido

- [01_pilas.md](01_pilas.md) — 3.1 Pilas: representación en memoria, operaciones básicas, notaciones infija/prefija/postfija, aplicaciones (balanceo de paréntesis, evaluar postfija/prefija, deshacer, conversión infija→postfija)
- [02_colas.md](02_colas.md) — 3.2 Colas: representación en memoria, operaciones básicas, tipos (simples, circulares, bicolas), aplicaciones (simulación de atención, BFS)
- [03_listas_simples.md](03_listas_simples.md) — 3.3 Listas — simplemente enlazadas: nodo, inserción, búsqueda, eliminación
- [04_listas_doblemente_ligadas.md](04_listas_doblemente_ligadas.md) — 3.3 Listas — doblemente enlazadas: O(1) en ambos extremos
- [05_listas_circulares.md](05_listas_circulares.md) — 3.3 Listas — circulares y buffer circular, más una tabla de usos reales de listas simples/dobles/circulares (blockchain, caché LRU, Round Robin, etc.)
- [06_actividades_evaluacion.md](06_actividades_evaluacion.md) — Actividades de aprendizaje y evaluación
- [07_practica_pilas_colas.md](07_practica_pilas_colas.md) — Práctica guiada: historial de navegador (pilas) + cola de descargas (colas)
- [08_practica_colas_redis.md](08_practica_colas_redis.md) — Práctica guiada: qué es Redis (arquitectura cliente-servidor, persistencia RDB/AOF, con diagramas), colas reales con Python (patrón productor/consumidor bloqueante, cola de prioridad) + comparación con RabbitMQ y Kafka

## Nota sobre el código

Todos los ejemplos de esta unidad son Python **ejecutado y verificado** antes de publicarse — implementaciones desde cero con clases `Nodo`, seguidas de la versión real con `collections.deque` para comparar. Cada salida de ejemplo (incluidos los checkpoints de la práctica) coincide exactamente con lo que se obtiene al correr el código.

## Fuentes

- Programa sinóptico oficial AED-1026 — TecNM
- docs.python.org/3/library/collections.html#collections.deque
