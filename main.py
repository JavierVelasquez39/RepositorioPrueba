import xml.etree.ElementTree as ET
import graphviz

class Nodo:
    def __init__(self, nombre, n, m, datos):
        self.nombre = nombre
        self.n = n
        self.m = m
        self.datos = datos
        self.siguiente = None

class ListaCircular:
    def __init__(self):
        self.cabeza = None

    def agregar(self, nombre, n, m, datos):
        nuevo_nodo = Nodo(nombre, n, m, datos)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
            nuevo_nodo.siguiente = self.cabeza
        else:
            temp = self.cabeza
            while temp.siguiente != self.cabeza:
                temp = temp.siguiente
            temp.siguiente = nuevo_nodo
            nuevo_nodo.siguiente = self.cabeza

    def buscar(self, nombre):
        temp = self.cabeza
        if not temp:
            return None
        while True:
            if temp.nombre == nombre:
                return temp
            temp = temp.siguiente
            if temp == self.cabeza:
                break
        return None

    def mostrar(self):
        temp = self.cabeza
        if not temp:
            return
        while True:
            print(f"Matriz: {temp.nombre}, n: {temp.n}, m: {temp.m}")
            for fila in temp.datos:
                print(fila)
            temp = temp.siguiente
            if temp == self.cabeza:
                break

class PatronNodo:
    def __init__(self, patron):
        self.patron = patron
        self.grupo = ListaCircular()
        self.siguiente = None

class ListaPatrones:
    def __init__(self):
        self.cabeza = None

    def agregar(self, patron, fila):
        nuevo_nodo = PatronNodo(patron)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
            nuevo_nodo.grupo.agregar(fila, 0, 0, [])
            nuevo_nodo.siguiente = self.cabeza
        else:
            temp = self.cabeza
            while True:
                if temp.patron == patron:
                    temp.grupo.agregar(fila, 0, 0, [])
                    return
                if temp.siguiente == self.cabeza:
                    break
                temp = temp.siguiente
            temp.siguiente = nuevo_nodo
            nuevo_nodo.grupo.agregar(fila, 0, 0, [])
            nuevo_nodo.siguiente = self.cabeza

    def buscar(self, patron):
        temp = self.cabeza
        if not temp:
            return None
        while True:
            if temp.patron == patron:
                return temp
            temp = temp.siguiente
            if temp == self.cabeza:
                break
        return None

def leer_archivo(ruta):
    tree = ET.parse(ruta)
    root = tree.getroot()
    lista = ListaCircular()
    for matriz in root.findall('matriz'):
        nombre = matriz.get('nombre')
        n = int(matriz.get('n'))
        m = int(matriz.get('m'))
        datos = ListaCircular()
        for i in range(n):
            fila = ListaCircular()
            for j in range(m):
                fila.agregar("", 0, 0, [0])
            datos.agregar("", 0, 0, fila)
        for dato in matriz.findall('dato'):
            x = int(dato.get('x')) - 1
            y = int(dato.get('y')) - 1
            valor = int(dato.text)
            fila = datos.buscar(x)
            celda = fila.datos.buscar(y)
            celda.datos[0] = valor
        lista.agregar(nombre, n, m, datos)
    return lista

def procesar_matriz(nodo):
    n, m = nodo.n, nodo.m
    datos = nodo.datos
    patrones = ListaPatrones()
    
    for i in range(n):
        fila = datos.buscar(i)
        patron = ListaCircular()
        for j in range(m):
            celda = fila.datos.buscar(j)
            patron.agregar("", 0, 0, [1 if celda.datos[0] > 0 else 0])
        patrones.agregar(patron, i)
    
    matriz_reducida = ListaCircular()
    frecuencias = ListaCircular()
    temp = patrones.cabeza
    while True:
        nueva_fila = ListaCircular()
        for j in range(m):
            nueva_fila.agregar("", 0, 0, [0])
        grupo_temp = temp.grupo.cabeza
        while True:
            fila = datos.buscar(grupo_temp.nombre)
            for j in range(m):
                celda = fila.datos.buscar(j)
                nueva_celda = nueva_fila.buscar(j)
                nueva_celda.datos[0] += celda.datos[0]
            grupo_temp = grupo_temp.siguiente
            if grupo_temp == temp.grupo.cabeza:
                break
        matriz_reducida.agregar("", 0, 0, nueva_fila)
        frecuencias.agregar("", 0, 0, [len(temp.grupo.cabeza)])
        temp = temp.siguiente
        if temp == patrones.cabeza:
            break
    
    return matriz_reducida, frecuencias

def escribir_archivo_salida(nombre, matriz_reducida, frecuencias, ruta_salida):
    root = ET.Element("matrices")
    matriz_elem = ET.SubElement(root, "matriz", nombre=nombre, n=str(matriz_reducida.cabeza.n), m=str(matriz_reducida.cabeza.m), g=str(frecuencias.cabeza.n))
    temp = matriz_reducida.cabeza
    while True:
        fila_temp = temp.datos.cabeza
        while True:
            for j, valor in enumerate(fila_temp.datos):
                ET.SubElement(matriz_elem, "dato", x=str(temp.nombre+1), y=str(j+1)).text = str(valor)
            fila_temp = fila_temp.siguiente
            if fila_temp == temp.datos.cabeza:
                break
        temp = temp.siguiente
        if temp == matriz_reducida.cabeza:
            break
    temp = frecuencias.cabeza
    while True:
        ET.SubElement(matriz_elem, "frecuencia", g=str(temp.datos[0])).text = str(temp.datos[0])
        temp = temp.siguiente
        if temp == frecuencias.cabeza:
            break
    tree = ET.ElementTree(root)
    tree.write(ruta_salida, encoding='utf-8', xml_declaration=True)

def generar_grafica(nodo, matriz_reducida, frecuencias):
    dot = graphviz.Digraph(comment=nodo.nombre)
    dot.node('M', f'Matriz: {nodo.nombre}\nn: {nodo.n}, m: {nodo.m}')
    fila_temp = nodo.datos.cabeza
    while True:
        dot.node(f'F{fila_temp.nombre+1}', f'Fila {fila_temp.nombre+1}: {fila_temp.datos}')
        dot.edge('M', f'F{fila_temp.nombre+1}')
        fila_temp = fila_temp.siguiente
        if fila_temp == nodo.datos.cabeza:
            break
    
    dot.render('grafo_original', format='png')
    
    dot_reducida = graphviz.Digraph(comment=f'{nodo.nombre}_Reducida')
    dot_reducida.node('MR', f'Matriz Reducida: {nodo.nombre}\nn: {matriz_reducida.cabeza.n}, m: {matriz_reducida.cabeza.m}, g: {frecuencias.cabeza.n}')
    temp = matriz_reducida.cabeza
    while True:
        fila_temp = temp.datos.cabeza
        while True:
            dot_reducida.node(f'FR{fila_temp.nombre+1}', f'Fila {fila_temp.nombre+1}: {fila_temp.datos}')
            dot_reducida.edge('MR', f'FR{fila_temp.nombre+1}')
            fila_temp = fila_temp.siguiente
            if fila_temp == temp.datos.cabeza:
                break
        temp = temp.siguiente
        if temp == matriz_reducida.cabeza:
            break
    
    dot_reducida.render('grafo_reducido', format='png')

def mostrar_menu():
    print("Menú principal:")
    print("1. Cargar archivo")
    print("2. Procesar archivo")
    print("3. Escribir archivo salida")
    print("4. Mostrar datos del estudiante")
    print("5. Generar gráfica")
    print("6. Salida")

def main():
    lista = None
    matriz_procesada = None
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            ruta = input("Ingrese la ruta del archivo: ")
            lista = leer_archivo(ruta)
            print("Archivo cargado exitosamente.")
        elif opcion == '2':
            if lista:
                nombre = input("Ingrese el nombre de la matriz a procesar: ")
                nodo = lista.buscar(nombre)
                if nodo:
                    matriz_reducida, frecuencias = procesar_matriz(nodo)
                    matriz_procesada = (nodo, matriz_reducida, frecuencias)
                    print("Archivo procesado exitosamente.")
                else:
                    print("Matriz no encontrada.")
            else:
                print("Primero debe cargar un archivo.")
        elif opcion == '3':
            if matriz_procesada:
                nodo, matriz_reducida, frecuencias = matriz_procesada
                ruta_salida = input("Ingrese la ruta del archivo de salida: ")
                escribir_archivo_salida(nodo.nombre + "_Salida", matriz_reducida, frecuencias, ruta_salida)
                print("Archivo de salida escrito exitosamente.")
            else:
                print("Primero debe procesar un archivo.")
        elif opcion == '4':
            print("Carné: 12345678")
            print("Nombre: Juan Pérez")
            print("Curso: Programación Avanzada")
            print("Carrera: Ingeniería en Sistemas")
            print("Semestre: 5to")
            print("Documentación: https://github.com/usuario/proyecto")
        elif opcion == '5':
            if matriz_procesada:
                nodo, matriz_reducida, frecuencias = matriz_procesada
                generar_grafica(nodo, matriz_reducida, frecuencias)
                print("Gráfica generada exitosamente.")
            else:
                print("Primero debe procesar un archivo.")
        elif opcion == '6':
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()