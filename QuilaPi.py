import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import threading
from decimal import Decimal, getcontext
import psutil
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import os
from datetime import datetime, timedelta
import sys

class CalculadorPi:
    def __init__(self, root):
        self.root = root
        self.root.title(" Quila π - Herramienta de Estrés  Para CENTROS DE DATOS 🛰️🏴‍☠️ ")
        self.root.geometry("1400x700")
        self.root.resizable(True, True)
        
        # Variable para controlar cálculos en segundo plano
        self.calculando = False
        self.uso_multiprocessing = False
        self.tiempo_inicio = None
        self.iteraciones_totales = 0
        self.progreso_actual = 0
        self.pi_actual = 0.0
        self.ultima_actualizacion = 0
        
        # Información del sistema
        self.info_sistema = self.obtener_info_sistema()
        
        self.crear_interfaz()
    
    def obtener_info_sistema(self):
        """Obtener información del sistema"""
        try:
            # CPU
            cpu_cores = multiprocessing.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # RAM
            ram = psutil.virtual_memory()
            
            return {
                'cpu_cores': cpu_cores,
                'cpu_freq': f"{cpu_freq.current if cpu_freq else 'N/A'} MHz",
                'ram_total': f"{ram.total // (1024**3)} GB"
            }
        except:
            return {'cpu_cores': 'N/A', 'ram_total': 'N/A'}
    
    def crear_interfaz(self):
        """Crear la interfaz gráfica"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text=" Quila π - Herramienta de Estrés  Para CENTROS DE DATOS 🛰️🏴‍☠️ ", 
                          font=('Arial', 18, 'bold'))
        titulo.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Frame de información del sistema
        sistema_frame = ttk.LabelFrame(main_frame, text="Información del Sistema", padding="10")
        sistema_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = f"CPU: {self.info_sistema['cpu_cores']} núcleos, {self.info_sistema['cpu_freq']} | "
        info_text += f"RAM: {self.info_sistema['ram_total']}"
        
        ttk.Label(sistema_frame, text=info_text, font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        
        # Método de cálculo
        ttk.Label(config_frame, text="Método:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.metodo_var = tk.StringVar(value="monte_carlo_cpu")
        metodos = [
            ("Monte Carlo CPU", "monte_carlo_cpu"),
            ("Serie de Leibniz CPU", "leibniz"),
            ("Serie de Nilakantha CPU", "nilakantha"),
            ("Gauss-Legendre CPU", "gauss_legendre"),
            ("Chudnovsky CPU", "chudnovsky")
        ]
        
        for i, (texto, valor) in enumerate(metodos):
            ttk.Radiobutton(config_frame, text=texto, variable=self.metodo_var, 
                           value=valor).grid(row=0, column=i+1, sticky=tk.W, padx=5)
        
        # Precisión/Iteraciones
        ttk.Label(config_frame, text="Iteraciones/Precisión:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.iteraciones_var = tk.StringVar(value="1000000")
        self.entry_iteraciones = ttk.Entry(config_frame, textvariable=self.iteraciones_var, width=20)
        self.entry_iteraciones.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(config_frame, text="(Ej: 1000000 = 1 millón)").grid(row=1, column=2, sticky=tk.W, padx=5)
        
        # Para Chudnovsky - dígitos de precisión
        ttk.Label(config_frame, text="Chudnovsky - Dígitos:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.digitos_var = tk.StringVar(value="100")
        self.entry_digitos = ttk.Entry(config_frame, textvariable=self.digitos_var, width=10)
        self.entry_digitos.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(config_frame, text="(Solo para Chudnovsky)").grid(row=2, column=2, sticky=tk.W, padx=5)
        
        # Opciones de visualización en tiempo real
        ttk.Label(config_frame, text="Visualización:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.frecuencia_actualizacion = tk.StringVar(value="alta")
        frecuencias = [
            ("Alta Frecuencia", "alta"),
            ("Media Frecuencia", "media"), 
            ("Baja Frecuencia", "baja")
        ]
        
        for i, (texto, valor) in enumerate(frecuencias):
            ttk.Radiobutton(config_frame, text=texto, variable=self.frecuencia_actualizacion, 
                           value=valor).grid(row=3, column=i+1, sticky=tk.W, padx=5)
        
        # Opciones de hardware
        ttk.Label(config_frame, text="Opciones:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.usar_multiprocessing = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Usar Multi-procesamiento", 
                       variable=self.usar_multiprocessing).grid(row=4, column=1, sticky=tk.W)
        
        # Frame de controles
        controles_frame = ttk.Frame(main_frame)
        controles_frame.grid(row=5, column=0, columnspan=4, pady=10)
        
        # Botones
        self.boton_calcular = ttk.Button(controles_frame, text="Calcular π", 
                                        command=self.iniciar_calculo)
        self.boton_calcular.grid(row=0, column=0, padx=5)
        
        self.boton_detener = ttk.Button(controles_frame, text="Detener", 
                                       command=self.detener_calculo, state=tk.DISABLED)
        self.boton_detener.grid(row=0, column=1, padx=5)
        
        ttk.Button(controles_frame, text="Limpiar", command=self.limpiar).grid(row=0, column=2, padx=5)
        
        ttk.Button(controles_frame, text="Monitor Sistema", 
                  command=self.mostrar_monitor_sistema).grid(row=0, column=3, padx=5)
        
        # Frame de resultados
        resultados_frame = ttk.LabelFrame(main_frame, text="Resultados en Tiempo Real", padding="10")
        resultados_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        resultados_frame.columnconfigure(0, weight=1)
        resultados_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Área de texto para resultados
        self.texto_resultados = tk.Text(resultados_frame, height=12, width=80, 
                                       font=('Courier', 10), wrap=tk.WORD)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.VERTICAL, 
                                   command=self.texto_resultados.yview)
        h_scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.HORIZONTAL, 
                                   command=self.texto_resultados.xview)
        self.texto_resultados.configure(yscrollcommand=v_scrollbar.set, 
                                       xscrollcommand=h_scrollbar.set)
        
        self.texto_resultados.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Frame de progreso
        self.frame_progreso = ttk.Frame(main_frame)
        self.frame_progreso.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Barra de progreso principal
        self.progreso = ttk.Progressbar(self.frame_progreso, mode='determinate')
        self.progreso.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.frame_progreso.columnconfigure(0, weight=1)
        
        # Label de progreso en ROJO con porcentaje en tiempo real
        self.label_progreso = ttk.Label(self.frame_progreso, text="", 
                                       foreground='red', font=('Arial', 10, 'bold'))
        self.label_progreso.grid(row=1, column=0, pady=(5, 0))
        
        # Label para tiempo estimado
        self.label_tiempo_estimado = ttk.Label(self.frame_progreso, text="", 
                                             foreground='blue', font=('Arial', 9, 'italic'))
        self.label_tiempo_estimado.grid(row=2, column=0, pady=(2, 0))
        
        # Frame de visualización en tiempo real
        self.tiempo_real_frame = ttk.LabelFrame(main_frame, text="Evolución de π en Tiempo Real", padding="10")
        self.tiempo_real_frame.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.label_tiempo_real = ttk.Label(self.tiempo_real_frame, text="π = 0.000000000000", 
                                         font=('Courier', 12, 'bold'), foreground='darkgreen')
        self.label_tiempo_real.grid(row=0, column=0, sticky=tk.W)
        
        self.label_diferencia = ttk.Label(self.tiempo_real_frame, text="Diferencia: 0.000000000000", 
                                        font=('Courier', 10), foreground='darkred')
        self.label_diferencia.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        self.label_digitos_correctos = ttk.Label(self.tiempo_real_frame, text="Dígitos correctos: 0", 
                                               font=('Courier', 10), foreground='darkblue')
        self.label_digitos_correctos.grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        
        # Frame de métricas del sistema
        self.metricas_frame = ttk.LabelFrame(main_frame, text="Métricas en Tiempo Real", padding="10")
        self.metricas_frame.grid(row=9, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.label_metricas = ttk.Label(self.metricas_frame, text="CPU: 0% | RAM: 0%")
        self.label_metricas.grid(row=0, column=0, sticky=tk.W)
    
    def obtener_paso_actualizacion(self, iteraciones_totales):
        """Obtener el paso de actualización según la frecuencia seleccionada"""
        frecuencia = self.frecuencia_actualizacion.get()
        
        if frecuencia == "alta":
            # Actualizar cada 0.1% o cada 1000 iteraciones (lo que sea menor)
            return max(1000, iteraciones_totales // 1000)
        elif frecuencia == "media":
            # Actualizar cada 0.5% o cada 5000 iteraciones
            return max(5000, iteraciones_totales // 500)
        else:  # baja
            # Actualizar cada 1% o cada 10000 iteraciones
            return max(10000, iteraciones_totales // 100)
    
    def calcular_tiempo_estimado(self, porcentaje, tiempo_transcurrido):
        """Calcular tiempo estimado restante"""
        if porcentaje > 0 and porcentaje < 100:
            tiempo_total_estimado = tiempo_transcurrido / (porcentaje / 100)
            tiempo_restante = tiempo_total_estimado - tiempo_transcurrido
            
            if tiempo_restante > 3600:  # Más de 1 hora
                horas = int(tiempo_restante // 3600)
                minutos = int((tiempo_restante % 3600) // 60)
                return f"Tiempo estimado: {horas}h {minutos}m"
            elif tiempo_restante > 60:  # Más de 1 minuto
                minutos = int(tiempo_restante // 60)
                segundos = int(tiempo_restante % 60)
                return f"Tiempo estimado: {minutos}m {segundos}s"
            else:
                return f"Tiempo estimado: {tiempo_restante:.1f}s"
        elif porcentaje >= 100:
            return "Completado"
        else:
            return "Calculando tiempo estimado..."
    
    def monitorear_sistema(self):
        """Monitorear uso de CPU y RAM en tiempo real"""
        while self.calculando:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # RAM
                ram = psutil.virtual_memory()
                ram_percent = ram.percent
                ram_used = ram.used // (1024**3)  # GB
                ram_total = ram.total // (1024**3)  # GB
                
                metricas_text = f"CPU: {cpu_percent:.1f}% | RAM: {ram_percent:.1f}% ({ram_used}/{ram_total} GB)"
                
                self.root.after(0, lambda: self.label_metricas.config(text=metricas_text))
                
            except:
                pass
    
    def mostrar_monitor_sistema(self):
        """Mostrar ventana de monitor del sistema"""
        monitor_window = tk.Toplevel(self.root)
        monitor_window.title("Monitor del Sistema")
        monitor_window.geometry("400x300")
        
        info_text = f"""Información Detallada del Sistema:
        
CPU: {self.info_sistema['cpu_cores']} núcleos
Frecuencia CPU: {self.info_sistema['cpu_freq']}
RAM Total: {self.info_sistema['ram_total']}"""
        
        ttk.Label(monitor_window, text=info_text, justify=tk.LEFT, padding=20).pack()
    
    def actualizar_visualizacion_tiempo_real(self, pi_actual, iteracion_actual):
        """Actualizar la visualización en tiempo real del valor de π"""
        if not self.calculando:
            return
        
        # Formatear π actual
        if isinstance(pi_actual, Decimal):
            pi_str = f"{float(pi_actual):.15f}"
            diferencia = abs(float(pi_actual) - math.pi)
        else:
            pi_str = f"{pi_actual:.15f}"
            diferencia = abs(pi_actual - math.pi)
        
        # Calcular dígitos correctos
        digitos_correctos = self.calcular_digitos_correctos(pi_actual)
        
        # Actualizar interfaz en el hilo principal
        self.root.after(0, lambda: self._actualizar_ui_tiempo_real(
            pi_str, diferencia, digitos_correctos, iteracion_actual
        ))
    
    def _actualizar_ui_tiempo_real(self, pi_str, diferencia, digitos_correctos, iteracion_actual):
        """Actualizar la UI de tiempo real en el hilo principal"""
        self.label_tiempo_real.config(text=f"π ≈ {pi_str}")
        self.label_diferencia.config(text=f"Diferencia: {diferencia:.2e}")
        self.label_digitos_correctos.config(text=f"Dígitos correctos: {digitos_correctos}")
        
        # También actualizar en el área de texto
        if hasattr(self, 'ultima_iteracion_log'):
            if iteracion_actual - self.ultima_iteracion_log >= 10000:  # Log cada 10k iteraciones
                self.agregar_log_tiempo_real(iteracion_actual, pi_str, diferencia, digitos_correctos)
                self.ultima_iteracion_log = iteracion_actual
        else:
            self.ultima_iteracion_log = iteracion_actual
            self.agregar_log_tiempo_real(iteracion_actual, pi_str, diferencia, digitos_correctos)
    
    def agregar_log_tiempo_real(self, iteracion, pi_str, diferencia, digitos_correctos):
        """Agregar log al área de texto"""
        log_text = f"Iteración {iteracion:,}: π ≈ {pi_str} | Dif: {diferencia:.2e} | Dígitos: {digitos_correctos}\n"
        self.texto_resultados.insert(tk.END, log_text)
        self.texto_resultados.see(tk.END)
    
    def actualizar_progreso_real(self, iteracion_actual, iteraciones_totales, pi_actual):
        """Actualizar el progreso REAL en tiempo real - CON VISUALIZACIÓN MEJORADA"""
        if not self.calculando:
            return
        
        # Calcular porcentaje
        porcentaje = (iteracion_actual / iteraciones_totales) * 100
        
        # Obtener paso de actualización según frecuencia seleccionada
        paso_actualizacion = self.obtener_paso_actualizacion(iteraciones_totales)
        
        # Actualizar más frecuentemente para mejor visualización
        tiempo_actual = time.time()
        if (iteracion_actual % paso_actualizacion == 0 or 
            tiempo_actual - self.ultima_actualizacion >= 1.0 or
            iteracion_actual == iteraciones_totales):
            
            self.progreso_actual = porcentaje
            self.ultima_actualizacion = tiempo_actual
            
            # Calcular tiempo transcurrido y estimado
            tiempo_transcurrido = tiempo_actual - self.tiempo_inicio
            tiempo_estimado = self.calcular_tiempo_estimado(porcentaje, tiempo_transcurrido)
            
            # Actualizar visualización en tiempo real
            self.actualizar_visualizacion_tiempo_real(pi_actual, iteracion_actual)
            
            # Actualizar interfaz en el hilo principal
            self.root.after(0, lambda: self._actualizar_ui_progreso(
                porcentaje, pi_actual, iteracion_actual, iteraciones_totales, tiempo_estimado
            ))
    
    def _actualizar_ui_progreso(self, porcentaje, pi_valor, iteracion_actual, iteraciones_totales, tiempo_estimado):
        """Actualizar la UI del progreso en el hilo principal"""
        # Actualizar barra de progreso
        self.progreso.config(value=porcentaje)
        
        # Actualizar label de progreso en ROJO
        if isinstance(pi_valor, Decimal):
            pi_str = f"{float(pi_valor):.12f}"
        else:
            pi_str = f"{pi_valor:.12f}"
            
        texto_progreso = f"PROGRESO: {porcentaje:.2f}% | π ≈ {pi_str} | Iteración: {iteracion_actual:,}/{iteraciones_totales:,}"
        self.label_progreso.config(text=texto_progreso)
        
        # Actualizar tiempo estimado
        self.label_tiempo_estimado.config(text=tiempo_estimado)
    
    def metodo_monte_carlo_cpu(self, iteraciones):
        """Método Monte Carlo optimizado con CPU - CON VISUALIZACIÓN EN TIEMPO REAL"""
        import numpy as np
        
        # Para mejor visualización, usar más lotes
        if iteraciones > 10000000:  # Más de 10 millones
            lotes = 500
        elif iteraciones > 1000000:  # Más de 1 millón
            lotes = 200
        else:
            lotes = 100
            
        tam_lote = iteraciones // lotes
        dentro_circulo = 0
        resultados_parciales = []
        
        for lote in range(lotes):
            if not self.calculando:
                return None
            
            # Calcular lote actual
            inicio = lote * tam_lote
            fin = min((lote + 1) * tam_lote, iteraciones)
            puntos_lote = fin - inicio
            
            # Generar números aleatorios para este lote
            x = np.random.random(puntos_lote)
            y = np.random.random(puntos_lote)
            distancias = np.square(x) + np.square(y)
            dentro_lote = np.sum(distancias <= 1.0)
            dentro_circulo += dentro_lote
            
            # Calcular π actual
            puntos_totales = fin
            pi_actual = 4 * dentro_circulo / puntos_totales
            
            # Actualizar progreso y visualización
            self.actualizar_progreso_real(fin, iteraciones, pi_actual)
            resultados_parciales.append((fin, pi_actual))
        
        pi_final = 4 * dentro_circulo / iteraciones
        return pi_final, resultados_parciales
    
    def metodo_leibniz_secuencial(self, iteraciones):
        """Serie de Leibniz secuencial con progreso real - CON VISUALIZACIÓN MEJORADA"""
        pi_aproximado = 0
        resultados_parciales = []
        
        # Para mejor visualización, actualizar más frecuentemente
        paso_actualizacion = self.obtener_paso_actualizacion(iteraciones)
        
        for i in range(iteraciones):
            if not self.calculando:
                return None
                
            termino = 4 * (-1)**i / (2*i + 1)
            pi_aproximado += termino
            
            # Actualizar progreso de manera optimizada pero más frecuente
            if i % paso_actualizacion == 0 or i == iteraciones - 1:
                self.actualizar_progreso_real(i, iteraciones, pi_aproximado)
                resultados_parciales.append((i, pi_aproximado))
        
        return pi_aproximado, resultados_parciales
    
    def metodo_leibniz(self, iteraciones):
        """Serie de Leibniz original o paralelizada"""
        if self.usar_multiprocessing.get() and self.info_sistema['cpu_cores'] > 1:
            # Para mejor visualización, usar secuencial
            return self.metodo_leibniz_secuencial(iteraciones)
        else:
            return self.metodo_leibniz_secuencial(iteraciones)
    
    def metodo_nilakantha(self, iteraciones):
        """Serie de Nilakantha con progreso real - CON VISUALIZACIÓN MEJORADA"""
        pi_aproximado = 3
        resultados_parciales = []
        
        # Para mejor visualización, actualizar más frecuentemente
        paso_actualizacion = self.obtener_paso_actualizacion(iteraciones)
        
        for i in range(1, iteraciones):
            if not self.calculando:
                return None
                
            termino = 4 * (-1)**(i+1) / ((2*i) * (2*i+1) * (2*i+2))
            pi_aproximado += termino
            
            # Actualizar progreso de manera optimizada
            if i % paso_actualizacion == 0 or i == iteraciones - 1:
                self.actualizar_progreso_real(i, iteraciones, pi_aproximado)
                resultados_parciales.append((i, pi_aproximado))
        
        return pi_aproximado, resultados_parciales
    
    def metodo_gauss_legendre(self, iteraciones):
        """Algoritmo de Gauss-Legendre con progreso real - CON VISUALIZACIÓN MEJORADA"""
        a = 1.0
        b = 1.0 / math.sqrt(2)
        t = 1.0 / 4.0
        p = 1.0
        
        resultados_parciales = []
        
        for i in range(iteraciones):
            if not self.calculando:
                return None
                
            a_siguiente = (a + b) / 2
            b = math.sqrt(a * b)
            t = t - p * (a - a_siguiente)**2
            a = a_siguiente
            p *= 2
            
            pi_aproximado = (a + b)**2 / (4 * t)
            
            # Actualizar progreso en cada iteración (este método converge rápido)
            self.actualizar_progreso_real(i + 1, iteraciones, pi_aproximado)
            self.actualizar_visualizacion_tiempo_real(pi_aproximado, i + 1)
            resultados_parciales.append((i+1, pi_aproximado))
        
        return pi_aproximado, resultados_parciales
    
    def metodo_chudnovsky(self, digitos):
        """
        Algoritmo de Chudnovsky para calcular π con alta precisión.
        CON VISUALIZACIÓN MEJORADA EN TIEMPO REAL
        """
        try:
            # Configurar precisión decimal
            getcontext().prec = digitos + 50  # Margen extra para precisión
            
            # Constantes del algoritmo de Chudnovsky
            C = Decimal(426880) * Decimal(10005).sqrt()
            
            # Términos iniciales
            M = Decimal(1)
            L = Decimal(13591409)
            X = Decimal(1)
            K = Decimal(6)
            S = L
            
            pi_aproximado = C / S
            resultados_parciales = []
            
            # Calcular iteraciones necesarias (cada iteración añade ~14 dígitos)
            iteraciones_necesarias = (digitos // 14) + 2
            
            for i in range(1, iteraciones_necesarias):
                if not self.calculando:
                    return None
                
                # Calcular siguiente término
                M = M * (K**3 - 16*K) / Decimal((i+1)**3)
                L += Decimal(545140134)
                X *= Decimal(-262537412640768000)
                K += Decimal(12)
                
                termino = M * L / X
                S += termino
                
                # Calcular π actual
                pi_actual = C / S
                
                # Actualizar progreso y visualización
                self.actualizar_progreso_real(i, iteraciones_necesarias, pi_actual)
                self.actualizar_visualizacion_tiempo_real(pi_actual, i)
                resultados_parciales.append((i, pi_actual))
            
            # Redondear al número de dígitos solicitado
            pi_final = +pi_actual  # Aplicar la precisión actual
            return pi_final, resultados_parciales
            
        except Exception as e:
            print(f"Error en Chudnovsky: {e}")
            # Fallback a método más simple
            return self.metodo_gauss_legendre(min(20, digitos))
    
    def iniciar_calculo(self):
        """Iniciar el cálculo en un hilo separado"""
        try:
            metodo = self.metodo_var.get()
            
            if metodo == "chudnovsky":
                # Para Chudnovsky usamos dígitos de precisión
                iteraciones = int(self.digitos_var.get())
                if iteraciones <= 0:
                    messagebox.showerror("Error", "El número de dígitos debe ser mayor que 0")
                    return
                
                if iteraciones > 10000:  # Límite razonable
                    respuesta = messagebox.askyesno(
                        "Advertencia", 
                        f"Estás a punto de calcular π con {iteraciones:,} dígitos.\n"
                        f"Esto puede requerir mucha memoria y tiempo.\n\n"
                        f"¿Continuar?"
                    )
                    if not respuesta:
                        return
            else:
                # Para otros métodos usamos iteraciones
                iteraciones = int(self.iteraciones_var.get())
                if iteraciones <= 0:
                    messagebox.showerror("Error", "El número de iteraciones debe ser mayor que 0")
                    return
                
                # Advertencia para iteraciones muy grandes
                if iteraciones > 100000000:  # Más de 100 millones
                    respuesta = messagebox.askyesno(
                        "Advertencia", 
                        f"Estás a punto de ejecutar {iteraciones:,} iteraciones.\n"
                        f"Esto puede tomar mucho tiempo.\n\n"
                        f"¿Continuar?"
                    )
                    if not respuesta:
                        return
                        
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un número válido")
            return
        
        # Configurar interfaz para cálculo
        self.calculando = True
        self.tiempo_inicio = time.time()
        self.iteraciones_totales = iteraciones
        self.progreso_actual = 0
        self.pi_actual = 0.0
        self.ultima_actualizacion = 0
        self.ultima_iteracion_log = 0
        
        self.boton_calcular.config(state=tk.DISABLED)
        self.boton_detener.config(state=tk.NORMAL)
        
        # Configurar barra de progreso determinada
        self.progreso.config(value=0, maximum=100)
        
        # Limpiar resultados anteriores
        self.texto_resultados.delete(1.0, tk.END)
        
        # Mostrar mensaje inicial
        metodo_nombre = self.obtener_nombre_metodo(self.metodo_var.get())
        if metodo == "chudnovsky":
            mensaje_inicial = f"""Iniciando cálculo con método: {metodo_nombre}
Dígitos de precisión: {iteraciones}
Frecuencia de actualización: {self.frecuencia_actualizacion.get().upper()}
Hora de inicio: {time.strftime('%H:%M:%S')}

EVOLUCIÓN DE π EN TIEMPO REAL:
"""
        else:
            mensaje_inicial = f"""Iniciando cálculo con método: {metodo_nombre}
Iteraciones: {iteraciones:,}
Frecuencia de actualización: {self.frecuencia_actualizacion.get().upper()}
Hora de inicio: {time.strftime('%H:%M:%S')}

EVOLUCIÓN DE π EN TIEMPO REAL:
"""
        
        self.texto_resultados.insert(1.0, mensaje_inicial)
        
        # Iniciar monitoreo del sistema
        monitor_thread = threading.Thread(target=self.monitorear_sistema)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.ejecutar_calculo, args=(iteraciones,))
        thread.daemon = True
        thread.start()
    
    def ejecutar_calculo(self, iteraciones):
        """Ejecutar el cálculo (en hilo separado)"""
        metodo = self.metodo_var.get()
        inicio_tiempo = time.time()
        
        try:
            # Seleccionar método
            if metodo == "monte_carlo_cpu":
                resultado = self.metodo_monte_carlo_cpu(iteraciones)
            elif metodo == "leibniz":
                resultado = self.metodo_leibniz(iteraciones)
            elif metodo == "nilakantha":
                resultado = self.metodo_nilakantha(iteraciones)
            elif metodo == "gauss_legendre":
                resultado = self.metodo_gauss_legendre(iteraciones)
            elif metodo == "chudnovsky":
                resultado = self.metodo_chudnovsky(iteraciones)
            
            tiempo_transcurrido = time.time() - inicio_tiempo
            
            # Actualizar interfaz en el hilo principal
            if resultado and self.calculando:
                pi_aproximado, resultados_parciales = resultado
                self.mostrar_resultados(pi_aproximado, resultados_parciales, 
                                      tiempo_transcurrido, iteraciones, metodo)
            elif not self.calculando:
                self.mostrar_mensaje("Cálculo detenido por el usuario")
                
        except Exception as e:
            self.mostrar_error(f"Error en el cálculo: {str(e)}")
        
        finally:
            # Restaurar interfaz
            self.root.after(0, self.finalizar_calculo)
    
    def mostrar_resultados(self, pi_aproximado, resultados_parciales, tiempo, iteraciones, metodo):
        """Mostrar los resultados en el área de texto"""
        # Formatear resultados
        if metodo == "chudnovsky":
            pi_str = str(pi_aproximado)
            if len(pi_str) > 100:
                pi_display = pi_str[:50] + "..." + pi_str[-50:]
            else:
                pi_display = pi_str
                
            resultado_texto = f"""

=== RESULTADO FINAL ===

MÉTODO: {self.obtener_nombre_metodo(metodo)}
DÍGITOS SOLICITADOS: {iteraciones}
TIEMPO TOTAL: {tiempo:.4f} segundos
HORA FINAL: {time.strftime('%H:%M:%S')}

RESULTADO:
π ≈ {pi_display}

PRIMEROS 15 DÍGITOS: {pi_str[:17]}
Math.pi = {math.pi:.15f}
COINCIDENCIA: {self.calcular_digitos_correctos(pi_aproximado)} dígitos correctos
"""
        else:
            resultado_texto = f"""

=== RESULTADO FINAL ===

MÉTODO: {self.obtener_nombre_metodo(metodo)}
ITERACIONES: {iteraciones:,}
TIEMPO TOTAL: {tiempo:.4f} segundos
VELOCIDAD: {iteraciones/tiempo:,.0f} iteraciones/segundo
HORA FINAL: {time.strftime('%H:%M:%S')}

RESULTADO:
π ≈ {pi_aproximado:.15f}
Math.pi = {math.pi:.15f}
DIFERENCIA: {abs(pi_aproximado - math.pi):.2e}

PRECISIÓN: {self.calcular_digitos_correctos(pi_aproximado)} dígitos correctos
"""
        
        # Actualizar en el hilo principal
        self.root.after(0, lambda: self.actualizar_texto_resultados(resultado_texto))
    
    def obtener_nombre_metodo(self, metodo):
        """Obtener el nombre completo del método"""
        nombres = {
            "monte_carlo_cpu": "Monte Carlo (CPU Vectorizado)",
            "leibniz": "Serie de Leibniz",
            "nilakantha": "Serie de Nilakantha", 
            "gauss_legendre": "Algoritmo Gauss-Legendre",
            "chudnovsky": "Algoritmo de Chudnovsky (Alta Precisión)"
        }
        return nombres.get(metodo, metodo)
    
    def calcular_digitos_correctos(self, pi_aproximado):
        """Calcular cuántos dígitos son correctos"""
        if isinstance(pi_aproximado, Decimal):
            pi_str = f"{math.pi:.50f}"
            aprox_str = f"{pi_aproximado:.50f}"
        else:
            pi_str = f"{math.pi:.15f}"
            aprox_str = f"{pi_aproximado:.15f}"
        
        digitos_correctos = 0
        for i, (d1, d2) in enumerate(zip(pi_str, aprox_str)):
            if d1 == d2 and d1 != '.':
                digitos_correctos += 1
            elif d1 != d2 and d1 != '.':
                break
        return digitos_correctos
    
    def actualizar_texto_resultados(self, texto):
        """Actualizar el área de texto con los resultados"""
        # Agregar al texto existente
        self.texto_resultados.insert(tk.END, texto)
        self.texto_resultados.see(tk.END)
    
    def mostrar_mensaje(self, mensaje):
        """Mostrar mensaje en el área de texto"""
        self.root.after(0, lambda: self.actualizar_texto_resultados(f"\n{mensaje}"))
    
    def mostrar_error(self, error):
        """Mostrar error en el área de texto"""
        self.root.after(0, lambda: self.actualizar_texto_resultados(f"\nERROR:\n{error}"))
    
    def detener_calculo(self):
        """Detener el cálculo en curso"""
        self.calculando = False
        self.boton_detener.config(state=tk.DISABLED)
    
    def finalizar_calculo(self):
        """Finalizar el cálculo y restaurar la interfaz"""
        self.calculando = False
        self.boton_calcular.config(state=tk.NORMAL)
        self.boton_detener.config(state=tk.DISABLED)
        self.progreso.config(value=100)
        self.label_progreso.config(text="CÁLCULO COMPLETADO - 100.00%", foreground='green')
        self.label_tiempo_estimado.config(text="Tiempo total completado")
        self.label_metricas.config(text="CPU: 0% | RAM: 0%")
    
    def limpiar(self):
        """Limpiar todos los campos"""
        self.texto_resultados.delete(1.0, tk.END)
        self.label_progreso.config(text="", foreground='red')
        self.label_tiempo_estimado.config(text="")
        self.progreso.config(value=0)
        self.label_metricas.config(text="CPU: 0% | RAM: 0%")
        self.label_tiempo_real.config(text="π = 0.000000000000")
        self.label_diferencia.config(text="Diferencia: 0.000000000000")
        self.label_digitos_correctos.config(text="Dígitos correctos: 0")

def main():
    """Función principal"""
    root = tk.Tk()
    app = CalculadorPi(root)
    root.mainloop()

if __name__ == "__main__":
    main()