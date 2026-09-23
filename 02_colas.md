# 3.2 Colas (queues)

## FIFO: el primero en entrar es el primero en salir

Una cola es como la fila de una caja registradora: entras por atrás, sales por adelante. El primero en llegar es el primero en ser atendido — *First In, First Out*.

```
salida ← [A][B][C][D] ← entrada
         frente      final
```

| Operación | Qué hace |
|---|---|
| `encolar(dato)` | Agrega un elemento al **final** |
| `desencolar()` | Quita y devuelve el elemento del **frente** |
| `frente()` | Mira el elemento del frente sin quitarlo |

## El error clásico: usar una `list` mal

```python
cola = []
cola.append("A")
cola.append("B")
cola.append("C")

primero = cola.pop(0)   # ¡NO hagas esto! — pop(0) es O(n): mueve TODOS los elementos restantes
```

`pop(0)` funciona, pero es lento — cada vez que sacas del frente, Python recorre y desplaza todos los elementos que quedan (viste esto exacto en 1.5: insertar/eliminar al inicio de un arreglo es O(n)). Para una cola real, se necesita O(1) en ambos extremos — exactamente lo que resuelve una lista doblemente ligada (3.3).

## Implementación correcta, con lista doble por dentro

```python
class NodoCola:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class Cola:
    def __init__(self):
        self.frente_nodo = None
        self.final_nodo = None
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self.frente_nodo is None

    def encolar(self, dato):
        """O(1) — gracias a guardar el puntero final_nodo."""
        nuevo = NodoCola(dato)
        if self.esta_vacia():
            self.frente_nodo = self.final_nodo = nuevo
        else:
            self.final_nodo.siguiente = nuevo
            self.final_nodo = nuevo
        self._tamano += 1

    def desencolar(self):
        """O(1) — sin desplazar nada, a diferencia de list.pop(0)."""
        if self.esta_vacia():
            raise IndexError("desencolar() sobre cola vacía")
        dato = self.frente_nodo.dato
        self.frente_nodo = self.frente_nodo.siguiente
        if self.frente_nodo is None:
            self.final_nodo = None
        self._tamano -= 1
        return dato

    def frente(self):
        if self.esta_vacia():
            raise IndexError("frente() sobre cola vacía")
        return self.frente_nodo.dato

    def __repr__(self):
        elementos = []
        actual = self.frente_nodo
        while actual is not None:
            elementos.append(repr(actual.dato))
            actual = actual.siguiente
        return "Cola[frente→ " + ", ".join(elementos) + " ←final]"
```

## Probándola

```python
cola = Cola()
cola.encolar("cliente 1")
cola.encolar("cliente 2")
cola.encolar("cliente 3")
print(cola)                     # Cola[frente→ 'cliente 1', 'cliente 2', 'cliente 3' ←final]
print(cola.desencolar())        # 'cliente 1' — el primero que llegó
print(cola.frente())            # 'cliente 2'
print(len(cola))                # 2
```

## En Python real: `collections.deque`

Igual que con la pila, no necesitas construir la clase a mano en producción — `deque` ya resuelve esto con O(1) real en ambos extremos:

```python
from collections import deque

cola = deque()
cola.append("cliente 1")     # encolar
cola.append("cliente 2")
print(cola.popleft())          # desencolar — O(1), sin el problema de list.pop(0)
```

## Aplicación 1: simular una fila de atención

```python
from collections import deque
import random

fila = deque()
for i in range(1, 6):
    fila.append(f"Ticket-{i}")

print("Orden de atención:")
while fila:
    print(" atendiendo:", fila.popleft())
```

## Aplicación 2: BFS — recorrido por niveles

El algoritmo de **búsqueda en anchura** (*Breadth-First Search*), que verás formalmente con árboles y grafos más adelante, usa una cola para garantizar que explora nivel por nivel:

```python
def bfs(grafo, inicio):
    """grafo: dict {nodo: [vecinos]}. Devuelve el orden en que BFS visita los nodos."""
    visitados = {inicio}
    cola = deque([inicio])
    orden = []

    while cola:
        actual = cola.popleft()      # el más antiguo en la cola — por eso es "por niveles"
        orden.append(actual)
        for vecino in grafo[actual]:
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(vecino)
    return orden


grafo = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B"],
    "E": ["B", "F"],
    "F": ["C", "E"],
}
print(bfs(grafo, "A"))   # ['A', 'B', 'C', 'D', 'E', 'F'] — nivel por nivel desde A
```

**Por qué una cola y no una pila:** si usaras una pila aquí (DFS — profundidad primero), explorarías una rama completa antes de mirar sus vecinos. La cola garantiza que revisas todos los vecinos directos de A antes de pasar a los vecinos de los vecinos — eso es "por niveles".

## Tipos de colas: simples, circulares y bicolas

| Tipo | Cómo funciona | Cuándo se usa |
|---|---|---|
| **Simple** (la de arriba) | Entra solo por el final, sale solo por el frente. | El caso general — atención por orden de llegada. |
| **Circular** | Sobre un arreglo de tamaño fijo, reutiliza los índices con aritmética modular en vez de desperdiciar espacio al frente. | Buffers de tamaño fijo, la misma técnica que el `BufferCircular` de listas circulares (3.3). |
| **Bicola** (*deque*, doble extremo) | Se puede insertar y eliminar **por ambos extremos**, no solo frente/final fijos. | Cuando necesitas la flexibilidad de pila y cola a la vez — es justo lo que ya usaste como `deque`. |

```python
from collections import deque

bicola = deque()
bicola.append("B")       # entra por el final
bicola.appendleft("A")   # entra por el frente
bicola.append("C")
print(list(bicola))        # ['A', 'B', 'C']
print(bicola.popleft())    # 'A' — sale por el frente
print(bicola.pop())        # 'C' — sale por el final
print(list(bicola))        # ['B']
```

`deque` es, en realidad, una **bicola** — por eso te sirvió tanto para implementar la cola simple (usando solo un extremo cada vez) como, en 3.3, para la lista doblemente ligada. Una cola normal es una bicola a la que decides usar solo dos de sus cuatro operaciones posibles (`append` + `popleft`).

## Conexión con la teoría

Pilas y colas son, en el fondo, la misma idea (contenedor lineal + dos operaciones) con la disciplina de acceso invertida. Ambas son la base de estructuras y algoritmos que vienen después: pilas para DFS y evaluación de expresiones; colas para BFS y para el propio planificador Round Robin que ya viste en Sistemas Operativos 2.4 — la cola de procesos "Listos" es, literalmente, una cola.
