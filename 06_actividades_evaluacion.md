# Actividades de aprendizaje y evaluación — Unidad 3

## Actividades de aprendizaje

- Implementar un método `insertar_ordenado(dato)` en `ListaSimple` (3.3) que inserte manteniendo el orden ascendente, sin usar `sorted()`.
- Agregar un método `invertir()` a `ListaDoble` (3.3) que invierta la lista en el lugar (sin crear una lista nueva), intercambiando `siguiente` y `anterior` de cada nodo.
- Extender `ListaCircular` (3.3) con un método `rotar(n)` que mueva el puntero `self.ultimo` n posiciones hacia adelante, simulando n turnos de Round Robin sin recorrer toda la lista de nuevo.
- Implementar `evaluar_postfija` (3.1) para que soporte también paréntesis y funciones simples como `raiz(9)`.
- Reescribir el BFS de 3.2 usando `Pila` en vez de `Cola` (esto es, de hecho, un DFS) y comparar el orden de visita resultante en el mismo grafo — documentar la diferencia.
- Implementar una `Cola` usando **dos pilas** (un ejercicio clásico): una pila para encolar, otra para desencolar, transfiriendo elementos entre ellas cuando sea necesario.

## Evaluación sugerida

| Evidencia | Qué valora |
|---|---|
| `ListaSimple.insertar_ordenado` funcionando | Manejo de punteros con una condición extra de comparación |
| `ListaDoble.invertir()` en el lugar | Comprensión real de los dos punteros — no solo copiar valores a una lista nueva |
| `ListaCircular.rotar(n)` | Aplicación de aritmética modular sobre punteros, no solo sobre índices de arreglo |
| Postfija con paréntesis/funciones | Extensión de un algoritmo base a un caso más general |
| DFS con pila, comparado contra BFS | Comprensión de que la *misma estructura de datos base* con disciplina de acceso distinta produce comportamientos completamente diferentes |
| Cola con dos pilas | Ejercicio de "traducir" una estructura en términos de otra — habilidad transferible a estructuras más complejas |
| Examen de conceptos | Nodo, punteros, costos O() de cada operación, LIFO vs. FIFO, cuándo usar cada estructura |
