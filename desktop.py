import threading
import subprocess
import time
import requests
import webview


DJANGO_URL = "http://127.0.0.1:8000"


def start_django():
    """
    Inicia o servidor Django
    """
    subprocess.run(
        ["python", "manage.py", "runserver"],
        shell=True
    )


# inicia Django em thread separada
django_thread = threading.Thread(
    target=start_django,
    daemon=True
)

django_thread.start()


# espera servidor iniciar
server_started = False

for _ in range(15):
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