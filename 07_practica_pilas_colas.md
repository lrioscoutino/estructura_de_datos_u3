# Práctica guiada: historial de navegador (pilas) y cola de descargas (colas)

Práctica complementaria a [3.1 Pilas](01_pilas.md) y [3.2 Colas](02_colas.md). En vez de solo implementar `push`/`pop`/`encolar`/`desencolar` en abstracto, vas a construir dos mini-sistemas que ya usas todos los días: el botón "Atrás" de un navegador (pilas) y una cola de descargas que procesa en orden de llegada (colas).

No vas a recibir el código resuelto. Vas creando tu propio script, celda por celda o bloque por bloque, copiando y ejecutando cada uno en orden.

## Antes de empezar

Crea un archivo `practica_pilas_colas.py` y ve agregando cada bloque en orden, ejecutando con `python3 practica_pilas_colas.py` después de cada uno para verificar el checkpoint antes de seguir.

---

## Parte 1 — Historial de navegador con dos pilas

Un navegador real usa **dos pilas**: una para "Atrás" (páginas ya visitadas) y una para "Adelante" (a las que puedes volver si retrocediste de más).

**Bloque 1 — la clase base:**
```python
class Navegador:
    def __init__(self, pagina_inicial):
        self.pagina_actual = pagina_inicial
        self.historial_atras = []      # pila: páginas anteriores
        self.historial_adelante = []   # pila: páginas a las que puedes "rehacer"

    def visitar(self, nueva_pagina):
        self.historial_atras.append(self.pagina_actual)
        self.pagina_actual = nueva_pagina
        self.historial_adelante.clear()   # visitar algo nuevo borra el "adelante"
        print(f"→ Visitando: {self.pagina_actual}")
```

**Bloque 2 — el botón atrás:**
```python
    def atras(self):
        if not self.historial_atras:
            print("No hay páginas anteriores.")
            return
        self.historial_adelante.append(self.pagina_actual)
        self.pagina_actual = self.historial_atras.pop()
        print(f"← Atrás: {self.pagina_actual}")
```

**Bloque 3 — Completa tú: el botón adelante**

Escribe el método `adelante(self)`. Debe seguir la lógica simétrica de `atras()`: si `historial_adelante` está vacío, avisa que no hay adelante; si no, mueve la página actual a `historial_atras`, y saca (`pop()`) la nueva página actual de `historial_adelante`.

<details><summary>Ver solución</summary>

```python
    def adelante(self):
        if not self.historial_adelante:
            print("No hay páginas hacia adelante.")
            return
        self.historial_atras.append(self.pagina_actual)
        self.pagina_actual = self.historial_adelante.pop()
        print(f"→ Adelante: {self.pagina_actual}")
```
</details>

**Bloque 4 — probarlo:**
```python
nav = Navegador("inicio.com")
nav.visitar("noticias.com")
nav.visitar("clima.com")
nav.visitar("correo.com")

nav.atras()      # vuelve a clima.com
nav.atras()      # vuelve a noticias.com
nav.adelante()   # vuelve a clima.com

nav.visitar("mapas.com")   # esto BORRA la posibilidad de ir "adelante" a correo.com
nav.adelante()               # debe avisar "No hay páginas hacia adelante."
```

**Checkpoint esperado:**
```
→ Visitando: noticias.com
→ Visitando: clima.com
→ Visitando: correo.com
← Atrás: clima.com
← Atrás: noticias.com
→ Adelante: clima.com
→ Visitando: mapas.com
No hay páginas hacia adelante.
```

---

## Parte 2 — Cola de descargas

Ahora una cola: los archivos se procesan en el orden exacto en que llegaron — nunca "salta" uno más nuevo antes que uno más viejo.

**Bloque 5 — la clase base:**
```python
from collections import deque
import time

class GestorDescargas:
    def __init__(self):
        self.cola = deque()
        self.completadas = []

    def agregar_descarga(self, nombre_archivo):
        self.cola.append(nombre_archivo)
        print(f"[en cola] {nombre_archivo}  (posición {len(self.cola)})")
```

**Bloque 6 — Completa tú: procesar la siguiente descarga**

Escribe el método `procesar_siguiente(self)`. Debe: si la cola está vacía, avisar "No hay descargas pendientes."; si no, sacar (con el método correcto de `deque` para el **frente**) el nombre del archivo, imprimir `f"[descargando...] {archivo}"`, y agregarlo a `self.completadas`.

<details><summary>Ver solución</summary>

```python
    def procesar_siguiente(self):
        if not self.cola:
            print("No hay descargas pendientes.")
            return
        archivo = self.cola.popleft()
        print(f"[descargando...] {archivo}")
        self.completadas.append(archivo)
```
</details>

**Bloque 7 — probarlo:**
```python
gestor = GestorDescargas()
gestor.agregar_descarga("reporte.pdf")
gestor.agregar_descarga("foto.jpg")
gestor.agregar_descarga("video.mp4")

gestor.procesar_siguiente()   # debe procesar reporte.pdf — el primero en llegar
gestor.procesar_siguiente()   # foto.jpg
print("Completadas:", gestor.completadas)
print("Pendientes:", list(gestor.cola))
```

**Checkpoint esperado:**
```
[en cola] reporte.pdf  (posición 1)
[en cola] foto.jpg  (posición 2)
[en cola] video.mp4  (posición 3)
[descargando...] reporte.pdf
[descargando...] foto.jpg
Completadas: ['reporte.pdf', 'foto.jpg']
Pendientes: ['video.mp4']
```

---

## Entregable de la práctica

Al terminar, tu script debe correr sin errores y mostrar exactamente los checkpoints de arriba. Agrega al final un comentario respondiendo:

1. ¿Por qué el navegador necesita **dos** pilas y no le bastaría con una?
2. ¿Qué pasaría si `GestorDescargas.procesar_siguiente()` usara `self.cola.pop()` (del final) en vez de `popleft()` (del frente)? ¿A qué estructura se convertiría, en la práctica?
3. En el Bloque 4, ¿por qué `nav.visitar("mapas.com")` borra la posibilidad de ir "adelante"? Relaciónalo con cómo funciona un navegador real cuando visitas un link nuevo después de retroceder.

## Para profundizar (opcional)

- Agrega un límite al historial del navegador (ej. máximo 10 páginas atrás) — cuando se supere, la página más antigua se descarta.
- Implementa **prioridad** en el gestor de descargas: un archivo marcado como urgente se procesa antes que los demás, aunque haya llegado después (pista: esto ya no es una cola FIFO pura — investiga qué estructura de datos resuelve "prioridad" antes de intentarlo; la verás formalmente más adelante en el curso).
