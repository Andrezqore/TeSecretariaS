import tkinter as tk
from tkinter import filedialog, messagebox
import math
import re
import pandas as pd

def rellenar_con_ceros(valor, longitud):
    return str(valor).zfill(longitud)

def calcular_dias_trabajados(horas):
    return str(math.ceil(horas / 3)).zfill(2)  # Redondear siempre hacia arriba

claves_txt = []
claves_excel = []

def mostrar_claves(claves_empleados):
    resultado_text.delete(1.0, tk.END)
    for i, clave in enumerate(claves_empleados):
        resultado_text.insert(tk.END, f"Empleado {i + 1}: {clave}\n")

def guardar_claves_por_tipo(claves):
    tiempos_extra = []
    guardias = []
    prima_dominical = []
    
    for clave in claves:
        concepto = clave[10:14]  # Extraer el concepto de la clave
        if concepto == "4306":
            tiempos_extra.append(clave)
        elif concepto == "1170":
            guardias.append(clave)
        elif concepto == "1621":
            prima_dominical.append(clave)
    
    with open("tiempos_extra.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(tiempos_extra))
    
    with open("guardias.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(guardias))
    
    with open("prima_dominical.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(prima_dominical))
    
    messagebox.showinfo("Guardado", "Se han creado los archivos:\n- tiempos_extra.txt\n- guardias.txt\n- prima_dominical.txt")

def combinar_claves():
    claves_combinadas = claves_txt + claves_excel
    guardar_claves_por_tipo(claves_combinadas)
    mostrar_claves(claves_combinadas)

def procesar_txt():
    global claves_txt
    claves_txt = []
    
    archivo = filedialog.askopenfilename(title="Seleccionar archivo TXT", filetypes=[("Archivos de texto", "*.txt")])
    if not archivo:
        return

    try:
        with open(archivo, "r", encoding="latin-1") as file:
            for linea in file:
                if len(linea) < 40:
                    continue  # Saltar líneas inválidas
                
                match = re.search(r'\D(\d{10,})', linea)
                if not match:
                    continue
                
                inicio_datos = match.start(1)
                num_empleado = linea[inicio_datos:inicio_datos + 10].strip()
                concepto = linea[inicio_datos + 10:inicio_datos + 14].strip()
                fecha_inicio = linea[inicio_datos + 18:inicio_datos + 26].strip()
                fecha_fin = linea[inicio_datos + 26:inicio_datos + 34].strip()
                horas_trabajadas = linea[inicio_datos + 42:inicio_datos + 44].strip()
                
                partes = linea.split(".")
                unidad_administrativa = "0024" if len(partes) <= 1 or len(partes[1]) < 6 else partes[1][2:6].strip()
                
                if not horas_trabajadas.isdigit():
                    horas_trabajadas = "00"
                
                dias_trabajados = "00"
                if concepto == "4306":
                    dias_trabajados = calcular_dias_trabajados(int(horas_trabajadas))
                
                clave = (
                    rellenar_con_ceros(num_empleado, 10) +
                    concepto +
                    fecha_inicio +
                    fecha_fin +
                    "00000000" +
                    rellenar_con_ceros(horas_trabajadas, 2) +
                    "0000" +
                    unidad_administrativa +
                    dias_trabajados
                )
                claves_txt.append(clave)
    except Exception as e:
        messagebox.showerror("Error de lectura", f"No se pudo leer el archivo TXT:\n{str(e)}")
        return
    
    mostrar_claves(claves_txt)

def procesar_excel():
    global claves_excel
    claves_excel = []
    
    archivo = filedialog.askopenfilename(title="Seleccionar archivo Excel", filetypes=[("Archivos de Excel", "*.xlsx;*.xls")])
    if not archivo:
        return
    
    try:
        df = pd.read_excel(archivo, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        
        columnas_esperadas = ["EMP", "CONCEPTO", "FECHA INICIO", "FECHA FIN", "HORAS TIEMPO", "DIAS DE GU Y PD", "DIAS A PAGAR"]
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
        
        if columnas_faltantes:
            messagebox.showerror("Error de lectura", f"No se encontraron las columnas esperadas en el archivo Excel:\n{columnas_faltantes}\n\nLas columnas detectadas fueron:\n{list(df.columns)}")
            return
        
        df.fillna("0", inplace=True)
        
        for _, row in df.iterrows():
            num_empleado = rellenar_con_ceros(row['EMP'], 10)
            concepto = row['CONCEPTO']
            fecha_inicio = row['FECHA INICIO'][8:10] + row['FECHA INICIO'][5:7] + row['FECHA INICIO'][0:4]
            fecha_fin = row['FECHA FIN'][8:10] + row['FECHA FIN'][5:7] + row['FECHA FIN'][0:4]
            
            if concepto == "4306":
                horas_trabajadas = rellenar_con_ceros(row['HORAS TIEMPO'], 2)
                dias_trabajados = calcular_dias_trabajados(int(row['HORAS TIEMPO']))
            else:
                horas_trabajadas = rellenar_con_ceros(str(int(row['DIAS DE GU Y PD']) * 4), 2)
                dias_trabajados = "00"
            
            clave = (
                num_empleado +
                concepto +
                fecha_inicio +
                fecha_fin +
                "00000000" +
                horas_trabajadas +
                "0000" +
                "0024" +
                dias_trabajados
            )
            claves_excel.append(clave)
    except Exception as e:
        messagebox.showerror("Error de lectura", f"No se pudo leer el archivo Excel:\n{str(e)}")
        return
    
    mostrar_claves(claves_excel)

root = tk.Tk()
root.title("Generador de Claves desde TXT y Excel")

tk.Button(root, text="Seleccionar archivo TXT", command=procesar_txt).pack(pady=5)
tk.Button(root, text="Seleccionar archivo Excel", command=procesar_excel).pack(pady=5)
tk.Button(root, text="Combinar información TXT y Excel", command=combinar_claves).pack(pady=5)

resultado_text = tk.Text(root, height=20, width=60)
resultado_text.pack(pady=10)

root.mainloop()
