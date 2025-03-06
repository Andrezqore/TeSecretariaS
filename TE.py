import tkinter as tk
from tkinter import filedialog, messagebox
import math
import re

def rellenar_con_ceros(valor, longitud):
    return valor.zfill(longitud)

def calcular_dias_trabajados(horas):
    return str(math.ceil(horas / 3)).zfill(2)  # Redondear siempre hacia arriba

def procesar_archivo():
    archivo = filedialog.askopenfilename(title="Seleccionar archivo TXT", filetypes=[("Archivos de texto", "*.txt")])
    if not archivo:
        return
    
    claves_empleados = []
    total_empleados = 0
    total_tiempo_extra = 0
    total_guardias = 0
    total_prima_dominical = 0
    
    try:
        with open(archivo, "r", encoding="latin-1") as file:  # Usar latin-1 para evitar problemas de codificación
            for linea in file:
                if len(linea) < 40:
                    continue  # Saltar líneas inválidas
                
                # Buscar el primer número después del nombre
                match = re.search(r'\D(\d{10,})', linea)
                if not match:
                    continue
                
                total_empleados += 1
                
                inicio_datos = match.start(1)
                num_empleado = linea[inicio_datos:inicio_datos + 10].strip()
                concepto = linea[inicio_datos + 10:inicio_datos + 14].strip()
                fecha_inicio = linea[inicio_datos + 18:inicio_datos + 26].strip()
                fecha_fin = linea[inicio_datos + 26:inicio_datos + 34].strip()
                horas_trabajadas = linea[inicio_datos + 42:inicio_datos + 44].strip()
                
                # Encontrar la unidad administrativa
                partes = linea.split(".")
                if len(partes) > 1 and len(partes[1]) >= 6:
                    unidad_administrativa = partes[1][2:6].strip()
                else:
                    unidad_administrativa = "0000"  # Valor por defecto si no se encuentra
                
                if not horas_trabajadas.isdigit():
                    horas_trabajadas = "00"
                
                dias_trabajados = "00"  # Por defecto 00 para Prima Dominical y Guardias
                if concepto == "4306":  # Si es tiempo extra, calcular días trabajados
                    dias_trabajados = calcular_dias_trabajados(int(horas_trabajadas))
                    total_tiempo_extra += 1
                elif concepto == "1170":
                    total_guardias += 1
                elif concepto == "1621":
                    total_prima_dominical += 1
                
                clave = (
                    rellenar_con_ceros(num_empleado, 10) +
                    concepto +
                    fecha_inicio +
                    fecha_fin +
                    "00000000" +  # Ocho ceros fijos
                    rellenar_con_ceros(horas_trabajadas, 2) +
                    "0000" +  # Cuatro ceros fijos
                    unidad_administrativa +
                    dias_trabajados
                )
                clave = clave[:50]  # Asegurar que la clave tenga exactamente 50 caracteres
                claves_empleados.append(clave)
    except Exception as e:
        messagebox.showerror("Error de lectura", f"No se pudo leer el archivo:\n{str(e)}")
        return
    
    mostrar_claves(claves_empleados, total_empleados, total_tiempo_extra, total_guardias, total_prima_dominical)

def mostrar_claves(claves_empleados, total_empleados, total_tiempo_extra, total_guardias, total_prima_dominical):
    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, f"Total de empleados: {total_empleados}\n")
    resultado_text.insert(tk.END, f"Empleados con tiempo extra: {total_tiempo_extra}\n")
    resultado_text.insert(tk.END, f"Empleados con guardias: {total_guardias}\n")
    resultado_text.insert(tk.END, f"Empleados con prima dominical: {total_prima_dominical}\n\n")
    
    for i, clave in enumerate(claves_empleados):
        resultado_text.insert(tk.END, f"Empleado {i + 1}: {clave}\n")

# Crear ventana principal
root = tk.Tk()
root.title("Generador de Claves desde TXT")

tk.Button(root, text="Seleccionar archivo TXT", command=procesar_archivo).pack(pady=10)

resultado_text = tk.Text(root, height=15, width=60)
resultado_text.pack(pady=10)

root.mainloop()
