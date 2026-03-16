#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import importlib.util
import os

# --- Configuración ---
MODULES = [
    "aiohttp",
    "art",
    "beautifulsoup4",
    "cfscrape",
    "cloudscraper",
    "colorama",
    "fake-useragent",
    "flag",
    "imageio",
    "m3u8",
    "names",
    "playsound==1.2.2",  # Versión específica
    "progressbar",
    "pyshorteners",
    "PySocks",
    "qrcode",
    "requests",
    "selenium",
    "sock",
    "stem",
    "termcolor",
    "timeout-decorator",
    "tqdm",
    "unidecode",
    "urllib3",
    "user-agent",
    "wget"
]

# =========================
# FUNCIONES DE UTILIDAD (CORE MEJORADO)
# =========================

def check_pip():
    """Verifica si pip está instalado y lo actualiza."""
    print("🔄 Verificando pip...")
    try:
        # Actualizar pip (silenciosamente)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Pip está actualizado.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  No se pudo actualizar pip: {e.stderr}")
    except FileNotFoundError:
        print("❌ Pip no está instalado o no se encuentra en el PATH.")
        sys.exit(1)

def is_module_installed(module_name):
    """
    Verifica si un módulo de Python ya está instalado.
    Nota: Esto funciona para el nombre del paquete importable, no para el nombre de instalación con guiones.
    """
    # Limpiar el nombre para la importación (ej. "fake-useragent" -> "fake_useragent")
    import_name = module_name.split('==')[0].replace('-', '_')
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def install_package(pkg):
    """Intenta instalar un paquete y maneja los errores."""
    pkg_name_only = pkg.split('==')[0]  # Para mostrar solo el nombre
    print(f"📦 Procesando: {pkg_name_only}...")

    # 1. Verificar si ya está instalado
    if is_module_installed(pkg_name_only):
        print(f"   ⏭️  Ya está instalado. Omitiendo.")
        return True

    # 2. Intentar la instalación
    try:
        # Ejecutar pip y capturar la salida
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg],
            check=True,  # Lanza excepción si el código de retorno no es 0
            capture_output=True,
            text=True,
            timeout=120  # Timeout de 2 minutos por si acaso
        )
        print(f"   ✅ Instalado correctamente.")
        # (Opcional) Mostrar solo las últimas líneas de la instalación si quieres debuggear
        # print(result.stdout[-500:])
        return True

    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error instalando {pkg_name_only}.")
        print(f"      Razón: {e.stderr.strip()}")
        return False
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout: La instalación de {pkg_name_only} tomó demasiado tiempo.")
        return False
    except Exception as e:
        print(f"   💥 Error inesperado: {e}")
        return False

def install_all():
    """Instala todos los módulos de la lista, mostrando un resumen."""
    print("\n🔥 Instalando TODOS los módulos 🔥\n")
    
    # Primero, verificar/actualizar pip
    check_pip()
    
    results = {"success": [], "failed": []}
    
    for m in MODULES:
        success = install_package(m)
        pkg_name = m.split('==')[0]
        if success:
            results["success"].append(pkg_name)
        else:
            results["failed"].append(pkg_name)
    
    # Resumen final
    print("\n" + "="*40)
    print("📊 RESUMEN DE INSTALACIÓN")
    print("="*40)
    if results["success"]:
        print(f"✅ Instalados: {', '.join(results['success'])}")
    if results["failed"]:
        print(f"❌ Fallaron: {', '.join(results['failed'])}")
    print("="*40)

def install_one():
    """Instala un módulo específico solicitado por el usuario."""
    print("\n📦 Instalar módulo específico")
    name = input("👉 Nombre del módulo (ej: requests, colorama==0.4.6): ").strip()

    if not name:
        print("⚠️ Nombre vacío, cancelado.")
        return

    # Verificar pip antes
    check_pip()
    
    # Instalar el paquete
    if install_package(name):
        print(f"✅ {name} se instaló correctamente.")
    else:
        print(f"❌ La instalación de {name} falló.")

# =========================
# MENÚ PRINCIPAL
# =========================

def menu():
    """Muestra el menú principal."""
    # Limpiar pantalla (opcional, para dar sensación de frescura)
    # os.system('cls' if os.name == 'nt' else 'clear')
    
    print("""
╔════════════════════════════════╗
║  PYTHON MODULE INSTALLER v2.0  ║
╚════════════════════════════════╝

1) 📦 Instalar TODOS los módulos
2) 🔍 Instalar UN módulo específico
3) 🚪 Salir
""")

    choice = input("👉 Elige una opción: ").strip()

    if choice == "1":
        install_all()
    elif choice == "2":
        install_one()
    elif choice == "3":
        print("👋 ¡Hasta luego!")
        sys.exit(0)
    else:
        print("❌ Opción inválida. Por favor, elige 1, 2 o 3.")

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    try:
        while True:
            menu()
            input("\n⏎ Presiona ENTER para continuar...")
    except KeyboardInterrupt:
        print("\n\n👋 Interrupción recibida. Saliendo...")
        sys.exit(0)
