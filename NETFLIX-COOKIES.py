#!/usr/bin/env python3
"""
Netflix NFToken Generator - Professional Edition
Author: 工V龱尺ㄚ㇌7
Version: 2.0 Professional
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import requests
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import time

# Configuración de colores profesional
COLORS = {
    'bg_dark': '#1e1e2e',      # Fondo principal
    'bg_light': '#2d2d3f',      # Fondo secundario
    'fg_light': '#cdd6f4',      # Texto principal
    'fg_gray': '#6c7086',       # Texto secundario
    'accent': '#89b4fa',        # Azul acento
    'success': '#a6e3a1',       # Verde éxito
    'warning': '#f9e2af',       # Amarillo advertencia
    'error': '#f38ba8',         # Rojo error
    'button_bg': '#313244',     # Fondo botón
    'button_hover': '#45475a',  # Fondo botón hover
    'entry_bg': '#181825',      # Fondo entrada
    'border': '#585b70'         # Bordes
}

class VerificadorTokenNetflix:
    """Clase principal para verificación de tokens Netflix"""
    
    def __init__(self):
        self.sesion = requests.Session()
        self.cabeceras = {
            'User-Agent': 'com.netflix.mediaclient/63884 (Linux; U; Android 13; ro; M2007J3SG; Build/TQ1A.230205.001.A2; Cronet/143.0.7445.0)',
            'Accept': 'multipart/mixed;deferSpec=20220824, application/graphql-response+json, application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://www.netflix.com',
            'Referer': 'https://www.netflix.com/'
        }
        self.url_api = 'https://android13.prod.ftl.netflix.com/graphql'

    def extraer_cookies_de_texto(self, texto: str) -> List[Dict[str, str]]:
        """Extrae todas las cookies NetflixId, SecureNetflixId y nfvdid del texto."""
        lineas = texto.split('\n')
        conjuntos_cookies = []
        
        patron_netflixid = r'NetflixId=([^;\s]+)'
        patron_secure = r'SecureNetflixId=([^;\s]+)'
        patron_nfvdid = r'nfvdid=([^;\s]+)'
        
        for linea in lineas:
            cookie_dict = {}
            
            match = re.search(patron_netflixid, linea)
            if match:
                cookie_dict['NetflixId'] = match.group(1)
            
            match = re.search(patron_secure, linea)
            if match:
                cookie_dict['SecureNetflixId'] = match.group(1)
            
            match = re.search(patron_nfvdid, linea)
            if match:
                cookie_dict['nfvdid'] = match.group(1)
            
            if 'NetflixId' in cookie_dict:
                if 'SecureNetflixId' not in cookie_dict:
                    cookie_dict['SecureNetflixId'] = ''
                if 'nfvdid' not in cookie_dict:
                    cookie_dict['nfvdid'] = ''
                conjuntos_cookies.append(cookie_dict)
        
        return conjuntos_cookies

    def construir_cadena_cookie(self, diccionario_cookie: Dict[str, str]) -> str:
        """Construye una cadena de cookie '; ' a partir del diccionario."""
        filtrado = {k: v for k, v in diccionario_cookie.items() if v}
        return '; '.join([f"{k}={v}" for k, v in filtrado.items()])

    def generar_token(self, diccionario_cookie: Dict[str, str]) -> Tuple[bool, Optional[str], Optional[str]]:
        """Envía la petición GraphQL a Netflix para generar el NFToken."""
        
        if not diccionario_cookie.get('NetflixId'):
            return False, None, "La cookie 'NetflixId' está vacía o no se encontró."

        cadena_cookie = self.construir_cadena_cookie(diccionario_cookie)

        payload = {
            "operationName": "CreateAutoLoginToken",
            "variables": {"scope": "WEBVIEW_MOBILE_STREAMING"},
            "extensions": {
                "persistedQuery": {
                    "version": 102,
                    "id": "76e97129-f4b5-41a0-a73c-12e674896849"
                }
            }
        }
        cabeceras = self.cabeceras.copy()
        cabeceras['Cookie'] = cadena_cookie

        try:
            respuesta = self.sesion.post(self.url_api, headers=cabeceras, json=payload, timeout=30)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                if 'data' in datos and datos['data'] and 'createAutoLoginToken' in datos['data']:
                    return True, datos['data']['createAutoLoginToken'], None
                elif 'errors' in datos:
                    return False, None, f"Error de API: {datos['errors'][0].get('message', 'Error desconocido')}"
                else:
                    return False, None, f"Respuesta inesperada: {datos}"
            elif respuesta.status_code == 401:
                return False, None, "Cookie caducada (401 No autorizado)"
            else:
                return False, None, f"HTTP {respuesta.status_code}: {respuesta.text[:200]}"
        except Exception as e:
            return False, None, f"Error de conexión: {str(e)}"

    def formatear_enlace_nftoken(self, token: str) -> str:
        """Formatea el token en un enlace utilizable."""
        return f"https://netflix.com/?nftoken={token}"


class BotonModerno(tk.Canvas):
    """Botón personalizado con efectos hover"""
    
    def __init__(self, parent, texto, comando, color=COLORS['accent'], **kwargs):
        super().__init__(parent, **kwargs)
        self.comando = comando
        self.texto = texto
        self.color = color
        self.color_hover = COLORS['button_hover']
        
        self.configure(
            width=200,
            height=40,
            bg=COLORS['bg_dark'],
            highlightthickness=0
        )
        
        self.dibujar_boton(color)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
    def dibujar_boton(self, color):
        self.delete('all')
        self.create_rounded_rect(0, 0, 200, 40, 10, fill=color, outline=color)
        self.create_text(100, 20, text=self.texto, fill='white', font=('Segoe UI', 11, 'bold'))
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, event):
        self.dibujar_boton(self.color_hover)
        
    def on_leave(self, event):
        self.dibujar_boton(self.color)
        
    def on_click(self, event):
        if self.comando:
            self.comando()


class InterfazNFToken:
    """Interfaz gráfica profesional"""
    
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("🎬 Netflix NFToken Generator - Professional Edition")
        self.ventana.geometry("850x750")
        self.ventana.configure(bg=COLORS['bg_dark'])
        
        self.verificador = VerificadorTokenNetflix()
        self.archivo_entrada = None
        self.archivo_salida = None
        self.procesando = False
        self.detener_solicitado = False

        self.texto_estado = tk.StringVar()
        self.texto_estado.set("✨ Listo para comenzar")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura todos los elementos de la interfaz"""
        
        # Encabezado con autor
        header_frame = tk.Frame(self.ventana, bg=COLORS['bg_dark'])
        header_frame.pack(pady=20)
        
        titulo = tk.Label(
            header_frame,
            text="🎬 NFToken Generator",
            font=('Segoe UI', 24, 'bold'),
            bg=COLORS['bg_dark'],
            fg=COLORS['accent']
        )
        titulo.pack()
        
        autor = tk.Label(
            header_frame,
            text="by 工V龱尺ㄚ㇌7",
            font=('Segoe UI', 12, 'italic'),
            bg=COLORS['bg_dark'],
            fg=COLORS['fg_gray']
        )
        autor.pack()
        
        # Línea decorativa
        separator = tk.Frame(self.ventana, height=2, bg=COLORS['border'])
        separator.pack(fill=tk.X, padx=50, pady=10)
        
        # Marco de archivos
        files_frame = tk.Frame(self.ventana, bg=COLORS['bg_dark'])
        files_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Archivo de entrada
        input_frame = tk.Frame(files_frame, bg=COLORS['bg_light'], relief=tk.FLAT, bd=2)
        input_frame.pack(pady=5, fill=tk.X, ipadx=10, ipady=10)
        
        tk.Label(
            input_frame,
            text="📂 ARCHIVO DE ENTRADA",
            font=('Segoe UI', 9, 'bold'),
            bg=COLORS['bg_light'],
            fg=COLORS['fg_gray']
        ).pack(anchor=tk.W, padx=10)
        
        input_subframe = tk.Frame(input_frame, bg=COLORS['bg_light'])
        input_subframe.pack(fill=tk.X, padx=10)
        
        self.entrada_label = tk.Label(
            input_subframe,
            text="Ningún archivo seleccionado",
            font=('Segoe UI', 10),
            bg=COLORS['bg_light'],
            fg=COLORS['fg_gray'],
            anchor=tk.W
        )
        self.entrada_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            input_subframe,
            text="Seleccionar",
            command=self.seleccionar_archivo_entrada,
            bg=COLORS['button_bg'],
            fg=COLORS['fg_light'],
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.RIGHT)
        
        # Archivo de salida
        output_frame = tk.Frame(files_frame, bg=COLORS['bg_light'], relief=tk.FLAT, bd=2)
        output_frame.pack(pady=5, fill=tk.X, ipadx=10, ipady=10)
        
        tk.Label(
            output_frame,
            text="💾 ARCHIVO DE SALIDA",
            font=('Segoe UI', 9, 'bold'),
            bg=COLORS['bg_light'],
            fg=COLORS['fg_gray']
        ).pack(anchor=tk.W, padx=10)
        
        output_subframe = tk.Frame(output_frame, bg=COLORS['bg_light'])
        output_subframe.pack(fill=tk.X, padx=10)
        
        self.salida_label = tk.Label(
            output_subframe,
            text="No seleccionado",
            font=('Segoe UI', 10),
            bg=COLORS['bg_light'],
            fg=COLORS['fg_gray'],
            anchor=tk.W
        )
        self.salida_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            output_subframe,
            text="Seleccionar",
            command=self.seleccionar_archivo_salida,
            bg=COLORS['button_bg'],
            fg=COLORS['fg_light'],
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.RIGHT)
        
        # Barra de progreso
        self.progress_frame = tk.Frame(self.ventana, bg=COLORS['bg_dark'])
        self.progress_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=('Segoe UI', 9),
            bg=COLORS['bg_dark'],
            fg=COLORS['fg_gray']
        )
        self.progress_label.pack()
        
        self.progress_bar = tk.Canvas(
            self.progress_frame,
            height=6,
            bg=COLORS['entry_bg'],
            highlightthickness=0
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.progress_bar_width = 0
        
        # Marco de botones
        buttons_frame = tk.Frame(self.ventana, bg=COLORS['bg_dark'])
        buttons_frame.pack(pady=20)
        
        self.boton_iniciar = BotonModerno(
            buttons_frame,
            "🚀 INICIAR",
            self.iniciar_procesamiento,
            width=200,
            height=40
        )
        self.boton_iniciar.pack(side=tk.LEFT, padx=10)
        
        self.boton_detener = BotonModerno(
            buttons_frame,
            "⏹️ DETENER",
            self.solicitar_detener,
            color=COLORS['error'],
            width=150,
            height=40
        )
        self.boton_detener.pack(side=tk.LEFT, padx=10)
        self.boton_detener.configure(state=tk.DISABLED)
        
        # Área de log
        log_label = tk.Label(
            self.ventana,
            text="📋 REGISTRO DE ACTIVIDAD",
            font=('Segoe UI', 10, 'bold'),
            bg=COLORS['bg_dark'],
            fg=COLORS['fg_gray']
        )
        log_label.pack(anchor=tk.W, padx=20)
        
        log_frame = tk.Frame(self.ventana, bg=COLORS['border'])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.area_log = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            bg=COLORS['entry_bg'],
            fg=COLORS['fg_light'],
            font=('Consolas', 10),
            insertbackground=COLORS['fg_light'],
            relief=tk.FLAT,
            borderwidth=0
        )
        self.area_log.pack(fill=tk.BOTH, expand=True)
        
        # Barra de estado
        status_frame = tk.Frame(self.ventana, bg=COLORS['bg_light'], height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(
            status_frame,
            textvariable=self.texto_estado,
            font=('Segoe UI', 9),
            bg=COLORS['bg_light'],
            fg=COLORS['fg_light']
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Configurar tags de color para el log
        self.area_log.tag_config('success', foreground=COLORS['success'])
        self.area_log.tag_config('error', foreground=COLORS['error'])
        self.area_log.tag_config('warning', foreground=COLORS['warning'])
        self.area_log.tag_config('info', foreground=COLORS['accent'])
        
    def log(self, mensaje, tipo='info'):
        """Añade un mensaje al área de log con formato"""
        def _escribir():
            self.area_log.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.area_log.insert(tk.END, f"[{timestamp}] ", 'info')
            self.area_log.insert(tk.END, mensaje + "\n", tipo)
            self.area_log.see(tk.END)
            self.area_log.config(state=tk.DISABLED)
        self.ventana.after(0, _escribir)

    def actualizar_progreso(self, actual, total):
        """Actualiza la barra de progreso"""
        porcentaje = (actual / total) * 100
        self.progress_label.config(text=f"Progreso: {actual}/{total} ({porcentaje:.1f}%)")
        
        def _dibujar():
            self.progress_bar.delete('all')
            ancho = int((self.progress_bar.winfo_width() * actual) / total)
            self.progress_bar.create_rectangle(0, 0, ancho, 6, fill=COLORS['accent'], outline='')
        self.ventana.after(0, _dibujar)

    def seleccionar_archivo_entrada(self):
        nombre_archivo = filedialog.askopenfilename(
            title="Selecciona el archivo de cookies",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if nombre_archivo:
            self.archivo_entrada = nombre_archivo
            self.entrada_label.config(text=os.path.basename(nombre_archivo), fg=COLORS['fg_light'])
            self.log(f"📁 Archivo seleccionado: {os.path.basename(nombre_archivo)}", 'success')

    def seleccionar_archivo_salida(self):
        nombre_archivo = filedialog.asksaveasfilename(
            title="Selecciona el archivo de salida",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if nombre_archivo:
            self.archivo_salida = nombre_archivo
            self.salida_label.config(text=os.path.basename(nombre_archivo), fg=COLORS['fg_light'])
            self.log(f"💾 Archivo de salida: {os.path.basename(nombre_archivo)}", 'success')

    def solicitar_detener(self):
        self.detener_solicitado = True
        self.log("⏹️ DETENIENDO proceso...", 'warning')
        self.boton_detener.configure(state=tk.DISABLED)

    def iniciar_procesamiento(self):
        if not self.archivo_entrada:
            messagebox.showwarning("Error", "❌ Selecciona un archivo de entrada")
            return
        if not self.archivo_salida:
            self.seleccionar_archivo_salida()
            if not self.archivo_salida:
                return

        self.procesando = True
        self.detener_solicitado = False
        self.boton_iniciar.configure(state=tk.DISABLED)
        self.boton_detener.configure(state=tk.NORMAL)

        hilo = threading.Thread(target=self.procesar_archivo, daemon=True)
        hilo.start()

    def finalizar_procesamiento(self, mensaje_estado):
        self.procesando = False
        self.boton_iniciar.configure(state=tk.NORMAL)
        self.boton_detener.configure(state=tk.DISABLED)
        self.texto_estado.set(mensaje_estado)
        self.progress_label.config(text="")

    def procesar_archivo(self):
        self.log("🚀 INICIANDO procesamiento...", 'info')
        self.texto_estado.set("Procesando...")

        try:
            with open(self.archivo_entrada, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
        except Exception as e:
            self.log(f"❌ Error de lectura: {e}", 'error')
            self.finalizar_procesamiento("Error de lectura")
            return

        lista_cookies = self.verificador.extraer_cookies_de_texto(contenido)
        
        if not lista_cookies:
            self.log("❌ No se encontraron cookies", 'error')
            self.finalizar_procesamiento("Sin cookies")
            return

        total_con_netflixid = sum(1 for c in lista_cookies if c.get('NetflixId'))
        total_con_secure = sum(1 for c in lista_cookies if c.get('SecureNetflixId'))
        total_con_nfvdid = sum(1 for c in lista_cookies if c.get('nfvdid'))
        
        self.log(f"📊 Cookies encontradas: {len(lista_cookies)}", 'success')
        self.log(f"   • NetflixId: {total_con_netflixid}", 'info')
        self.log(f"   • SecureNetflixId: {total_con_secure}", 'warning' if total_con_secure == 0 else 'success')
        self.log(f"   • nfvdid: {total_con_nfvdid}", 'warning' if total_con_nfvdid == 0 else 'success')

        if total_con_secure == 0 or total_con_nfvdid == 0:
            self.log("⚠️  ADVERTENCIA: Faltan cookies de seguridad", 'warning')
            self.log("   Los tokens probablemente NO funcionarán", 'warning')

        resultados_validos = []
        total_procesados = 0

        for idx, cookie in enumerate(lista_cookies, 1):
            if self.detener_solicitado:
                self.log(f"⏹️ Proceso detenido en juego {idx-1}", 'warning')
                break

            self.actualizar_progreso(idx, len(lista_cookies))
            self.log(f"▶️ Procesando {idx}/{len(lista_cookies)}", 'info')
            
            tiene_netflix = "✅" if cookie.get('NetflixId') else "❌"
            tiene_secure = "✅" if cookie.get('SecureNetflixId') else "❌"
            tiene_nfvdid = "✅" if cookie.get('nfvdid') else "❌"
            self.log(f"   Cookies: {tiene_netflix} | {tiene_secure} | {tiene_nfvdid}", 'info')
            
            exito, token, error = self.verificador.generar_token(cookie)
            total_procesados += 1
            
            if exito and token:
                enlace = self.verificador.formatear_enlace_nftoken(token)
                self.log(f"   ✅ TOKEN: {token}", 'success')
                resultados_validos.append({
                    'token': token,
                    'enlace': enlace,
                    'cookies': cookie
                })
            else:
                self.log(f"   ❌ Error: {error}", 'error')
            
            time.sleep(0.5)

        if resultados_validos:
            self.guardar_resultados(resultados_validos)
            self.log(f"💾 {len(resultados_validos)} token(s) guardados", 'success')
            self.finalizar_procesamiento(f"Completado: {len(resultados_validos)} tokens")
        else:
            self.log("❌ No se generaron tokens", 'error')
            self.finalizar_procesamiento("Sin tokens válidos")

    def guardar_resultados(self, resultados):
        modo = 'a' if os.path.exists(self.archivo_salida) else 'w'
        with open(self.archivo_salida, modo, encoding='utf-8') as f:
            if modo == 'w':
                f.write("=" * 60 + "\n")
                f.write("NETFLIX NFTOKEN GENERATOR\n")
                f.write(f"Author: 工V龱尺ㄚ㇌7\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

            f.write(f"\n--- Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Source: {self.archivo_entrada}\n\n")

            for r in resultados:
                f.write(f"🔗 TOKEN: {r['token']}\n")
                f.write(f"🔗 LINK: {r['enlace']}\n")
                f.write("COOKIES:\n")
                for k, v in r['cookies'].items():
                    f.write(f"  {k}: {v[:50]}...\n" if v else f"  {k}: [EMPTY]\n")
                f.write("-" * 40 + "\n")


def main():
    ventana = tk.Tk()
    app = InterfazNFToken(ventana)
    ventana.mainloop()

if __name__ == "__main__":
    main()