# 3.3 Listas — doblemente enlazadas

## La limitación que resuelven

En una lista simplemente enlazada (sección anterior), cada nodo solo conoce al **siguiente** — para ir hacia atrás no hay atajo, tendrías que recorrer desde la cabeza otra vez. Una lista **doblemente ligada** agrega un puntero extra: cada nodo conoce tanto al siguiente como al **anterior**.

```
None ←[●|dato|●]⇄[●|dato|●]⇄[●|dato|●]→ None
        nodo1          nodo2          nodo3
```

Esto tiene un costo (cada nodo usa más memoria: un puntero extra) a cambio de un beneficio real: **insertar y eliminar en cualquiera de los dos extremos es O(1)**, sin necesitar recorrer nada — algo que en una lista simple solo era O(1) en el extremo inicial.

**Paso a paso: qué pasa en memoria al insertar al final**

```
Estado inicial (un solo nodo):     cabeza → [a|●⇄●] ← cola
                                          (anterior=None, siguiente=None)

Paso 1 — crear el nuevo nodo, todavía suelto:
                                    nuevo → [b|None⇄None]

Paso 2 — nuevo.anterior = cola  (el nuevo mira hacia atrás, a lo que era la cola):
                                    nuevo → [b|●⇄None]  (su .anterior apunta a "a")

Paso 3 — cola.siguiente = nuevo  (el viejo último ahora mira hacia adelante, al nuevo):
                          cabeza → [a|●⇄●] ⇄ [b|●⇄None]

Paso 4 — cola = nuevo  (el puntero externo "cola" se actualiza al final):
                          cabeza → [a|●⇄●] ⇄ [b|●⇄None] ← cola
```

**Cuatro pasos, en ambas direcciones** — por eso una lista doble "cuesta" más código que una simple: cada inserción/eliminación debe mantener consistentes **dos** flechas (`.siguiente` y `.anterior`), no solo una. Olvidar el Paso 2 (`nuevo.anterior = cola`) es el error más común: la lista se vería bien recorriéndola hacia adelante, pero `recorrer_atras()` fallaría o daría un resultado incompleto, porque el nuevo nodo no sabría a quién regresar.

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

    def buscar(self, dato):
        """O(n) — sin acceso directo por índice."""
        actual = self.cabeza
        indice = 0
        while actual is not None:
            if actual.dato == dato:
                return indice
            actual = actual.siguiente
            indice += 1
        return -1

    def eliminar(self, dato):
        """O(n) para encontrarlo, O(1) para desconectarlo — y sin necesitar 'anterior' como
        parámetro extra (a diferencia de la lista simple), porque cada nodo ya conoce al suyo."""
        actual = self.cabeza
        while actual is not None:
            if actual.dato == dato:
                if actual.anterior is None:              # es la cabeza
                    self.cabeza = actual.siguiente
                else:
                    actual.anterior.siguiente = actual.siguiente
                if actual.siguiente is None:              # es la cola
                    self.cola = actual.anterior
                else:
                    actual.siguiente.anterior = actual.anterior
                self._tamano -= 1
                return True
            actual = actual.siguiente
        return False
```

**Paso a paso: eliminar un nodo del medio (`b`, de la lista `a ⇄ b ⇄ c`)**

```
Antes:   a ⇄ b ⇄ c
         (b.anterior=a, b.siguiente=c)

Paso 1 — actual.anterior.siguiente = actual.siguiente
         (el nodo "a" deja de apuntar a "b" y apunta directo a "c"):
         a ──────────► c
              ⇄
              b   (b sigue existiendo en memoria, pero ya nadie
                    "hacia adelante" pasa por él)

Paso 2 — actual.siguiente.anterior = actual.anterior
         (el nodo "c" deja de apuntar a "b" y apunta directo a "a"):
         a ⇄ c        (ahora tampoco se puede llegar a "b" recorriendo hacia atrás)

Resultado:   a ⇄ c
```

**Por qué son necesarios los dos pasos:** el Paso 1 desconecta a `b` de la dirección "hacia adelante"; el Paso 2 lo desconecta de la dirección "hacia atrás". Si solo hicieras el Paso 1, `recorrer_adelante()` ya no vería a `b` — pero `c.anterior` seguiría apuntando a `b` (un nodo que "no debería estar ahí" desde el punto de vista de la lista), y `recorrer_atras()` desde `c` pasaría por `b` antes de llegar a `a`, dando un resultado inconsistente con el recorrido hacia adelante.

```python
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

lista.insertar_final("c")
lista.insertar_final("d")
print(lista)                          # 'a' ⇄ 'b' ⇄ 'c' ⇄ 'd'
print(lista.buscar("c"))              # 2
print(lista.eliminar("b"))            # True — elimina del MEDIO, no de un extremo
print(lista)                          # 'a' ⇄ 'c' ⇄ 'd'
```

**Por qué `eliminar` aquí es más simple que en la lista simple (3.3, sección anterior):** ahí necesitabas rastrear un puntero `anterior` a mano mientras recorrías, porque el nodo no sabía quién venía antes de él. Aquí `actual.anterior` **ya existe** — el precio que pagaste en memoria extra (un puntero más por nodo) se cobra de vuelta en código más simple y sin el riesgo de olvidar actualizar `anterior` en el ciclo.

## Comparación con la lista simple

| Operación | Lista simple | Lista doble |
|---|---|---|
| Insertar al inicio | O(1) | O(1) |
| Insertar al final | O(n) — hay que recorrer | O(1) — gracias a `self.cola` |
| Eliminar del inicio | O(1) | O(1) |
| Eliminar del final | O(n) — hay que encontrar el penúltimo | O(1) — gracias a `.anterior` |
| Buscar / eliminar por valor | O(n) | O(n) — pero el código es más simple, sin rastrear `anterior` a mano |
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
