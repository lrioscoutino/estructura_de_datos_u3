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

`pop(0)` funciona, pero es lento — cada vez que sacas del frente, Python recorre y desplaza todos los elementos que quedan (viste esto exacto en 1.5: insertar/eliminar al inicio de un arreglo es O(n)). Para una cola real, se necesita O(1) en ambos extremos.

## Representación en memoria: arreglo circular vs. lista ligada

Igual que con las pilas (3.1.1), una cola se puede representar de dos formas:

### Opción A — arreglo circular (memoria estática)

Un arreglo fijo por sí solo tiene el problema de `pop(0)`: si "frente" siempre fuera el índice 0, desencolar obligaría a recorrer todo. La solución es dejar que `frente` **se mueva** por el arreglo, y cuando llegue al final, dar la vuelta al principio con aritmética modular — la misma técnica de las listas y buffers circulares que viste más adelante en esta unidad (3.3).

```
Capacidad 3, después de encolar A, B, C:

 [ A | B | C ]        frente=0, cuenta=3
   0   1   2

Después de desencolar() una vez (sale A):

 [ _ | B | C ]        frente=1, cuenta=2
   0   1   2

Después de encolar(D) — D ocupa el índice 0, que quedó libre:

 [ D | B | C ]        frente=1, cuenta=3
   0   1   2
```

```python
class ColaArreglo:
    def __init__(self, capacidad):
        self.capacidad = capacidad
        self.datos = [None] * capacidad
        self.frente = 0
        self.cuenta = 0          # cuántos elementos hay realmente ocupados

    def esta_vacia(self):
        return self.cuenta == 0

    def esta_llena(self):
        return self.cuenta == self.capacidad

    def encolar(self, dato):
        if self.esta_llena():
            raise OverflowError("cola llena")
        indice_libre = (self.frente + self.cuenta) % self.capacidad   # % es lo que "da la vuelta"
        self.datos[indice_libre] = dato
        self.cuenta += 1

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("cola vacía")
        dato = self.datos[self.frente]
        self.datos[self.frente] = None
        self.frente = (self.frente + 1) % self.capacidad
        self.cuenta -= 1
        return dato


c = ColaArreglo(3)
c.encolar("A"); c.encolar("B"); c.encolar("C")
print(c.desencolar())    # 'A'
c.encolar("D")            # ocupa el índice 0, liberado por el desencolar anterior — sin mover nada
print(c.datos)              # ['D', 'B', 'C']
```

**El operador `%` es la clave:** sin él, `frente` avanzaría siempre hacia adelante y nunca podría reutilizar los índices bajos que ya quedaron libres — el arreglo se "acabaría" aunque técnicamente hubiera huecos disponibles al principio.

### Opción B — lista ligada (memoria dinámica)

Sin límite de tamaño, creciendo bajo demanda. Se necesitan **dos punteros**: `frente_nodo` (por dónde se desencola) y `final_nodo` (por dónde se encola) — sin el segundo, encolar tendría que recorrer toda la lista cada vez, igual que le pasaba a `insertar_final` en la lista simple (3.3).

**Paso a paso: qué pasa en memoria al encolar tres elementos**

```
encolar("A"):  lista vacía → A se vuelve frente Y final a la vez
  frente_nodo ─┐
               ▼
              [A|None]
               ▲
  final_nodo ──┘

encolar("B"):  final_nodo.siguiente = nuevo, LUEGO final_nodo = nuevo
  frente_nodo ─┐
               ▼
              [A|●]──►[B|None]
                        ▲
  final_nodo ───────────┘

encolar("C"):  se repite el mismo patrón, siempre sobre el final_nodo actual
  frente_nodo ─┐
               ▼
              [A|●]──►[B|●]──►[C|None]
                                ▲
  final_nodo ─────────────────────┘
```

`desencolar()` hace exactamente lo opuesto en el otro extremo: `frente_nodo = frente_nodo.siguiente` — nunca toca `final_nodo`, salvo en el caso especial de que la cola se quede completamente vacía (ahí hay que poner `final_nodo = None` también, o quedaría apuntando a un nodo fantasma).

## Implementación correcta, con lista simple + dos punteros externos

> Nota: aunque a veces se describe informalmente como "usar una lista doble", en realidad basta con una lista **simplemente** enlazada (cada `NodoCola` solo tiene `.siguiente`) — el truco no está en el nodo, sino en guardar **dos punteros externos** (`frente_nodo` y `final_nodo`) a esa misma lista. Una lista doblemente enlazada real (3.3, siguiente archivo) sí sería necesaria si quisieras recorrer la cola también hacia atrás, cosa que una cola normal nunca necesita hacer.

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

**Diagrama de flujo — `encolar` y `desencolar` juntos:**

```
   encolar(dato)                          desencolar()
        │                                       │
        ▼                                       ▼
┌───────────────────┐               ┌───────────────────────┐
│ ¿cola vacía?        │               │ ¿cola vacía?           │
└────┬─────────┬─────┘               └────┬──────────┬───────┘
  sí │         │ no                    sí │          │ no
     ▼         ▼                          ▼          ▼
┌──────────┐ ┌──────────────────┐  ┌───────────┐ ┌────────────────────┐
│ frente_  │ │ final_nodo.       │  │ raise      │ │ dato = frente_nodo. │
│ nodo =    │ │  siguiente = nuevo │  │ IndexError │ │  dato                │
│ final_    │ │ final_nodo = nuevo │  └───────────┘ │ frente_nodo =        │
│ nodo =    │ └──────────────────┘                  │  frente_nodo.        │
│  nuevo     │                                       │  siguiente            │
└──────────┘                                       └──────────┬───────────┘
                                                                ▼
                                                     ┌───────────────────────┐
                                                     │ ¿frente_nodo es None    │
                                                     │  ahora (quedó vacía)?    │
                                                     └────┬──────────┬────────┘
                                                       sí │          │ no
                                                          ▼          │
                                                 ┌──────────────┐    │
                                                 │ final_nodo =  │    │
                                                 │  None (también)│    │
                                                 └──────┬────────┘    │
                                                        └──── return dato
```

**El paso que más se olvida:** al `desencolar()` el último elemento, `frente_nodo` queda en `None` — pero `final_nodo` seguiría apuntando al nodo que ya no existe en la lista si no se reinicia también. Ese chequeo extra es exactamente el mismo cuidado que tuviste con `self.ultimo` en la lista circular (3.3) al eliminar su único nodo.

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

**Diagrama de flujo del algoritmo:**

```
        ┌───────────────────────┐
        │ visitados = {inicio}  │
        │ cola = [inicio]        │
        └───────────┬───────────┘
                    ▼
        ┌───────────────────────┐
   ┌────┤ ¿cola tiene elementos? ├────┐
   │ sí └───────────────────────┘  no │
   ▼                                   ▼
┌───────────────────┐         ┌──────────────────┐
│ actual =           │         │ return orden      │
│ cola.popleft()      │         └──────────────────┘
│ (el más antiguo)     │
└─────────┬────────────┘
          ▼
┌───────────────────────┐
│ orden.append(actual)   │
└─────────┬──────────────┘
          ▼
┌───────────────────────────┐
│ Por cada vecino de actual  │
└─────────┬──────────────────┘
          ▼
┌───────────────────────┐
│ ¿vecino en visitados?  │
└────┬──────────────┬───┘
  sí │              │ no
     │              ▼
     │    ┌──────────────────────┐
     │    │ visitados.add(vecino) │
     │    │ cola.append(vecino)    │
     │    └───────────┬────────────┘
     │                │
     └── (se ignora) ─┴─── vuelve a "¿cola tiene elementos?"
```

**El detalle que hace que sea "por niveles":** `visitados` se marca **al encolar**, no al desencolar — así un mismo vecino nunca se encola dos veces, aunque dos nodos distintos lo tengan como vecino compartido.

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

## Usos y aplicaciones en la vida real

| Dónde se usa | Cómo aplica FIFO |
|---|---|
| **Planificador de procesos de un sistema operativo** (Round Robin, Sistemas Operativos 2.4) | La cola de procesos "Listos" — a nadie se le "brinca" la fila sin una razón (prioridad) explícita. |
| **Cola de impresión** (spooler) | El primer documento enviado es el primero en imprimirse, aunque lleguen más después. |
| **Colas de mensajes en sistemas distribuidos** (RabbitMQ, Kafka, AWS SQS) | Microservicios que se comunican procesando mensajes en el orden en que llegaron, para no perder eventos ni procesarlos fuera de orden. |
| **Atención al cliente / call centers** | "Su llamada será atendida en el orden en que fue recibida" — literalmente la definición de FIFO. |
| **Buffer de teclado del sistema operativo** | Las teclas que presionas se encolan si la aplicación no las procesa al instante; se entregan en el mismo orden en que las tecleaste. |
| **Streaming de video/audio** (buffer de reproducción) | Los fragmentos de video llegan por la red y se encolan; el reproductor los consume (desencola) en orden, para no reproducir el minuto 5 antes que el minuto 2. |
| **Sistemas de boletos/reservaciones en línea** (conciertos, vuelos) | La "sala de espera virtual" de sitios como Ticketmaster es, literalmente, una cola — se le asigna un turno a cada visitante en el orden en que entró. |
| **BFS en aplicaciones de mapas/GPS** | Encontrar la ruta más corta en número de "saltos" (ej. redes sociales: ¿a cuántos amigos de distancia está esta persona?) usa la misma cola vista en la Aplicación de BFS. |

## Conexión con la teoría

Pilas y colas son, en el fondo, la misma idea (contenedor lineal + dos operaciones) con la disciplina de acceso invertida. Ambas son la base de estructuras y algoritmos que vienen después: pilas para DFS y evaluación de expresiones; colas para BFS y para el propio planificador Round Robin que ya viste en Sistemas Operativos 2.4 — la cola de procesos "Listos" es, literalmente, una cola.
