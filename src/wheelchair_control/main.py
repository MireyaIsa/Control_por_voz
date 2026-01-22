#!/usr/bin/env python3
"""
================================================================================
CONTROL AVANZADO DE SILLA DE RUEDAS - INTERFAZ GRÁFICA
================================================================================

Versión: 3.0 (Bluetooth Classic)
Fecha: Enero 2026
Plataforma: Python 3.7+ con Tkinter

DESCRIPCIÓN:
Interfaz gráfica avanzada para controlar una silla de ruedas eléctrica mediante
un ESP32 conectado por USB Serial o Bluetooth Classic. Proporciona múltiples 
métodos de control con interfaz visual intuitiva.

CARACTERÍSTICAS PRINCIPALES:
- Joystick Virtual: Control con mouse, 16 direcciones, magnitud proporcional
- Control por Voz Offline: Reconocimiento en español sin internet (Vosk)
- Botones de Función: 3 botones programables (1, 2, 3)
- Visualización en Tiempo Real: Joystick físico, estado BLE, notificaciones
- Interfaz Organizada: 3 columnas (Control, Joystick, Info)

MÉTODOS DE CONTROL:
1. Joystick Virtual (Mouse):
   - Arrastrar en el canvas circular
   - 16 direcciones (sectores de 22.5°)
   - Magnitud proporcional a la distancia del centro
   - Zona muerta de 30 píxeles

2. Control por Voz (Push-to-Talk):
   - Presionar y mantener botón "🎤 PRESIONA Y HABLA"
   - Hablar comandos en español
   - Reconocimiento offline con Vosk
   - Comandos: direcciones + velocidades
   - Ejemplo: "adelante rápido", "izquierda medio", "detener"

3. Botones de Función:
   - Botón 1, 2, 3: Envían comandos "1\n", "2\n", "3\n" al ESP32
   - Funciones definidas en el firmware del ESP32

COMANDOS DE VOZ DISPONIBLES:
Direcciones:
  - adelante, atrás, izquierda, derecha
  - adelante derecha, adelante izquierda
  - atrás derecha, atrás izquierda

Velocidades:
  - lento: 50%
  - medio: 75%
  - rápido: 100%
  - sin especificar: 50% (por defecto)

Detener:
  - detener, alto, parar, stop

Ejemplos:
  - "adelante rápido" → 0° @ 100%
  - "izquierda medio" → 270° @ 75%
  - "adelante derecha lento" → 45° @ 50%
  - "detener" → Detiene la silla

COMUNICACIÓN PC ↔ ESP32:
Soporta DUAL: USB Serial O Bluetooth Classic (SPP)
Baudrate Serial: 115200
Nombre Bluetooth: "ESP32_Wheelchair_BT"

Comandos enviados al ESP32:
  - "JOY,angle,magnitude\n" - Joystick virtual
    Ejemplo: "JOY,45,0.8\n" (45°, magnitud 0.8)
  - "1\n", "2\n", "3\n" - Botones de función

Datos recibidos del ESP32:
  - "STATUS:connected,authenticated" - Estado BLE
  - "PHYSICAL:angle,magnitude" - Posición joystick físico

INTERFAZ GRÁFICA:
┌─────────────────────────────────────────────────────────────┐
│  COLUMNA IZQUIERDA  │  COLUMNA CENTRAL  │  COLUMNA DERECHA  │
│  (Control)          │  (Joystick)       │  (Información)    │
├─────────────────────┼───────────────────┼───────────────────┤
│ • Conexión Serial   │ • Joystick Virtual│ • Estado BLE      │
│ • Control por Voz   │ • Visualización   │ • Joystick Físico │
│ • Botones 1, 2, 3   │ • Indicadores     │ • Notificaciones  │
│ • Comandos de Voz   │                   │                   │
└─────────────────────┴───────────────────┴───────────────────┘

RECONOCIMIENTO DE VOZ OFFLINE:
Utiliza Vosk (https://alphacephei.com/vosk/) para reconocimiento sin internet.

Ventajas:
  - Sin conexión a internet
  - Privacidad total (todo local)
  - Respuesta instantánea (~0.1-0.5 seg)
  - Sin límites de uso
  - Funciona en cualquier lugar

Requisitos:
  - Modelo de idioma español: vosk-model-small-es-0.42 (39 MB)
  - Descargar de: https://alphacephei.com/vosk/models
  - Extraer en la carpeta del programa

DEPENDENCIAS:
- pyserial >= 3.5 - Comunicación serial/Bluetooth con ESP32
- pybluez >= 0.23 - Bluetooth Classic en Windows/Linux (opcional)
- vosk >= 0.3.45 - Reconocimiento de voz offline
- sounddevice >= 0.4.6 - Captura de audio del micrófono
- tkinter - Interfaz gráfica (incluido en Python)

INSTALACIÓN:
1. pip install -r requirements.txt
2. Descargar modelo Vosk: vosk-model-small-es-0.42.zip
3. Extraer en la carpeta del programa
4. Ejecutar: python wheelchair_control_advanced.py

USO:
1. Conectar ESP32 por USB O emparejar por Bluetooth
2. Seleccionar puerto COM o dispositivo Bluetooth
3. Presionar "Conectar"
4. Usar joystick virtual con mouse O control por voz
5. Ver estado en tiempo real

ARQUITECTURA:
- Thread principal: Interfaz gráfica (Tkinter)
- Thread de lectura: Recepción de datos seriales
- Thread de envío: Envío continuo cada 100ms
- Thread de voz: Reconocimiento continuo mientras botón presionado

SEGURIDAD:
- Envío continuo: Mantiene comando activo
- Al soltar joystick/voz: Envía magnitud 0 (detiene silla)
- Timeout en ESP32: 500ms sin comando = parada automática
- Zona muerta: Evita movimientos no intencionales

AUTOR: Proyecto de Maestría en Inteligencia Artificial
RELACIONADO CON: esp32_wheelchair_controller.ino

HISTORIAL DE VERSIONES:
- v1.0: Control por voz online (Google Speech Recognition)
- v2.0: Control por voz offline (Vosk)
- v3.0: Soporte Bluetooth Classic - Versión actual

================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import math
import threading
import time
import json
import queue
import os
import platform
import subprocess
import re

# Imports opcionales según motor de voz
try:
    import sounddevice as sd
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("⚠ Vosk no disponible. Instalar: pip install vosk sounddevice")

try:
    import speech_recognition as sr
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠ Google Speech Recognition no disponible. Instalar: pip install SpeechRecognition PyAudio")

# Imports opcionales para Bluetooth
try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("⚠ PyBluez no disponible. Instalar: pip install pybluez")
    print("  Nota: En Windows puede requerir: pip install pybluez-win10")

class AdvancedWheelchairController:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Avanzado - Silla de Ruedas")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
        
        # Variables de estado
        self.serial_port = None
        self.bluetooth_socket = None
        self.connection_type = None  # 'serial' o 'bluetooth'
        self.is_connected = False
        self.chair_connected = False
        self.chair_authenticated = False
        
        # Joystick virtual
        self.joystick_active = False
        self.current_angle = 0.0
        self.current_magnitude = 0.0
        
        # Joystick físico
        self.physical_angle = 0.0
        self.physical_magnitude = 0.0
        self.physical_active = False
        
        # Canvas
        self.center_x = 200
        self.center_y = 200
        self.max_radius = 150
        self.deadzone_radius = 30
        
        # Threads
        self.read_thread = None
        self.running = False
        self.send_thread = None
        self.send_running = False
        
        # Control por voz (Dual: Vosk/Google)
        self.voice_active = False
        self.voice_listening = False
        self.voice_thread = None
        self.voice_engine = "vosk"  # "vosk" o "google"
        
        # Vosk (Offline)
        self.vosk_model = None
        self.vosk_recognizer = None
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        
        # Google (Online)
        self.google_recognizer = None
        self.microphone = None
        
        # Inicializar motores de voz ANTES de crear interfaz
        self.init_voice_engines()
        
        # Crear interfaz
        self.create_widgets()
        
        # Actualizar lista de puertos y dispositivos Bluetooth
        self.update_device_list()
        
    def init_voice_engines(self):
        """Inicializar motores de reconocimiento de voz disponibles"""
        # Inicializar Vosk (Offline)
        if VOSK_AVAILABLE:
            try:
                model_path = "vosk-model-small-es-0.42"
                
                if not os.path.exists(model_path):
                    print("⚠ Modelo Vosk no encontrado")
                    print("  Descarga desde: https://alphacephei.com/vosk/models")
                else:
                    self.vosk_model = vosk.Model(model_path)
                    self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
                    self.vosk_recognizer.SetWords(True)
                    print("✓ Vosk cargado (offline)")
                    
            except Exception as e:
                print(f"⚠ Error inicializando Vosk: {e}")
        
        # Inicializar Google (Online)
        if GOOGLE_AVAILABLE:
            try:
                self.google_recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                print("✓ Google Speech Recognition disponible (online)")
            except Exception as e:
                print(f"⚠ Error inicializando Google: {e}")
        
        # Determinar motor por defecto
        if self.vosk_model:
            self.voice_engine = "vosk"
            print("→ Motor por defecto: Vosk (offline)")
        elif self.google_recognizer:
            self.voice_engine = "google"
            print("→ Motor por defecto: Google (online)")
        else:
            print("⚠ Ningún motor de voz disponible")
    
    def create_widgets(self):
        # Frame principal dividido en 3 columnas
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ========== COLUMNA IZQUIERDA: Conexión y Control ==========
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5)
        
        # Conexión Serial/Bluetooth
        conn_frame = ttk.LabelFrame(left_frame, text="Conexión ESP32", padding=10)
        conn_frame.pack(fill=tk.X, pady=5)
        
        # Selector de tipo de conexión
        ttk.Label(conn_frame, text="Tipo:").grid(row=0, column=0, padx=5, sticky="w")
        self.conn_type_var = tk.StringVar(value="serial")
        conn_type_frame = ttk.Frame(conn_frame)
        conn_type_frame.grid(row=0, column=1, columnspan=3, sticky="w")
        ttk.Radiobutton(conn_type_frame, text="USB Serial", variable=self.conn_type_var, 
                       value="serial", command=self.update_device_list).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(conn_type_frame, text="Bluetooth", variable=self.conn_type_var, 
                       value="bluetooth", command=self.update_device_list).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(conn_frame, text="Dispositivo:").grid(row=1, column=0, padx=5, sticky="w")
        self.port_combo = ttk.Combobox(conn_frame, width=25, state="readonly")
        self.port_combo.grid(row=1, column=1, columnspan=2, padx=5, sticky="ew")
        
        ttk.Button(conn_frame, text="↻", width=3, command=self.update_device_list).grid(row=1, column=3, padx=2)
        self.connect_btn = ttk.Button(conn_frame, text="Conectar", command=self.toggle_connection)
        self.connect_btn.grid(row=2, column=0, columnspan=4, pady=5, sticky="ew")
        
        self.serial_status = ttk.Label(conn_frame, text="● Desconectado", foreground="red", font=("Arial", 9, "bold"))
        self.serial_status.grid(row=3, column=0, columnspan=4, pady=5)
        
        # Estado BLE
        ble_frame = ttk.LabelFrame(left_frame, text="Estado BLE (ESP32 ↔ Silla)", padding=10)
        ble_frame.pack(fill=tk.X, pady=5)
        
        self.ble_status = ttk.Label(ble_frame, text="● Desconectado", foreground="gray", font=("Arial", 9, "bold"))
        self.ble_status.pack()
        self.auth_status = ttk.Label(ble_frame, text="● No autenticado", foreground="gray", font=("Arial", 9, "bold"))
        self.auth_status.pack()
        
        # Controles BLE
        ble_controls_frame = ttk.Frame(ble_frame)
        ble_controls_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(ble_controls_frame, text="🔍 Escanear Sillas", 
                  command=self.scan_ble_devices, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(ble_controls_frame, text="🔗 Conectar a Silla", 
                  command=self.connect_to_chair, width=15).pack(side=tk.LEFT, padx=2)
        
        # Lista de dispositivos BLE disponibles
        self.ble_devices_label = ttk.Label(ble_frame, text="Dispositivos: --", 
                                           font=("Arial", 8), foreground="gray")
        self.ble_devices_label.pack(pady=2)
        
        # Botones de Función
        btn_frame = ttk.LabelFrame(left_frame, text="Funciones de la Silla", padding=10)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Botón 1", command=self.send_button1, width=15).pack(pady=3)
        ttk.Button(btn_frame, text="Botón 2", command=self.send_button2, width=15).pack(pady=3)
        ttk.Button(btn_frame, text="Botón 3", command=self.send_button3, width=15).pack(pady=3)
        
        # Control por Voz
        voice_frame = ttk.LabelFrame(left_frame, text="Control por Voz", padding=10)
        voice_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(voice_frame, text="Mantén presionado para hablar:", font=("Arial", 9)).pack(pady=5)
        
        self.voice_btn = tk.Button(voice_frame, text="🎤 PRESIONA Y HABLA", 
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                   height=3)
        self.voice_btn.pack(fill=tk.X, pady=5)
        self.voice_btn.bind("<ButtonPress-1>", self.start_voice_control)
        self.voice_btn.bind("<ButtonRelease-1>", self.stop_voice_control)
        
        # Selector de motor de voz
        engine_label_frame = ttk.LabelFrame(voice_frame, text="Motor de Reconocimiento", padding=5)
        engine_label_frame.pack(fill=tk.X, pady=5)
        
        self.voice_engine_var = tk.StringVar(value=self.voice_engine)
        
        # Crear radio buttons (habilitados/deshabilitados según disponibilidad)
        vosk_radio = ttk.Radiobutton(engine_label_frame, text="🔒 Vosk (Offline - Sin Internet)", 
                                     variable=self.voice_engine_var, 
                                     value="vosk", command=self.change_voice_engine)
        vosk_radio.pack(anchor=tk.W, padx=5, pady=2)
        
        google_radio = ttk.Radiobutton(engine_label_frame, text="🌐 Google (Online - Requiere Internet)", 
                                       variable=self.voice_engine_var, 
                                       value="google", command=self.change_voice_engine)
        google_radio.pack(anchor=tk.W, padx=5, pady=2)
        
        # Deshabilitar opciones no disponibles
        if not self.vosk_model:
            vosk_radio.config(state=tk.DISABLED)
            ttk.Label(engine_label_frame, text="  ⚠ Modelo Vosk no encontrado", 
                     foreground="orange", font=("Arial", 8)).pack(anchor=tk.W, padx=20)
        
        if not self.google_recognizer:
            google_radio.config(state=tk.DISABLED)
            ttk.Label(engine_label_frame, text="  ⚠ Google Speech Recognition no instalado", 
                     foreground="orange", font=("Arial", 8)).pack(anchor=tk.W, padx=20)
        
        # Mostrar motor activo
        active_engine = "Vosk (Offline)" if self.voice_engine == "vosk" else "Google (Online)"
        ttk.Label(engine_label_frame, text=f"✓ Activo: {active_engine}", 
                 foreground="green", font=("Arial", 9, "bold")).pack(pady=5)
        
        self.voice_status = ttk.Label(voice_frame, text="Inactivo", foreground="gray")
        self.voice_status.pack()
        
        # Comandos de voz - Área con scroll
        commands_label = ttk.Label(voice_frame, text="Comandos disponibles:", 
                                   font=("Arial", 9, "bold"))
        commands_label.pack(pady=5)
        
        # Frame con scroll para comandos
        commands_scroll_frame = ttk.Frame(voice_frame)
        commands_scroll_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        commands_canvas = tk.Canvas(commands_scroll_frame, height=200, bg="white")
        scrollbar = ttk.Scrollbar(commands_scroll_frame, orient="vertical", command=commands_canvas.yview)
        scrollable_frame = ttk.Frame(commands_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: commands_canvas.configure(scrollregion=commands_canvas.bbox("all"))
        )
        
        commands_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        commands_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Contenido de comandos
        commands_content = [
            ("VELOCIDADES:", "bold", "blue"),
            ("• Lento: 50%", "normal", "black"),
            ("• Medio: 75%", "normal", "black"),
            ("• Rápido: 100%", "normal", "black"),
            ("• Sin especificar: 50%", "normal", "gray"),
            ("", "normal", "black"),
            ("BÁSICAS:", "bold", "blue"),
            ("• adelante [lento/medio/rápido]", "normal", "black"),
            ("• atrás [lento/medio/rápido]", "normal", "black"),
            ("• izquierda [lento/medio/rápido]", "normal", "black"),
            ("• derecha [lento/medio/rápido]", "normal", "black"),
            ("", "normal", "black"),
            ("DIAGONALES:", "bold", "blue"),
            ("• adelante derecha [lento/medio/rápido]", "normal", "black"),
            ("• adelante izquierda [lento/medio/rápido]", "normal", "black"),
            ("• atrás derecha [lento/medio/rápido]", "normal", "black"),
            ("• atrás izquierda [lento/medio/rápido]", "normal", "black"),
            ("", "normal", "black"),
            ("DETENER:", "bold", "red"),
            ("• detener / alto / parar / stop", "normal", "red"),
        ]
        
        for text, weight, color in commands_content:
            label = ttk.Label(scrollable_frame, text=text, 
                            font=("Arial", 8, weight),
                            foreground=color)
            label.pack(anchor="w", padx=5)
        
        commands_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ========== COLUMNA CENTRAL: Joystick ==========
        center_frame = ttk.Frame(main_frame)
        center_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Joystick Virtual
        joy_frame = ttk.LabelFrame(center_frame, text="Joystick Virtual", padding=10)
        joy_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(joy_frame, width=400, height=400, bg="white")
        self.canvas.pack()
        
        self.draw_joystick()
        
        # Eventos del mouse
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # Estado del Joystick
        info_frame = ttk.Frame(center_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.angle_label = ttk.Label(info_frame, text="Ángulo: 0°", font=("Arial", 10, "bold"))
        self.angle_label.pack(side=tk.LEFT, padx=10)
        
        self.magnitude_label = ttk.Label(info_frame, text="Velocidad: 0%", font=("Arial", 10, "bold"))
        self.magnitude_label.pack(side=tk.LEFT, padx=10)
        
        self.direction_label = ttk.Label(info_frame, text="Dir: Neutral", font=("Arial", 10, "bold"))
        self.direction_label.pack(side=tk.LEFT, padx=10)
        
        # ========== COLUMNA DERECHA: Información ==========
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=5)
        
        # Joystick Físico
        phys_frame = ttk.LabelFrame(right_frame, text="Joystick Físico", padding=10)
        phys_frame.pack(fill=tk.X, pady=5)
        
        self.phys_angle_label = ttk.Label(phys_frame, text="Ángulo: --", font=("Arial", 9))
        self.phys_angle_label.pack(anchor="w")
        
        self.phys_mag_label = ttk.Label(phys_frame, text="Velocidad: --", font=("Arial", 9))
        self.phys_mag_label.pack(anchor="w")
        
        self.phys_status_label = ttk.Label(phys_frame, text="Estado: Inactivo", font=("Arial", 9))
        self.phys_status_label.pack(anchor="w")
        
        # Notificaciones del ESP32
        notif_frame = ttk.LabelFrame(right_frame, text="Notificaciones ESP32", padding=10)
        notif_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.notif_text = scrolledtext.ScrolledText(notif_frame, width=35, height=15, 
                                                    font=("Consolas", 8), wrap=tk.WORD)
        self.notif_text.pack(fill=tk.BOTH, expand=True)
        self.notif_text.config(state=tk.DISABLED)
        
        # Botón limpiar notificaciones
        ttk.Button(notif_frame, text="Limpiar", command=self.clear_notifications).pack(pady=5)
        
        # Configurar grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def draw_joystick(self):
        """Dibujar joystick virtual y físico"""
        self.canvas.delete("all")
        
        # Círculo exterior
        self.canvas.create_oval(
            self.center_x - self.max_radius, self.center_y - self.max_radius,
            self.center_x + self.max_radius, self.center_y + self.max_radius,
            outline="black", width=2
        )
        
        # Zona muerta
        self.canvas.create_oval(
            self.center_x - self.deadzone_radius, self.center_y - self.deadzone_radius,
            self.center_x + self.deadzone_radius, self.center_y + self.deadzone_radius,
            outline="gray", width=1, dash=(5, 5)
        )
        
        # Líneas de referencia
        self.canvas.create_line(self.center_x, self.center_y - self.max_radius,
                               self.center_x, self.center_y + self.max_radius,
                               fill="lightgray", dash=(3, 3))
        self.canvas.create_line(self.center_x - self.max_radius, self.center_y,
                               self.center_x + self.max_radius, self.center_y,
                               fill="lightgray", dash=(3, 3))
        
        # Etiquetas
        self.canvas.create_text(self.center_x, self.center_y - self.max_radius - 15,
                               text="N (0°)", font=("Arial", 10, "bold"))
        self.canvas.create_text(self.center_x + self.max_radius + 25, self.center_y,
                               text="E (90°)", font=("Arial", 9))
        self.canvas.create_text(self.center_x, self.center_y + self.max_radius + 15,
                               text="S (180°)", font=("Arial", 9))
        self.canvas.create_text(self.center_x - self.max_radius - 25, self.center_y,
                               text="W (270°)", font=("Arial", 9))
        
        # Centro
        self.canvas.create_oval(self.center_x - 5, self.center_y - 5,
                               self.center_x + 5, self.center_y + 5, fill="red")
        
        # Joystick FÍSICO (verde)
        if self.physical_active:
            rad = math.radians(self.physical_angle)
            distance = self.physical_magnitude * self.max_radius
            phys_x = self.center_x + distance * math.sin(rad)
            phys_y = self.center_y - distance * math.cos(rad)
            
            self.canvas.create_line(self.center_x, self.center_y, phys_x, phys_y,
                                   fill="green", width=2, arrow=tk.LAST, dash=(4, 2))
            self.canvas.create_oval(phys_x - 12, phys_y - 12, phys_x + 12, phys_y + 12,
                                   fill="lightgreen", outline="darkgreen", width=2)
            self.canvas.create_text(phys_x, phys_y - 25, text="Físico",
                                   font=("Arial", 9, "bold"), fill="darkgreen")
        
        # Joystick VIRTUAL (azul)
        if self.joystick_active:
            rad = math.radians(self.current_angle)
            distance = self.current_magnitude * self.max_radius
            stick_x = self.center_x + distance * math.sin(rad)
            stick_y = self.center_y - distance * math.cos(rad)
            
            self.canvas.create_line(self.center_x, self.center_y, stick_x, stick_y,
                                   fill="blue", width=3, arrow=tk.LAST)
            self.canvas.create_oval(stick_x - 15, stick_y - 15, stick_x + 15, stick_y + 15,
                                   fill="blue", outline="darkblue", width=2)
            self.canvas.create_text(stick_x, stick_y + 25, text="Virtual",
                                   font=("Arial", 9, "bold"), fill="darkblue")
        else:
            self.canvas.create_oval(self.center_x - 15, self.center_y - 15,
                                   self.center_x + 15, self.center_y + 15,
                                   fill="lightblue", outline="blue", width=2)
    
    def on_mouse_press(self, event):
        self.update_joystick_position(event.x, event.y)
        
    def on_mouse_drag(self, event):
        self.update_joystick_position(event.x, event.y)
        
    def on_mouse_release(self, event):
        self.joystick_active = False
        self.current_magnitude = 0.0
        self.draw_joystick()
        self.update_info_labels()
        
    def update_joystick_position(self, mouse_x, mouse_y):
        dx = mouse_x - self.center_x
        dy = mouse_y - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        angle_rad = math.atan2(dx, -dy)
        angle_deg = math.degrees(angle_rad)
        if angle_deg < 0:
            angle_deg += 360
        
        if distance > self.deadzone_radius:
            self.joystick_active = True
            self.current_angle = angle_deg
            
            if distance > self.max_radius:
                distance = self.max_radius
            
            normalized_distance = (distance - self.deadzone_radius) / (self.max_radius - self.deadzone_radius)
            self.current_magnitude = max(0.0, min(1.0, normalized_distance))
        else:
            self.joystick_active = False
            self.current_magnitude = 0.0
        
        self.draw_joystick()
        self.update_info_labels()
        
    def update_info_labels(self):
        self.angle_label.config(text=f"Ángulo: {int(self.current_angle)}°")
        
        if self.joystick_active:
            real_magnitude = 30 + (self.current_magnitude * 70)
            self.magnitude_label.config(text=f"Velocidad: {int(real_magnitude)}%")
        else:
            self.magnitude_label.config(text="Velocidad: 0%")
        
        if not self.joystick_active:
            direction = "Neutral"
        else:
            directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                         "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
            sector = int((self.current_angle + 11.25) / 22.5) % 16
            direction = directions[sector]
        
        self.direction_label.config(text=f"Dir: {direction}")
    
    def send_joystick_command(self):
        """Enviar comando al ESP32"""
        if not self.is_connected:
            return
        
        try:
            if self.joystick_active or self.voice_active:
                command = f"JOY,{self.current_angle:.2f},{self.current_magnitude:.3f}\n"
            else:
                command = f"JOY,0.0,0.0\n"
            
            if self.connection_type == 'serial' and self.serial_port:
                self.serial_port.write(command.encode())
                self.serial_port.flush()
            elif self.connection_type == 'bluetooth' and self.bluetooth_socket:
                self.bluetooth_socket.send(command.encode())
            
        except Exception as e:
            self.add_notification(f"Error enviando: {e}", "error")
            self.disconnect()
    
    def send_thread_loop(self):
        """Thread de envío continuo"""
        while self.send_running:
            self.send_joystick_command()
            time.sleep(0.1)
    
    def read_serial_thread(self):
        """Thread de lectura serial o Bluetooth"""
        while self.running:
            try:
                line = None
                
                if self.connection_type == 'serial' and self.serial_port:
                    if self.serial_port.in_waiting > 0:
                        line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                
                elif self.connection_type == 'bluetooth' and self.bluetooth_socket:
                    try:
                        # Configurar timeout para no bloquear
                        self.bluetooth_socket.settimeout(0.1)
                        data = self.bluetooth_socket.recv(1024)
                        if data:
                            # Procesar datos recibidos por Bluetooth
                            decoded = data.decode('utf-8', errors='ignore')
                            for l in decoded.split('\n'):
                                l = l.strip()
                                if l:
                                    self.process_serial_line(l)
                    except Exception:
                        pass
                
                if line:
                    self.process_serial_line(line)
                    
                time.sleep(0.05)
            except Exception as e:
                time.sleep(0.5)
    
    def process_serial_line(self, line):
        """Procesar línea del ESP32"""
        try:
            if line.startswith("STATUS:"):
                parts = line.replace("STATUS:", "").split(",")
                if len(parts) == 2:
                    self.chair_connected = (parts[0] == "1")
                    self.chair_authenticated = (parts[1] == "1")
                    self.root.after(0, self.update_ble_status)
            
            elif line.startswith("BLE_DEVICES:"):
                # Respuesta de escaneo BLE
                devices_str = line.replace("BLE_DEVICES:", "")
                self.root.after(0, lambda: self.ble_devices_label.config(
                    text=f"Dispositivos: {devices_str}", foreground="green"))
                self.root.after(0, lambda: self.add_notification(f"Dispositivos BLE: {devices_str}", "success"))
            
            elif line.startswith("PHYSICAL:"):
                parts = line.replace("PHYSICAL:", "").split(",")
                if len(parts) == 2:
                    try:
                        angle = float(parts[0])
                        magnitude = float(parts[1])
                        
                        if magnitude > 0.01:
                            self.physical_angle = angle
                            self.physical_magnitude = magnitude
                            self.physical_active = True
                        else:
                            self.physical_active = False
                            self.physical_magnitude = 0.0
                        
                        self.root.after(0, self.update_physical_info)
                        self.root.after(0, self.draw_joystick)
                    except ValueError:
                        pass
            
            else:
                # Notificación del ESP32
                self.root.after(0, lambda: self.add_notification(line, "info"))
                
        except Exception as e:
            pass
    
    def update_ble_status(self):
        if self.chair_connected:
            self.ble_status.config(text="● Conectado BLE", foreground="green")
        else:
            self.ble_status.config(text="● Desconectado BLE", foreground="red")
        
        if self.chair_authenticated:
            self.auth_status.config(text="● Autenticado", foreground="green")
        else:
            self.auth_status.config(text="● No autenticado", foreground="orange")
    
    def update_physical_info(self):
        if self.physical_active:
            self.phys_angle_label.config(text=f"Ángulo: {int(self.physical_angle)}°")
            real_mag = 30 + (self.physical_magnitude * 70)
            self.phys_mag_label.config(text=f"Velocidad: {int(real_mag)}%")
            self.phys_status_label.config(text="Estado: Activo", foreground="green")
        else:
            self.phys_angle_label.config(text="Ángulo: --")
            self.phys_mag_label.config(text="Velocidad: --")
            self.phys_status_label.config(text="Estado: Inactivo", foreground="gray")
    
    def add_notification(self, message, msg_type="info"):
        """Agregar notificación al área de texto"""
        self.notif_text.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        if msg_type == "error":
            prefix = "❌"
        elif msg_type == "success":
            prefix = "✓"
        else:
            prefix = "ℹ"
        
        self.notif_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.notif_text.see(tk.END)
        self.notif_text.config(state=tk.DISABLED)
    
    def clear_notifications(self):
        self.notif_text.config(state=tk.NORMAL)
        self.notif_text.delete(1.0, tk.END)
        self.notif_text.config(state=tk.DISABLED)
    
    def send_button1(self):
        if self.is_connected:
            try:
                if self.connection_type == 'serial' and self.serial_port:
                    self.serial_port.write(b"1\n")
                    self.serial_port.flush()
                elif self.connection_type == 'bluetooth' and self.bluetooth_socket:
                    self.bluetooth_socket.send(b"1\n")
                self.add_notification("Botón 1 presionado", "success")
            except Exception as e:
                self.add_notification(f"Error enviando Botón 1: {e}", "error")
    
    def send_button2(self):
        if self.is_connected:
            try:
                if self.connection_type == 'serial' and self.serial_port:
                    self.serial_port.write(b"2\n")
                    self.serial_port.flush()
                elif self.connection_type == 'bluetooth' and self.bluetooth_socket:
                    self.bluetooth_socket.send(b"2\n")
                self.add_notification("Botón 2 presionado", "success")
            except Exception as e:
                self.add_notification(f"Error enviando Botón 2: {e}", "error")
    
    def send_button3(self):
        if self.is_connected:
            try:
                if self.connection_type == 'serial' and self.serial_port:
                    self.serial_port.write(b"3\n")
                    self.serial_port.flush()
                elif self.connection_type == 'bluetooth' and self.bluetooth_socket:
                    self.bluetooth_socket.send(b"3\n")
                self.add_notification("Botón 3 presionado", "success")
            except Exception as e:
                self.add_notification(f"Error enviando Botón 3: {e}", "error")
    
    def scan_ble_devices(self):
        """Solicitar al ESP32 que escanee dispositivos BLE"""
        if not self.is_connected:
            messagebox.showwarning("Advertencia", "Conecta al ESP32 primero")
            return
        
        self.add_notification("Escaneando dispositivos BLE...", "info")
        self.ble_devices_label.config(text="Dispositivos: Escaneando...", foreground="orange")
        
        # Enviar comando de escaneo al ESP32
        try:
            if self.connection_type == 'serial' and self.serial_port:
                self.serial_port.write(b"SCAN_BLE\n")
                self.serial_port.flush()
            elif self.connection_type == 'bluetooth' and self.bluetooth_socket:
                self.bluetooth_socket.send(b"SCAN_BLE\n")
            
            # El ESP32 responderá con la lista de dispositivos
            # Esto se procesará en read_serial_thread
        except Exception as e:
            self.add_notification(f"Error escaneando: {e}", "error")
            self.ble_devices_label.config(text="Dispositivos: Error", foreground="red")
    
    def connect_to_chair(self):
        """Solicitar al ESP32 que se conecte a la silla"""
        if not self.is_connected:
            messagebox.showwarning("Advertencia", "Conecta al ESP32 primero")
            return
        
        self.add_notification("Conectando ESP32 a silla...", "info")
        
        # Enviar comando de conexión al ESP32
        try:
            if self.connection_type == 'serial' and self.serial_port:
                self.serial_port.write(b"CONNECT_CHAIR\n")
                self.serial_port.flush()
            elif self.connection_type == 'bluetooth' and self.bluetooth_socket:
                self.bluetooth_socket.send(b"CONNECT_CHAIR\n")
            
            # El ESP32 responderá con el estado de conexión
        except Exception as e:
            self.add_notification(f"Error conectando: {e}", "error")
    
    def change_voice_engine(self):
        """Cambiar motor de reconocimiento de voz"""
        self.voice_engine = self.voice_engine_var.get()
        engine_name = "Vosk (Offline)" if self.voice_engine == "vosk" else "Google (Online)"
        print(f"→ Motor de voz cambiado a: {engine_name}")
        self.add_notification(f"Motor de voz: {engine_name}", "info")
    
    def start_voice_control(self, event):
        """Iniciar control por voz (Vosk o Google según selección)"""
        if not self.is_connected:
            messagebox.showwarning("Advertencia", "Conecta al ESP32 primero")
            return
        
        # Verificar que el motor seleccionado esté disponible
        if self.voice_engine == "vosk" and self.vosk_model is None:
            messagebox.showwarning("Advertencia", "Modelo Vosk no cargado")
            return
        
        if self.voice_engine == "google" and self.google_recognizer is None:
            messagebox.showwarning("Advertencia", "Google Speech Recognition no disponible")
            return
        
        self.voice_active = True
        self.voice_listening = True
        self.voice_btn.config(bg="#f44336", text="🎤 ESCUCHANDO...")
        
        # Iniciar thread según motor seleccionado
        if self.voice_engine == "vosk":
            self.voice_status.config(text="🎤 Escuchando (Vosk - Offline)...", foreground="red")
            self.voice_thread = threading.Thread(target=self.continuous_voice_recognition_vosk, daemon=True)
        else:  # google
            self.voice_status.config(text="🎤 Escuchando (Google - Online)...", foreground="red")
            self.voice_thread = threading.Thread(target=self.continuous_voice_recognition_google, daemon=True)
        
        self.voice_thread.start()
    
    def stop_voice_control(self, event):
        """Detener control por voz"""
        self.voice_listening = False
        self.voice_active = False
        self.joystick_active = False
        self.current_magnitude = 0.0
        self.voice_btn.config(bg="#4CAF50", text="🎤 PRESIONA Y HABLA")
        self.voice_status.config(text="Detenido", foreground="gray")
        self.draw_joystick()
        self.update_info_labels()
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback para captura de audio continua"""
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def continuous_voice_recognition_vosk(self):
        """Escucha continua con Vosk (offline) mientras el botón esté presionado"""
        try:
            # Abrir stream de audio
            with sd.RawInputStream(samplerate=self.sample_rate, blocksize=8000, dtype='int16',
                                  channels=1, callback=self.audio_callback):
                
                self.root.after(0, lambda: self.voice_status.config(
                    text="🎤 Escuchando (offline)...", foreground="red"))
                
                # Procesar audio continuamente
                while self.voice_listening:
                    try:
                        data = self.audio_queue.get(timeout=0.5)
                        
                        if self.vosk_recognizer.AcceptWaveform(data):
                            # Resultado final
                            result = json.loads(self.vosk_recognizer.Result())
                            if result.get("text"):
                                command = result["text"].lower()
                                self.root.after(0, lambda cmd=command: self.add_notification(f"🎤 '{cmd}'", "info"))
                                self.root.after(0, lambda cmd=command: self.process_voice_command(cmd))
                        else:
                            # Resultado parcial (opcional, para feedback)
                            partial = json.loads(self.vosk_recognizer.PartialResult())
                            if partial.get("partial"):
                                partial_text = partial["partial"]
                                self.root.after(0, lambda txt=partial_text: self.voice_status.config(
                                    text=f"🎤 {txt}...", foreground="orange"))
                    
                    except queue.Empty:
                        # No hay audio, continuar
                        continue
                    except Exception as e:
                        if self.voice_listening:
                            print(f"Error procesando audio: {e}")
                            continue
                        else:
                            break
                            
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.add_notification(f"Error micrófono: {err}", "error"))
        finally:
            # Limpiar queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    pass
            
            # Resetear reconocedor
            if self.vosk_recognizer:
                self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
            
            if not self.voice_listening:
                self.root.after(0, lambda: self.voice_status.config(text="Detenido", foreground="gray"))
    
    def continuous_voice_recognition_google(self):
        """Escucha continua con Google Speech Recognition (online) mientras el botón esté presionado"""
        try:
            with self.microphone as source:
                self.google_recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                self.root.after(0, lambda: self.voice_status.config(
                    text="🎤 Escuchando (Google - Online)...", foreground="red"))
                
                # Escuchar continuamente mientras voice_listening sea True
                while self.voice_listening:
                    try:
                        # Escuchar con timeout corto
                        audio = self.google_recognizer.listen(source, timeout=2, phrase_time_limit=3)
                        
                        # Reconocer en español
                        command = self.google_recognizer.recognize_google(audio, language="es-ES").lower()
                        self.root.after(0, lambda cmd=command: self.add_notification(f"🎤 '{cmd}'", "info"))
                        self.root.after(0, lambda cmd=command: self.process_voice_command(cmd))
                        
                    except sr.WaitTimeoutError:
                        # Timeout normal, continuar escuchando
                        if self.voice_listening:
                            continue
                        else:
                            break
                    except sr.UnknownValueError:
                        # No se entendió, continuar escuchando
                        if self.voice_listening:
                            self.root.after(0, lambda: self.voice_status.config(
                                text="No entendido, intenta de nuevo", foreground="orange"))
                            time.sleep(0.5)
                            continue
                        else:
                            break
                    except Exception as e:
                        if self.voice_listening:
                            self.root.after(0, lambda err=str(e): self.add_notification(f"Error: {err}", "error"))
                            time.sleep(0.5)
                            continue
                        else:
                            break
                            
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.add_notification(f"Error micrófono: {err}", "error"))
        finally:
            if not self.voice_listening:
                self.root.after(0, lambda: self.voice_status.config(text="Detenido", foreground="gray"))
    
    def process_voice_command(self, command):
        """Procesar comando de voz"""
        # Detener
        if any(word in command for word in ["detener", "alto", "parar", "stop"]):
            self.joystick_active = False
            self.current_magnitude = 0.0
            self.voice_status.config(text="Comando: DETENER", foreground="red")
            self.draw_joystick()
            self.update_info_labels()
            return
        
        # Determinar velocidad (por defecto 50% si no se especifica)
        magnitude = 0.5  # 50% por defecto
        if "rápido" in command or "rápida" in command:
            magnitude = 1.0  # 100%
        elif "medio" in command or "media" in command:
            magnitude = 0.75  # 75%
        elif "lento" in command or "lenta" in command or "despacio" in command:
            magnitude = 0.5  # 50%
        
        # Determinar dirección
        angle = None
        
        # Adelante (con o sin diagonal)
        if "adelante" in command or "avanza" in command or "avanzar" in command:
            if "derecha" in command:
                angle = 45  # NE - Adelante derecha
            elif "izquierda" in command:
                angle = 315  # NW - Adelante izquierda
            else:
                angle = 0  # N - Adelante
        
        # Atrás (con o sin diagonal)
        elif "atrás" in command or "retrocede" in command or "retroceder" in command:
            if "derecha" in command:
                angle = 135  # SE - Atrás derecha
            elif "izquierda" in command:
                angle = 225  # SW - Atrás izquierda
            else:
                angle = 180  # S - Atrás
        
        # Derecha sola
        elif "derecha" in command:
            angle = 90  # E - Derecha
        
        # Izquierda sola
        elif "izquierda" in command:
            angle = 270  # W - Izquierda
        
        if angle is not None:
            self.joystick_active = True
            self.current_angle = angle
            self.current_magnitude = magnitude
            
            # Mostrar dirección y velocidad
            direction_names = {
                0: "Adelante", 45: "Adelante-Derecha", 90: "Derecha", 135: "Atrás-Derecha",
                180: "Atrás", 225: "Atrás-Izquierda", 270: "Izquierda", 315: "Adelante-Izquierda"
            }
            dir_name = direction_names.get(angle, f"{angle}°")
            speed_pct = int(magnitude * 100)
            
            self.voice_status.config(text=f"{dir_name} @ {speed_pct}%", foreground="green")
            self.draw_joystick()
            self.update_info_labels()
        else:
            self.add_notification("Comando no reconocido", "error")
    
    def update_device_list(self):
        """Actualizar lista de dispositivos según tipo de conexión"""
        conn_type = self.conn_type_var.get()
        
        if conn_type == "serial":
            # Listar puertos seriales
            ports = serial.tools.list_ports.comports()
            device_list = [port.device for port in ports]
            self.port_combo['values'] = device_list
            if device_list:
                self.port_combo.current(0)
        
        elif conn_type == "bluetooth":
            # Listar dispositivos Bluetooth
            self.port_combo['values'] = ["Buscando..."]
            self.port_combo.current(0)
            # Buscar en thread separado para no bloquear UI
            threading.Thread(target=self._search_bluetooth_devices, daemon=True).start()
    
    def _search_bluetooth_devices(self):
        """Buscar dispositivos Bluetooth (thread separado)"""
        try:
            bt_devices = self.find_bluetooth_devices()
            self.root.after(0, lambda: self._update_bluetooth_list(bt_devices))
        except Exception as e:
            self.root.after(0, lambda: self.add_notification(f"Error buscando Bluetooth: {e}", "error"))
            self.root.after(0, lambda: self.port_combo.configure(values=["Sin dispositivos"]))
    
    def _update_bluetooth_list(self, devices):
        """Actualizar lista de dispositivos Bluetooth en UI"""
        if devices:
            # Formato: "COM5 - Serie estándar sobre el vínculo Bluetooth"
            device_list = [f"{addr} - {name}" for addr, name in devices]
            self.port_combo['values'] = device_list
            # Seleccionar el primero por defecto
            self.port_combo.current(0)
        else:
            self.port_combo['values'] = ["Sin dispositivos"]
            self.port_combo.current(0)
    
    def find_bluetooth_devices(self):
        """Buscar dispositivos Bluetooth emparejados"""
        devices = []
        
        if platform.system() == "Windows":
            # En Windows, buscar directamente puertos COM de Bluetooth
            try:
                ports = serial.tools.list_ports.comports()
                for port in ports:
                    # Buscar puertos que sean Bluetooth
                    if "Bluetooth" in port.description or "bluetooth" in port.description.lower():
                        # Agregar todos los puertos Bluetooth encontrados
                        device_name = port.description
                        devices.append((port.device, device_name))
                        print(f"Bluetooth encontrado: {port.device} - {device_name}")
            except Exception as e:
                print(f"Error buscando dispositivos Bluetooth: {e}")
        
        elif BLUETOOTH_AVAILABLE:
            # En Linux/Mac, usar PyBluez
            try:
                nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)
                for addr, name in nearby_devices:
                    devices.append((addr, name))
            except:
                pass
        
        return devices
    
    def toggle_connection(self):
        if self.is_connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        device = self.port_combo.get()
        if not device or device in ["Buscando...", "Sin dispositivos"]:
            messagebox.showerror("Error", "Selecciona un dispositivo válido")
            return
        
        conn_type = self.conn_type_var.get()
        
        try:
            if conn_type == "serial":
                # Conexión Serial USB
                self.serial_port = serial.Serial(device, 115200, timeout=0.1)
                self.connection_type = 'serial'
                time.sleep(2)
                status_text = f"● Conectado USB ({device})"
                
            elif conn_type == "bluetooth":
                # Conexión Bluetooth
                # Extraer puerto COM del formato "COM5 - Descripción"
                com_port = device.split(" - ")[0].strip()
                
                if com_port.startswith("COM"):
                    # Windows: Usar puerto COM directamente
                    self.serial_port = serial.Serial(com_port, 115200, timeout=0.1)
                    self.connection_type = 'serial'
                    time.sleep(2)
                    status_text = f"● Conectado BT ({com_port})"
                elif BLUETOOTH_AVAILABLE:
                    # Linux/Mac: Conexión Bluetooth directa con PyBluez
                    # Extraer dirección MAC del formato "Name (XX:XX:XX:XX:XX:XX)"
                    match = re.search(r'\(([0-9A-Fa-f:]+)\)', device)
                    if match:
                        addr = match.group(1)
                        port = 1  # Puerto RFCOMM estándar para SPP
                        self.bluetooth_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                        self.bluetooth_socket.connect((addr, port))
                        self.connection_type = 'bluetooth'
                        time.sleep(1)
                        status_text = f"● Conectado BT ({addr})"
                    else:
                        raise Exception("Formato de dispositivo no válido")
                else:
                    # Buscar puerto COM asociado
                    bt_port = self._find_bluetooth_com_port(device)
                    if bt_port:
                        self.serial_port = serial.Serial(bt_port, 115200, timeout=0.1)
                        self.connection_type = 'serial'
                        time.sleep(2)
                        status_text = f"● Conectado BT ({bt_port})"
                    else:
                        raise Exception("PyBluez no disponible y no se encontró puerto COM")
            
            self.is_connected = True
            self.serial_status.config(text=status_text, foreground="green")
            self.connect_btn.config(text="Desconectar")
            self.port_combo.config(state="disabled")
            
            # Iniciar threads
            self.running = True
            self.read_thread = threading.Thread(target=self.read_serial_thread, daemon=True)
            self.read_thread.start()
            
            self.send_running = True
            self.send_thread = threading.Thread(target=self.send_thread_loop, daemon=True)
            self.send_thread.start()
            
            self.add_notification(f"Conectado: {status_text}", "success")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar:\n{e}")
            self.serial_port = None
            self.bluetooth_socket = None
            self.is_connected = False
    
    def _find_bluetooth_com_port(self, device_name):
        """Buscar puerto COM asociado a dispositivo Bluetooth en Windows"""
        if platform.system() != "Windows":
            return None
        
        try:
            # Buscar en puertos seriales
            ports = serial.tools.list_ports.comports()
            
            # Primero buscar coincidencia exacta con el nombre del dispositivo
            for port in ports:
                if "ESP32" in port.description or "Wheelchair" in port.description:
                    print(f"Encontrado puerto Bluetooth: {port.device} - {port.description}")
                    return port.device
            
            # Luego buscar cualquier puerto Bluetooth
            for port in ports:
                if "Bluetooth" in port.description or "Standard Serial over Bluetooth" in port.description:
                    print(f"Encontrado puerto Bluetooth genérico: {port.device} - {port.description}")
                    return port.device
            
            # Finalmente, buscar por nombre parcial
            for port in ports:
                if device_name and device_name.lower() in port.description.lower():
                    print(f"Encontrado puerto por nombre: {port.device} - {port.description}")
                    return port.device
                    
        except Exception as e:
            print(f"Error buscando puerto COM: {e}")
        
        return None
    
    def disconnect(self):
        self.send_running = False
        if self.send_thread:
            self.send_thread.join(timeout=1)
        
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=1)
        
        # Enviar comando de parada
        try:
            if self.connection_type == 'serial' and self.serial_port:
                self.serial_port.write(b"JOY,0.0,0.0\n")
                time.sleep(0.1)
                self.serial_port.close()
            elif self.connection_type == 'bluetooth' and self.bluetooth_socket:
                self.bluetooth_socket.send(b"JOY,0.0,0.0\n")
                time.sleep(0.1)
                self.bluetooth_socket.close()
        except:
            pass
        
        self.serial_port = None
        self.bluetooth_socket = None
        self.connection_type = None
        self.is_connected = False
        self.chair_connected = False
        self.chair_authenticated = False
        
        self.serial_status.config(text="● Desconectado", foreground="red")
        self.ble_status.config(text="● Desconectado BLE", foreground="gray")
        self.auth_status.config(text="● No autenticado", foreground="gray")
        self.connect_btn.config(text="Conectar")
        self.port_combo.config(state="readonly")
        
        self.joystick_active = False
        self.current_magnitude = 0.0
        self.physical_active = False
        self.physical_magnitude = 0.0
        self.draw_joystick()
        self.update_info_labels()
        self.update_physical_info()
        
        self.add_notification("Desconectado", "info")
    
    def on_closing(self):
        self.disconnect()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AdvancedWheelchairController(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
