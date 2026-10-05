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