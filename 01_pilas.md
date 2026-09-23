# 3.1 Pilas (stacks)

## LIFO: el último en entrar es el primero en salir

Una pila es como una torre de platos: solo puedes agregar o quitar por **arriba**. El último plato que pusiste es el primero que puedes quitar — *Last In, First Out*.

```
   ┌───┐
   │ C │  ← tope (el último que entró)
   ├───┤
   │ B │
   ├───┤
   │ A │  ← el primero que entró, el último en salir
   └───┘
```

## Las dos operaciones fundamentales

| Operación | Qué hace |
|---|---|
| `push(dato)` | Agrega un elemento en el tope |
| `pop()` | Quita y devuelve el elemento del tope |
| `peek()` / `top()` | Mira el elemento del tope sin quitarlo |
| `esta_vacia()` | Comprueba si hay algo que sacar |

## Implementación con lista ligada (por dentro)

```python
class NodoPila:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class Pila:
    def __init__(self):
        self.tope = None
        self._tamano = 0

    def __len__(self):
        return self._tamano

    def esta_vacia(self):
        return self.tope is None

    def push(self, dato):
        """O(1) — insertar en el tope es como insertar al inicio de una lista simple."""
        nuevo = NodoPila(dato)
        nuevo.siguiente = self.tope
        self.tope = nuevo
        self._tamano += 1

    def pop(self):
        """O(1)."""
        if self.esta_vacia():
            raise IndexError("pop() sobre pila vacía")
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self._tamano -= 1
        return dato

    def peek(self):
        if self.esta_vacia():
            raise IndexError("peek() sobre pila vacía")
        return self.tope.dato

    def __repr__(self):
        elementos = []
        actual = self.tope
        while actual is not None:
            elementos.append(repr(actual.dato))
            actual = actual.siguiente
        return "Pila[tope→ " + ", ".join(elementos) + " ]"
```

## Probándola

```python
pila = Pila()
pila.push(1)
pila.push(2)
pila.push(3)
print(pila)              # Pila[tope→ 3, 2, 1 ]
print(pila.pop())        # 3 — el último en entrar
print(pila.peek())       # 2 — mira sin sacar
print(len(pila))         # 2
```

## En Python real: la `list` ya es una pila perfecta

Como `push`/`pop` solo tocan **un extremo**, el costo O(n) de insertar al inicio de una `list` no aplica aquí — usando el **final** de la lista (`append`/`pop`), ambas operaciones son O(1) amortizado:

```python
pila = []
pila.append(1)   # push
pila.append(2)
pila.append(3)
print(pila.pop())   # 3 — LIFO, sin construir ninguna clase
```

Construiste la versión con nodos arriba para entender el mecanismo — en código real, usa `list` así de simple.

## Aplicación 1: verificar paréntesis/llaves balanceados

```python
def esta_balanceado(expresion):
    pares = {")": "(", "]": "[", "}": "{"}
    pila = []
    for caracter in expresion:
        if caracter in "([{":
            pila.append(caracter)
        elif caracter in ")]}":
            if not pila or pila.pop() != pares[caracter]:
                return False
    return len(pila) == 0


print(esta_balanceado("(a + [b * (c - d)])"))   # True
print(esta_balanceado("(a + [b)"))               # False — se cierra en el orden equivocado
print(esta_balanceado("((a + b)"))                # False — falta cerrar uno
```

**Cómo funciona:** cada apertura se apila; cada cierre debe hacer `pop()` y coincidir con la apertura correspondiente. Si el paréntesis de cierre no coincide con lo que está en el tope, o si sobran aperturas al final, la expresión está mal balanceada. Esta es, literalmente, la técnica que usa cualquier editor de código para subrayarte un paréntesis sin cerrar.

## Aplicación 2: evaluar una expresión postfija (notación polaca inversa)

```python
def evaluar_postfija(expresion):
    """expresion: string tipo '3 4 + 2 *' → equivale a (3+4)*2"""
    pila = []
    for token in expresion.split():
        if token.lstrip("-").isdigit():
            pila.append(int(token))
        else:
            b = pila.pop()   # el orden importa: b salió primero, es el operando derecho
            a = pila.pop()
            if token == "+": pila.append(a + b)
            elif token == "-": pila.append(a - b)
            elif token == "*": pila.append(a * b)
            elif token == "/": pila.append(a / b)
    return pila.pop()


print(evaluar_postfija("3 4 +"))        # 7
print(evaluar_postfija("3 4 + 2 *"))    # 14  ← (3+4)*2
print(evaluar_postfija("5 1 2 + 4 * + 3 -"))   # 14  ← 5 + (1+2)*4 - 3
```

## Aplicación 3: deshacer/rehacer

El mecanismo `Ctrl+Z` de casi cualquier editor es una pila: cada acción se apila; `Ctrl+Z` hace `pop()` y revierte esa acción (y opcionalmente la mueve a una segunda pila de "rehacer" para `Ctrl+Y`).

## Conexión con la teoría

La pila resuelve "el último importa primero". La cola (3.2) resuelve exactamente lo opuesto: "el primero importa primero" — misma estructura de base (un contenedor lineal con dos operaciones simples), disciplina de acceso completamente distinta.
