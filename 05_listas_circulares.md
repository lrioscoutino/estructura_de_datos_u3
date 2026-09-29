# 3.3 Listas — circulares

## La idea: cerrar el círculo

En una lista simple o doble, el último nodo apunta a `None` — hay un final. En una **lista circular**, el último nodo apunta de vuelta al primero: no hay final, solo una vuelta que se repite.

```
     ┌─────────────────────────┐
     ▼                          │
[dato|●]→[dato|●]→[dato|●]──────┘
  nodo1      nodo2      nodo3
```

Sirve exactamente para lo que su forma sugiere: **turnos que se repiten**. Un reproductor de música en modo "repetir todo", la asignación de turnos de CPU entre procesos (Round Robin — ¿te suena? es la misma idea que viste en Sistemas Operativos 2.4), o un buffer circular que sobrescribe lo más viejo cuando se llena.

## Implementación mínima (circular simple)

```python
class NodoCircular:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaCircular:
    def __init__(self):
        self.ultimo = None      # basta con guardar el último — de ahí .siguiente es la cabeza
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self.ultimo is None

    def insertar_final(self, dato):
        nuevo = NodoCircular(dato)
        if self.esta_vacia():
            nuevo.siguiente = nuevo         # se apunta a sí mismo: la lista de 1 elemento
            self.ultimo = nuevo
        else:
            nuevo.siguiente = self.ultimo.siguiente   # nuevo apunta a la cabeza actual
            self.ultimo.siguiente = nuevo               # el viejo último apunta al nuevo
            self.ultimo = nuevo                           # el nuevo pasa a ser el último
        self._tamano += 1

    def insertar_inicio(self, dato):
        """O(1) — igual que insertar_final, salvo que NO mueve el puntero self.ultimo."""
        nuevo = NodoCircular(dato)
        if self.esta_vacia():
            nuevo.siguiente = nuevo
            self.ultimo = nuevo
        else:
            nuevo.siguiente = self.ultimo.siguiente   # el nuevo apunta a la cabeza vieja
            self.ultimo.siguiente = nuevo               # el nuevo se convierte en la cabeza
        self._tamano += 1

    def eliminar(self, dato):
        """O(n) para encontrarlo — hay que recorrer, no hay 'antes de la cabeza' al que saltar directo."""
        if self.esta_vacia():
            return False
        actual = self.ultimo.siguiente
        anterior = self.ultimo
        for _ in range(self._tamano):
            if actual.dato == dato:
                if actual is self.ultimo and actual.siguiente is actual:
                    self.ultimo = None                    # era el único nodo — la lista queda vacía
                else:
                    anterior.siguiente = actual.siguiente
                    if actual is self.ultimo:               # si borramos el último, hay que reasignarlo
                        self.ultimo = anterior
                self._tamano -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def recorrer_una_vuelta(self):
        """Recorre exactamente self._tamano elementos, empezando por la cabeza."""
        if self.esta_vacia():
            return
        cabeza = self.ultimo.siguiente
        actual = cabeza
        for _ in range(self._tamano):
            yield actual.dato
            actual = actual.siguiente

    def __repr__(self):
        return " → ".join(repr(d) for d in self.recorrer_una_vuelta()) + " → (vuelve al inicio)"
```

**El detalle clave:** con solo guardar `self.ultimo`, la cabeza siempre es `self.ultimo.siguiente` — no necesitas un puntero aparte para la cabeza. Y `recorrer_una_vuelta()` **cuenta** cuántos elementos ha visto (`self._tamano`) en vez de comparar contra `None`, porque en una lista circular **nunca llegas a `None`** — un `while actual is not None` aquí sería un bucle infinito.

**El caso borde que más se olvida en `eliminar`:** si el nodo que borras es justo el que apunta `self.ultimo`, hay que **reasignar** `self.ultimo` al nodo anterior — si no, `self.ultimo` quedaría apuntando a un nodo que ya no forma parte de la lista, y `recorrer_una_vuelta()` empezaría desde el lugar equivocado.

```python
lista = ListaCircular()
lista.insertar_final("B")
lista.insertar_final("C")
lista.insertar_inicio("A")
print(lista)                 # 'A' → 'B' → 'C' → (vuelve al inicio)
print(lista.eliminar("B"))   # True
print(lista)                 # 'A' → 'C' → (vuelve al inicio)
print(lista.eliminar("A"))   # True — borra la cabeza, self.ultimo no cambia
print(lista)                 # 'C' → (vuelve al inicio)
print(lista.eliminar("C"))   # True — borra el ÚNICO nodo, que también era self.ultimo
print(lista.esta_vacia())    # True
```

## Probándola

```python
turnos = ListaCircular()
turnos.insertar_final("Proceso A")
turnos.insertar_final("Proceso B")
turnos.insertar_final("Proceso C")
print(turnos)   # 'Proceso A' → 'Proceso B' → 'Proceso C' → (vuelve al inicio)

# simular 7 turnos de Round Robin sobre solo 3 procesos — el círculo se repite solo
ciclo = turnos.recorrer_una_vuelta
import itertools
repetido = itertools.islice(itertools.cycle(list(turnos.recorrer_una_vuelta())), 7)
print(list(repetido))
# ['Proceso A', 'Proceso B', 'Proceso C', 'Proceso A', 'Proceso B', 'Proceso C', 'Proceso A']
```

## Buffer circular: la aplicación real más común

Un caso de uso extremadamente común: un **buffer circular de tamaño fijo** que, al llenarse, sobreescribe el dato más viejo — usado en logs recientes, streaming de audio, o el historial de comandos de una terminal.

```python
class BufferCircular:
    def __init__(self, capacidad):
        self.capacidad = capacidad
        self.datos = [None] * capacidad
        self.inicio = 0     # índice del elemento más viejo
        self.cuenta = 0       # cuántos elementos hay realmente ocupados

    def agregar(self, dato):
        indice_libre = (self.inicio + self.cuenta) % self.capacidad
        self.datos[indice_libre] = dato
        if self.cuenta < self.capacidad:
            self.cuenta += 1
        else:
            self.inicio = (self.inicio + 1) % self.capacidad   # se sobrescribió el más viejo

    def contenido(self):
        return [self.datos[(self.inicio + i) % self.capacidad] for i in range(self.cuenta)]


buf = BufferCircular(3)
for evento in ["login", "click", "scroll", "logout", "error"]:
    buf.agregar(evento)
    print(f"agregado {evento!r} → buffer: {buf.contenido()}")
```

**Checkpoint esperado:** una vez que agregas el 4º evento (`"logout"`), el buffer de capacidad 3 debe mostrar solo los **3 más recientes** — `"login"` desaparece porque fue el más viejo.

## Usos y aplicaciones en la vida real (listas simples, dobles y circulares)

| Estructura | Dónde se usa | Por qué esa y no otra |
|---|---|---|
| **Lista simple** | Cada bloque de una **cadena de bloques** (blockchain) referencia solo al bloque anterior — nunca hace falta ir "hacia adelante". | Solo se necesita un puntero por nodo; ir siempre hacia adelante (del más nuevo al más viejo) es suficiente. |
| **Lista simple** | Pilas y colas (3.1–3.2) se construyen **por dentro** con esta estructura. | Es la pieza mínima — nodo + un puntero — sobre la que se levanta casi todo lo demás. |
| **Lista doble** | **Historial del navegador** (adelante/atrás) y el historial de "deshacer/rehacer" de editores más sofisticados. | Se necesita moverse en ambas direcciones sin volver a recorrer desde el inicio. |
| **Lista doble** | **Caché LRU** (*Least Recently Used*) — usada dentro de bases de datos, CPUs y sistemas de archivos para decidir qué expulsar de una memoria caché limitada. | Cada acceso mueve un nodo al frente en O(1) (gracias a los dos punteros) — imposible de hacer así de rápido con una lista simple. |
| **Lista doble** | Galerías de imágenes/reproductores de música con "siguiente" y "anterior". | Avanzar y retroceder deben costar lo mismo — ninguna de las dos direcciones es "especial". |
| **Lista circular** | **Round Robin** — el propio planificador de procesos de un sistema operativo (Sistemas Operativos 2.4) recorre la cola de procesos en círculo. | Los turnos se repiten indefinidamente; no existe un "último proceso" después del cual ya no haya nadie más. |
| **Lista circular** | Juegos de mesa/multijugador por turnos (ej. una partida de cartas en línea). | Después del último jugador, le vuelve a tocar al primero — sin un caso especial en el código. |
| **Lista circular** | **Buffer circular** en sistemas de audio/video en tiempo real, logs recientes, historial de comandos de una terminal. | Tamaño fijo que se sobrescribe solo — no hay que "correr" los datos viejos para hacer espacio. |

## Conexión con la teoría

Esta lista es la última pieza lineal antes de saltar a pilas (3.1) y colas (3.2) — que, de hecho, se construyen normalmente **usando** una lista simple o doble por dentro (rara vez circular, salvo la cola circular, una variante específica que verás en 3.2).
