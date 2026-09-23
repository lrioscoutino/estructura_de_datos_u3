# 3.3 Listas — doblemente enlazadas

## La limitación que resuelven

En una lista simplemente enlazada (sección anterior), cada nodo solo conoce al **siguiente** — para ir hacia atrás no hay atajo, tendrías que recorrer desde la cabeza otra vez. Una lista **doblemente ligada** agrega un puntero extra: cada nodo conoce tanto al siguiente como al **anterior**.

```
None ←[●|dato|●]⇄[●|dato|●]⇄[●|dato|●]→ None
        nodo1          nodo2          nodo3
```

Esto tiene un costo (cada nodo usa más memoria: un puntero extra) a cambio de un beneficio real: **insertar y eliminar en cualquiera de los dos extremos es O(1)**, sin necesitar recorrer nada — algo que en una lista simple solo era O(1) en el extremo inicial.

## El nodo, con dos punteros

```python
class NodoDoble:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
        self.anterior = None
```

## La lista, con cabeza y cola

```python
class ListaDoble:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self.cabeza is None

    def insertar_inicio(self, dato):
        """O(1) — sin importar cuántos elementos tenga la lista."""
        nuevo = NodoDoble(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            nuevo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo
            self.cabeza = nuevo
        self._tamano += 1

    def insertar_final(self, dato):
        """O(1) — gracias al puntero self.cola, ya no hay que recorrer."""
        nuevo = NodoDoble(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            nuevo.anterior = self.cola
            self.cola.siguiente = nuevo
            self.cola = nuevo
        self._tamano += 1

    def eliminar_inicio(self):
        """O(1)."""
        if self.esta_vacia():
            raise IndexError("lista vacía")
        dato = self.cabeza.dato
        self.cabeza = self.cabeza.siguiente
        if self.cabeza is None:
            self.cola = None
        else:
            self.cabeza.anterior = None
        self._tamano -= 1
        return dato

    def eliminar_final(self):
        """O(1) — la razón principal de tener el puntero self.cola."""
        if self.esta_vacia():
            raise IndexError("lista vacía")
        dato = self.cola.dato
        self.cola = self.cola.anterior
        if self.cola is None:
            self.cabeza = None
        else:
            self.cola.siguiente = None
        self._tamano -= 1
        return dato

    def recorrer_adelante(self):
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def recorrer_atras(self):
        actual = self.cola
        while actual is not None:
            yield actual.dato
            actual = actual.anterior

    def __repr__(self):
        return " ⇄ ".join(repr(d) for d in self.recorrer_adelante())
```

## Probándola

```python
lista = ListaDoble()
lista.insertar_final("a")
lista.insertar_final("b")
lista.insertar_final("c")
lista.insertar_inicio("z")
print(lista)                                # 'z' ⇄ 'a' ⇄ 'b' ⇄ 'c'
print(list(lista.recorrer_atras()))         # ['c', 'b', 'a', 'z']  ← el "truco" que la lista simple no tenía
print("elimina del final:", lista.eliminar_final())     # 'c'
print("elimina del inicio:", lista.eliminar_inicio())    # 'z'
print(lista)                                # 'a' ⇄ 'b'
```

## Comparación con la lista simple

| Operación | Lista simple | Lista doble |
|---|---|---|
| Insertar al inicio | O(1) | O(1) |
| Insertar al final | O(n) — hay que recorrer | O(1) — gracias a `self.cola` |
| Eliminar del inicio | O(1) | O(1) |
| Eliminar del final | O(n) — hay que encontrar el penúltimo | O(1) — gracias a `.anterior` |
| Recorrer hacia atrás | No es posible sin recorrer de nuevo desde el inicio | O(n) directo |
| Memoria por nodo | 1 puntero | 2 punteros |

## Dónde se usa de verdad

La `list` de Python **no** es una lista ligada — pero `collections.deque` (double-ended queue) del propio Python sí implementa esta misma idea internamente, precisamente para tener O(1) en ambos extremos:

```python
from collections import deque

d = deque()
d.append(10)        # O(1) — insertar al final
d.appendleft(5)      # O(1) — insertar al inicio
d.pop()               # O(1) — eliminar del final
d.popleft()            # O(1) — eliminar del inicio
```

`deque` es, en la práctica, la lista doblemente ligada que acabas de construir a mano — pero optimizada en C. Úsala en código real; constrúyela a mano aquí para entender *por qué* es rápida.

## Conexión con la teoría

Una lista circular (siguiente sección) es exactamente esta misma estructura, con un solo cambio: en vez de que `self.cola.siguiente` apunte a `None`, apunta de vuelta a `self.cabeza` — cerrando el círculo.
