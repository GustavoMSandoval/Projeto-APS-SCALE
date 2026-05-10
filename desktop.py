import threading
import subprocess
import time
import requests
import webview
import os
import sys


DJANGO_URL = "http://127.0.0.1:8000"


def resource_path(relative_path):
    """
    Resolve caminhos no PyInstaller
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def start_django():
    """
    Inicia o servidor Django
    """
    manage_path = resource_path("manage.py")

    subprocess.Popen(
        [sys.executable, manage_path, "runserver"],
        cwd=resource_path("."),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# inicia Django em thread separada
django_thread = threading.Thread(
    target=start_django,
    daemon=True
)

django_thread.start()


# espera servidor iniciar
server_started = False

for _ in range(20):
    try:
        requests.get(DJANGO_URL)
        server_started = True
        break

    except:
        time.sleep(1)


if not server_started:
    raise Exception(
        "Não foi possível iniciar o servidor Django."
    )


# verifica se já existe admin
try:
    response = requests.get(
        f"{DJANGO_URL}/check-admin/"
    )

    url = response.text.strip()

except:
    url = f"{DJANGO_URL}/login/"


# cria janela desktop
webview.create_window(
    title="SCALE System",
    url=url,
    width=1400,
    height=900,
    min_size=(1000, 700)
)

webview.start()