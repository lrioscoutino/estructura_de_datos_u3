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

## Las operaciones fundamentales

| Operación | Qué hace |
|---|---|
| `push(dato)` | Agrega un elemento en el tope |
| `pop()` | Quita y devuelve el elemento del tope |
| `peek()` / `top()` | Mira el elemento del tope sin quitarlo |
| `esta_vacia()` | Comprueba si hay algo que sacar |
| `esta_llena()` | Solo aplica a la representación con arreglo — ver abajo |

## Representación en memoria: arreglo (estática) vs. lista ligada (dinámica)

Una pila se puede construir de dos formas, y la diferencia es exactamente la que viste en la Unidad 1 (1.4, manejo de memoria):

### Opción A — sobre un arreglo (memoria estática)

Se reserva un bloque de tamaño fijo desde el inicio y se lleva un índice `tope` que marca la posición del último elemento insertado.

```
Arreglo de capacidad 5:

 [ 10 | 25 |  7 |  _ |  _ ]
   0    1    2    3    4
             ▲
           tope=2  (3 elementos ocupados: índices 0,1,2)
```

```python
class PilaArreglo:
    def __init__(self, capacidad):
        self.capacidad = capacidad
        self.datos = [None] * capacidad
        self.tope = -1              # -1 significa "vacía"; si no, es el índice del último elemento

    def esta_vacia(self):
        return self.tope == -1

    def esta_llena(self):
        return self.tope == self.capacidad - 1

    def push(self, dato):
        if self.esta_llena():
            raise OverflowError("pila llena (desbordamiento — stack overflow)")
        self.tope += 1
        self.datos[self.tope] = dato

    def pop(self):
        if self.esta_vacia():
            raise IndexError("pop() sobre pila vacía (underflow)")
        dato = self.datos[self.tope]
        self.datos[self.tope] = None
        self.tope -= 1
        return dato

    def peek(self):
        return self.datos[self.tope]


p = PilaArreglo(3)
p.push(1); p.push(2); p.push(3)
try:
    p.push(4)                       # la pila ya está llena
except OverflowError as e:
    print("Error:", e)              # "pila llena (desbordamiento — stack overflow)"
```

**Ventaja:** acceso muy rápido y predecible, sin overhead de punteros. **Desventaja:** el tamaño máximo hay que decidirlo de antemano — si te quedas corto, `push()` falla con desbordamiento aunque técnicamente "haya memoria libre" en el resto de la computadora. Este es, exactamente, el mismo concepto que produce un `RecursionError`/*stack overflow* real cuando una función recursiva se llama demasiadas veces (Unidad 2): la pila de llamadas de tu programa también tiene un tamaño máximo fijo.

### Opción B — sobre una lista ligada (memoria dinámica)

Sin límite fijo de antemano — crece mientras haya memoria disponible en el sistema. Es la que ya conoces de la sección anterior:

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

## Arreglo vs. lista ligada, resumido

| | Arreglo (estática) | Lista ligada (dinámica) |
|---|---|---|
| Tamaño | Fijo, definido al crear la pila | Crece y decrece libremente |
| `push`/`pop` | O(1), sin overhead de punteros | O(1), un puntero extra por nodo |
| Riesgo | Desbordamiento (`OverflowError`) si se llena | Ninguno, salvo agotar la memoria del sistema |
| Uso de memoria | Reservada de golpe (incluso si no se usa toda) | Solo lo que realmente se necesita en cada momento |
| Cuándo conviene | Se conoce el máximo de antemano (ej. profundidad máxima de un parser) | El tamaño es impredecible |

## Notaciones de expresiones: infija, prefija y postfija

Antes de ver las aplicaciones 2 y 4, vale la pena entender **por qué existen tres formas distintas** de escribir la misma expresión matemática — cada una resuelve un problema distinto para quien la procesa (una persona o un programa).

| Notación | Dónde va el operador | Ejemplo (`3 + 4`) | Ejemplo (`(3+4)*2`) |
|---|---|---|---|
| **Infija** | Entre los operandos | `3 + 4` | `( 3 + 4 ) * 2` |
| **Prefija** (polaca) | Antes de los operandos | `+ 3 4` | `* + 3 4 2` |
| **Postfija** (polaca inversa) | Después de los operandos | `3 4 +` | `3 4 + 2 *` |

- **Infija** es la que usas todos los días a mano — pero es **ambigua** sin reglas de precedencia (`3 + 4 * 2` necesita que todos sepamos que `*` "pesa más" que `+`) y necesita paréntesis para forzar un orden distinto.
- **Prefija** y **postfija** son **no ambiguas por construcción**: el orden de los operadores ya codifica la precedencia, así que **nunca necesitan paréntesis**, sin importar qué tan compleja sea la expresión.
- Por eso las calculadoras, compiladores e intérpretes casi nunca evalúan infija directamente — la convierten primero a postfija (Aplicación 4) y evalúan eso con una pila (Aplicación 2), que es mucho más simple de programar que respetar precedencia y paréntesis a mano.

### Evaluar prefija: el mismo truco, en sentido contrario

Evaluar postfija recorre de **izquierda a derecha** apilando operandos. Evaluar prefija hace lo simétrico: se recorre de **derecha a izquierda**, y también se apilan operandos — pero al aplicar un operador, el orden de los `pop()` se invierte.

```python
def evaluar_prefija(expresion):
    tokens = expresion.split()[::-1]   # se procesa de derecha a izquierda
    pila = []
    for token in tokens:
        if token.lstrip("-").isdigit():
            pila.append(int(token))
        else:
            a = pila.pop()   # el PRIMERO que sale es el operando IZQUIERDO (al revés que en postfija)
            b = pila.pop()
            if token == "+": pila.append(a + b)
            elif token == "-": pila.append(a - b)
            elif token == "*": pila.append(a * b)
            elif token == "/": pila.append(a / b)
    return pila.pop()


print(evaluar_prefija("+ 3 4"))          # 7
print(evaluar_prefija("* + 3 4 2"))      # 14   ← equivale a (3+4)*2
print(evaluar_prefija("- 10 4"))         # 6    ← a=10, b=4 → 10-4
```

**La diferencia exacta con `evaluar_postfija` (Aplicación 2):** ahí se recorre de izquierda a derecha y `b = pila.pop()` sale primero (es el operando derecho). Aquí se recorre de derecha a izquierda y `a = pila.pop()` sale primero (es el operando izquierdo) — el sentido del recorrido se invierte, y por eso también se invierte cuál operando sale primero de la pila.

### Las tres, lado a lado

```
Infija:    ( 3 + 4 ) * 2
Prefija:     *  +  3  4  2      ← operador antes: lee el árbol de arriba hacia abajo
Postfija:    3  4  +  2  *      ← operador después: lee el árbol de abajo hacia arriba
```

Ambas describen el mismo árbol de la expresión — solo cambia el orden en que se visita cada nodo (operador antes o después de sus operandos). Esa es la razón por la que ninguna de las dos necesita paréntesis: el árbol ya fija el orden sin ambigüedad, sea cual sea el orden en que lo leas.

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

**Traza explícita, carácter por carácter, de `esta_balanceado("(a+[b])")`:**

| Carácter | Acción | Estado de la pila después |
|---|---|---|
| `(` | Es apertura → se apila | `['(']` |
| `a` | No es paréntesis → se ignora | `['(']` |
| `+` | No es paréntesis → se ignora | `['(']` |
| `[` | Es apertura → se apila | `['(', '[']` |
| `b` | No es paréntesis → se ignora | `['(', '[']` |
| `]` | Es cierre → `pop()` saca `'['`, coincide con `pares[']']='['` | `['(']` |
| `)` | Es cierre → `pop()` saca `'('`, coincide con `pares[')']='('` | `[]` |

Al terminar, la pila quedó vacía (`len(pila) == 0`) → la función devuelve `True`. Si en algún paso el `pop()` hubiera sacado un carácter distinto al esperado (ej. cerrar con `)` cuando el tope tenía `[`), la función habría devuelto `False` en ese mismo instante, sin seguir leyendo el resto de la cadena.

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

**Traza explícita, token por token, de `evaluar_postfija("3 4 + 2 *")`:**

| Token | Acción | Estado de la pila después |
|---|---|---|
| `"3"` | Es número → se apila | `[3]` |
| `"4"` | Es número → se apila | `[3, 4]` |
| `"+"` | Es operador → saca `b=4`, `a=3` (en ese orden), calcula `3+4=7`, apila el resultado | `[7]` |
| `"2"` | Es número → se apila | `[7, 2]` |
| `"*"` | Es operador → saca `b=2`, `a=7`, calcula `7*2=14`, apila el resultado | `[14]` |

Al final queda un solo valor en la pila — ese es el resultado. **El orden `b, a = pila.pop(), pila.pop()` importa** para operaciones no conmutativas: en `"10 4 -"`, la resta correcta es `a - b = 10 - 4 = 6`, no `4 - 10`. Si invirtieras el orden de las dos líneas de `pop()`, todas las restas y divisiones darían el resultado equivocado sin que Python marque ningún error.

## Aplicación 3: deshacer/rehacer

El mecanismo `Ctrl+Z` de casi cualquier editor es una pila: cada acción se apila; `Ctrl+Z` hace `pop()` y revierte esa acción (y opcionalmente la mueve a una segunda pila de "rehacer" para `Ctrl+Y`).

## Aplicación 4: convertir una expresión infija a postfija

La notación que usas todos los días ("infija": `3 + 4`, el operador va *entre* los operandos) no es la que evaluaste en la Aplicación 2 ("postfija": `3 4 +`, el operador va *después*). Convertir de una a otra es exactamente el algoritmo *shunting-yard* de Dijkstra — otra pila, esta vez usada para "posponer" operadores hasta que les toque su turno según la precedencia.

```python
def infija_a_postfija(expresion):
    precedencia = {"+": 1, "-": 1, "*": 2, "/": 2}
    salida = []
    pila = []
    for token in expresion.split():
        if token.isdigit():
            salida.append(token)
        elif token == "(":
            pila.append(token)
        elif token == ")":
            while pila and pila[-1] != "(":
                salida.append(pila.pop())
            pila.pop()   # descarta el "(" que le corresponde a este ")"
        else:   # es un operador
            # saca de la pila cualquier operador de precedencia >= al actual, antes de meter el nuevo
            while pila and pila[-1] != "(" and precedencia.get(pila[-1], 0) >= precedencia[token]:
                salida.append(pila.pop())
            pila.append(token)
    while pila:                       # vacía lo que quede en la pila, al final
        salida.append(pila.pop())
    return " ".join(salida)


print(infija_a_postfija("3 4 +"))            # 3 4 +
print(infija_a_postfija("3 + 4 * 2"))         # 3 4 2 * +   ← respeta que * tiene más precedencia
print(infija_a_postfija("( 3 + 4 ) * 2"))      # 3 4 + 2 *   ← los paréntesis fuerzan el orden
```

**Por qué necesita una pila y no basta con leer de izquierda a derecha:** un operador no puede escribirse en la salida hasta que sepas que no viene algo de mayor precedencia después (como el `*` en `3 + 4 * 2` — el `+` tiene que esperar). La pila es exactamente el mecanismo para "posponer" una decisión hasta tener toda la información necesaria — la misma idea detrás de la evaluación de la Aplicación 2, en sentido inverso.

## Conexión con la teoría

La pila resuelve "el último importa primero". La cola (3.2) resuelve exactamente lo opuesto: "el primero importa primero" — misma estructura de base (un contenedor lineal con dos operaciones simples), disciplina de acceso completamente distinta.
