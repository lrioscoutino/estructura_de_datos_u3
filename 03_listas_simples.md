# 3.3 Listas — simplemente enlazadas

## Por qué no basta con `list` de Python

Una `list` de Python es, internamente, un arreglo dinámico: elementos contiguos en memoria. Eso hace `lista[i]` rápido (O(1)), pero insertar al inicio obliga a recorrer y mover cada elemento existente (O(n)) — lo viste en 1.5 (análisis de algoritmos).

Una **lista ligada** resuelve justo ese problema: en vez de casillas contiguas, cada elemento (**nodo**) guarda su dato y una referencia al siguiente nodo. Insertar al inicio deja de requerir mover nada — solo redirigir un puntero.

```
[dato|●]→[dato|●]→[dato|●]→ None
  nodo1      nodo2      nodo3
```

## El nodo, la pieza base

```python
class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

    def __repr__(self):
        return f"Nodo({self.dato!r})"
```

## La lista: cabeza + operaciones

```python
class ListaSimple:
    # (la clase Nodo definida arriba va antes que esta clase en tu archivo)
    def __init__(self):
        self.cabeza = None
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self.cabeza is None

    def insertar_inicio(self, dato):
        """O(1) — solo redirige dos punteros."""
        nuevo = Nodo(dato)
        nuevo.siguiente = self.cabeza
        self.cabeza = nuevo
        self._tamano += 1

    def insertar_final(self, dato):
        """O(n) — hay que llegar hasta el último nodo primero."""
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self._tamano += 1

    def insertar_en_posicion(self, indice, dato):
        """O(n) — hay que llegar caminando hasta esa posición, no hay acceso directo."""
        if indice == 0:
            self.insertar_inicio(dato)
            return
        if not (0 < indice <= self._tamano):
            raise IndexError("índice fuera de rango")
        anterior = self.cabeza
        for _ in range(indice - 1):
            anterior = anterior.siguiente
        nuevo = Nodo(dato)
        nuevo.siguiente = anterior.siguiente   # el nuevo apunta a lo que seguía
        anterior.siguiente = nuevo               # el anterior ahora apunta al nuevo
        self._tamano += 1

    def buscar(self, dato):
        """O(n) — sin atajos, hay que recorrer nodo por nodo."""
        actual = self.cabeza
        indice = 0
        while actual is not None:
            if actual.dato == dato:
                return indice
            actual = actual.siguiente
            indice += 1
        return -1

    def eliminar(self, dato):
        """O(n) para encontrarlo, O(1) para desconectarlo una vez encontrado."""
        actual = self.cabeza
        anterior = None
        while actual is not None:
            if actual.dato == dato:
                if anterior is None:          # es la cabeza
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                self._tamano -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def __repr__(self):
        elementos = []
        actual = self.cabeza
        while actual is not None:
            elementos.append(repr(actual.dato))
            actual = actual.siguiente
        return " → ".join(elementos) + " → None"
```

**Diagrama de flujo de `eliminar(dato)` — el algoritmo con más ramas de esta sección:**

```
        ┌─────────────────────┐
        │ actual = cabeza      │
        │ anterior = None       │
        └──────────┬───────────┘
                   ▼
        ┌─────────────────────┐
   ┌────┤ ¿actual es None?      ├────┐
   │ sí └─────────────────────┘  no │
   ▼                                  ▼
┌──────────────┐          ┌─────────────────────┐
│ return False  │          │ ¿actual.dato ==       │
│ (no se         │          │  dato buscado?         │
│  encontró)      │          └────┬──────────┬───────┘
└──────────────┘             sí │          │ no
                                 ▼           ▼
                    ┌─────────────────────┐ ┌────────────────────┐
                    │ ¿anterior es None?    │ │ anterior = actual   │
                    └────┬──────────┬──────┘ │ actual = actual.     │
                      sí │          │ no      │  siguiente           │
                         ▼          ▼          └──────────┬──────────┘
              ┌──────────────┐ ┌───────────────────┐      │
              │ cabeza =      │ │ anterior.siguiente │      │
              │  actual.       │ │  = actual.          │      │
              │  siguiente     │ │  siguiente           │      │
              │ (era la cabeza)│ │ (estaba en medio/final)│    │
              └──────┬────────┘ └─────────┬──────────────┘    │
                     └────────────┬────────┘                    │
                                  ▼                              │
                       ┌────────────────────┐                   │
                       │ return True          │                   │
                       └────────────────────┘                   │
                                                                   │
                       (vuelve a "¿actual es None?") ◄────────────┘
```

**Por qué existen dos casos al desconectar (`anterior is None` vs. no):** la cabeza de la lista es el único nodo al que **nadie más apunta** — no hay un `.siguiente` de otro nodo que redirigir, hay que reasignar directamente `self.cabeza`. Cualquier otro nodo, en cambio, siempre tiene un `anterior` cuyo puntero se puede redirigir. Ese mismo patrón de "¿es la cabeza, o no?" reaparece en casi todas las operaciones de listas ligadas que edites de aquí en adelante.

## Paso a paso: qué pasa en memoria al insertar al inicio

Antes de probar todo junto, vale la pena ver `insertar_inicio` en cámara lenta — es la operación que más confunde la primera vez, aunque sea la más simple:

```
Estado inicial:              cabeza → [10|●] → [20|●] → None

Paso 1 — crear el nuevo nodo (todavía "suelto", nadie apunta a él):
                              nuevo → [5|None]

Paso 2 — nuevo.siguiente = cabeza (el nuevo ahora apunta a lo que ERA la cabeza):
                              nuevo → [5|●] → [10|●] → [20|●] → None
                              cabeza → [10|●] → [20|●] → None     (cabeza AÚN no cambió)

Paso 3 — cabeza = nuevo (ahora sí, la cabeza apunta al nuevo nodo):
                              cabeza → [5|●] → [10|●] → [20|●] → None
```

**El orden de los dos pasos importa:** si hicieras `cabeza = nuevo` *antes* de `nuevo.siguiente = cabeza`, perderías la referencia al resto de la lista — `nuevo.siguiente` apuntaría al propio `nuevo`, y todo lo que había después quedaría inalcanzable (y, en Python, elegible para el recolector de basura). Este es el error más común al programar listas ligadas por primera vez.

## Probándola

```python
lista = ListaSimple()
lista.insertar_final(10)
lista.insertar_final(20)
lista.insertar_final(30)
lista.insertar_inicio(5)
print(lista)                      # 5 → 10 → 20 → 30 → None
print("longitud:", len(lista))    # 4
print("buscar 20:", lista.buscar(20))   # índice 2
print("buscar 99:", lista.buscar(99))   # -1
lista.eliminar(10)
print(lista)                      # 5 → 20 → 30 → None

lista.insertar_en_posicion(1, 15)   # inserta 15 en el índice 1 (entre 5 y 20)
print(lista)                         # 5 → 15 → 20 → 30 → None
```

## Costos, de un vistazo

| Operación | Costo | Por qué |
|---|---|---|
| Insertar al inicio | O(1) | Solo redirige `self.cabeza` |
| Insertar al final | O(n) | Hay que recorrer hasta el último nodo |
| Buscar / acceder por valor | O(n) | Sin índices, no hay atajo |
| Eliminar (ya localizado) | O(1) | Solo redirige el puntero `siguiente` del anterior |
| Eliminar por valor | O(n) | Primero hay que encontrarlo |

Compáralo con la tabla de arreglos que ya viste en la Unidad 1: donde el arreglo es O(n) (insertar al inicio), la lista es O(1) — y viceversa donde el arreglo es O(1) (acceso por índice), la lista es O(n). No hay una estructura "mejor" en absoluto, solo mejor **para el patrón de uso que tengas**.

## Conexión con la teoría

Esta es la estructura más simple de un grupo más amplio: las listas doblemente ligadas (siguiente sección) resuelven la limitación de solo poder avanzar hacia adelante; las listas circulares (sección después de esa) resuelven la de tener un "final" fijo. Ambas son variaciones directas del nodo que acabas de construir aquí.
