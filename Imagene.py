import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import tensorflow as tf  # Importar tensorflow

# Intentar cargar el modelo MobileNetV2
try:
    model = tf.keras.applications.MobileNetV2(weights='imagenet')
except Exception as e:
    print(f"Error al cargar el modelo: {e}")

def es_naranja(imagen):
    # Preprocesar la imagen para que sea compatible con el modelo
    imagen = cv2.resize(imagen, (224, 224))
    imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    imagen = np.expand_dims(imagen, axis=0)
    imagen = imagen / 255.0
    
    # Realizar la predicción
    pred = model.predict(imagen)
    # Analizar el resultado: Buscamos si la imagen contiene una naranja
    return 'orange' in tf.keras.applications.mobilenet_v2.decode_predictions(pred)[0][0][1].lower()

def analizar_imagen(imagen_path):
    # Analizar una sola imagen
    imagen = cv2.imread(imagen_path)
    if imagen is not None:
        if es_naranja(imagen):
            return "Es una naranja"
        else:
            return "No es una naranja"
    return None

def analizar_imagenes(carpeta):
    # Crear carpetas para las imágenes
    carpeta_naranjas = os.path.join(carpeta, "naranjas")
    carpeta_no_naranjas = os.path.join(carpeta, "no_naranjas")
    
    # Crear carpetas si no existen
    if not os.path.exists(carpeta_naranjas):
        os.makedirs(carpeta_naranjas)
    if not os.path.exists(carpeta_no_naranjas):
        os.makedirs(carpeta_no_naranjas)
    
    # Contadores
    cantidad_imagenes = 0
    naranjas = 0
    no_naranjas = 0
    
    # Analizar cada imagen en la carpeta
    for archivo in os.listdir(carpeta):
        if archivo.endswith(('png', 'jpg', 'jpeg')):
            imagen_path = os.path.join(carpeta, archivo)
            imagen = cv2.imread(imagen_path)
            if imagen is not None:
                cantidad_imagenes += 1
                if es_naranja(imagen):
                    naranjas += 1
                    shutil.copy(imagen_path, carpeta_naranjas)
                else:
                    no_naranjas += 1
                    shutil.copy(imagen_path, carpeta_no_naranjas)
    
    return cantidad_imagenes, naranjas, no_naranjas, carpeta_naranjas, carpeta_no_naranjas

# Interfaz gráfica con Tkinter
class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("UMG TAREA 3")
        self.resizable(True, True) 
        
        # Usar rutas relativas para icono e imagen
        icono_path = "assets/Logo.ico"  # Ruta relativa para el icono
        self.iconbitmap(icono_path)
        
        self.carpetas_analizadas = None
        self.imagen_path = None  # Aseguramos que la variable imagen_path esté definida
        
        self.titulo = tk.Label(self, text="DETECTOR DE NARANJAS", font=("Arial", 16, "bold"))
        self.titulo.pack(pady=10)
        
        # Usar rutas relativas para la imagen
        imagen_path = "assets/Umg.png"  # Ruta relativa para la imagen
        imagen = Image.open(imagen_path) 
        imagen = imagen.resize((100, 100))
        self.imagen_tk = ImageTk.PhotoImage(imagen)
        self.label_imagen_principal = tk.Label(self, image=self.imagen_tk)
        self.label_imagen_principal.pack(pady=20)
        
        self.label_carpeta = tk.Label(self, text="Seleccione la carpeta de imágenes a analizar")
        self.label_carpeta.pack(pady=10)
        
        self.boton_carpeta = tk.Button(self, text="Seleccionar carpeta", command=self.seleccionar_carpeta)
        self.boton_carpeta.pack(pady=5)
        
        self.label_imagen = tk.Label(self, text="Seleccione la imagen a analizar (opcional)")
        self.label_imagen.pack(pady=10)
        
        self.boton_imagen = tk.Button(self, text="Seleccionar imagen", command=self.seleccionar_imagen)
        self.boton_imagen.pack(pady=5)
        
        self.boton_iniciar = tk.Button(self, text="Iniciar análisis", command=self.iniciar_analisis)
        self.boton_iniciar.pack(pady=20)
        
        self.resultado_titulo = tk.Label(self, text="Resultados", font=("Arial", 12))
        self.resultado_titulo.pack(pady=5)
        
        self.resultados = tk.Label(self, text="")
        self.resultados.pack(pady=10)

    def seleccionar_carpeta(self):
        self.carpetas_analizadas = filedialog.askdirectory()
        self.imagen_path = None  # Limpiar la imagen seleccionada
    
    def seleccionar_imagen(self):
        self.imagen_path = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg")])
        self.carpetas_analizadas = None  # Limpiar la carpeta seleccionada
    
    def iniciar_analisis(self):
        if not self.carpetas_analizadas and not self.imagen_path:
            messagebox.showerror("Error", "Por favor seleccione una carpeta o una imagen para analizar.")
            return
        
        # Si se seleccionó una carpeta
        if self.carpetas_analizadas:
            cantidad_imagenes, naranjas, no_naranjas, carpeta_naranjas, carpeta_no_naranjas = analizar_imagenes(self.carpetas_analizadas)
            
            # Mostrar resumen de resultados
            resumen = f"Imágenes analizadas: {cantidad_imagenes}\n"
            resumen += f"Imágenes con naranjas: {naranjas}\n"
            resumen += f"Imágenes sin naranjas: {no_naranjas}\n"
            self.resultados.config(text=resumen)
            
            # Botones para abrir las carpetas
            self.boton_abrir_naranjas = tk.Button(self, text="Abrir imágenes con naranjas", command=lambda: os.startfile(carpeta_naranjas))
            self.boton_abrir_naranjas.pack(fill=tk.X, pady=5)
            
            self.boton_abrir_no_naranjas = tk.Button(self, text="Abrir imágenes sin naranjas", command=lambda: os.startfile(carpeta_no_naranjas))
            self.boton_abrir_no_naranjas.pack(fill=tk.X, pady=5)
        
        # Si se seleccionó una sola imagen
        if self.imagen_path:
            resultado = analizar_imagen(self.imagen_path)
            if resultado:
                self.resultados.config(text=resultado)
            else:
                self.resultados.config(text="No se pudo analizar la imagen.")
            

# Ejecutar la aplicación
if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
