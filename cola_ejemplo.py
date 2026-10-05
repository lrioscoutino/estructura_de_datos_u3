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
print(c.datos)