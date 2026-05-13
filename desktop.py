import os
import sys
import threading
import time
import requests
import webview

from django.core.management import execute_from_command_line


DJANGO_URL = "http://127.0.0.1:8000"


def resource_path(relative_path):
    """
    Resolve caminhos do PyInstaller
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def start_django():
    """
    Inicia Django internamente
    """

    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

    os.chdir(base_dir)

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "scale_system.settings"
    )

    # cria banco/tabelas automaticamente
    execute_from_command_line([
        "manage.py",
        "migrate"
    ])

    # inicia servidor
    execute_from_command_line([
        "manage.py",
        "runserver",
        "127.0.0.1:8000",
        "--noreload"
    ])


# inicia Django em thread separada
django_thread = threading.Thread(
    target=start_django,
    daemon=True
)

django_thread.start()


# espera servidor subir
server_started = False

for _ in range(30):
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


# verifica admin
try:
    response = requests.get(
        f"{DJANGO_URL}/check-admin/"
    )

    url = response.text.strip()

except:
    url = f"{DJANGO_URL}/login/"


# abre janela desktop
webview.create_window(
    title="SCALE System",
    url=url,
    width=1400,
    height=900,
    min_size=(1000, 700)
)

webview.start()