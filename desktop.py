import os
import sys
import threading
import time
import requests
import webview

from django.core.management import execute_from_command_line, call_command
from django.core.management.commands.runserver import Command
from waitress import serve
from scale_system.wsgi import application
import logging


DJANGO_URL = "http://127.0.0.1:8000"

def start_django():
    # 1. Garante que o diretório de log existe antes de iniciar o logging
    log_dir = os.path.join(os.environ["LOCALAPPDATA"], "SCALE")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "error_log.txt")
    
    # 2. Configura o logging
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        if getattr(sys, 'frozen', False):
            # Pasta onde o executável ESTÁ (C:\Users\...\Programs\SCALE System)
            exe_dir = os.path.dirname(sys.executable)
            # Pasta temporária onde estão os arquivos do Django
            base_dir = sys._MEIPASS
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = exe_dir

        # FORÇA o Windows a trabalhar dentro da pasta do executável
        os.chdir(exe_dir) 
    
        # O resto do seu código...
        sys.path.insert(0, base_dir)

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scale_system.settings")

        import django
        django.setup()

        logging.info("Iniciando migrações...")
        call_command("migrate", interactive=False)
        logging.info("Migrações concluídas.")

        logging.info("Iniciando servidor Waitress na porta 8000...")
        serve(application, host="127.0.0.1", port=8000)

    except Exception as e:
        logging.exception("Erro crítico ao iniciar o Django:")



# Inicia Django em thread separada
django_thread = threading.Thread(target=start_django, daemon=True)
django_thread.start()

server_started = False
for _ in range(30):
    try:
        # Importante: usar timeout curto para a verificação
        requests.get(DJANGO_URL, timeout=1)
        server_started = True
        break
    except:
        time.sleep(1)


if not server_started:
    # Em produção, você pode querer logar isso em um arquivo
    sys.exit("Erro: O servidor Django não iniciou a tempo.")


# Verifica admin ou vai para login
try:
    response = requests.get(f"{DJANGO_URL}/check-admin/", timeout=2)
    url = response.text.strip() if response.status_code == 200 else f"{DJANGO_URL}/login/"
except:
    url = f"{DJANGO_URL}/login/"


# Abre janela desktop
webview.create_window(
    title="SCALE System",
    url=url,
    width=1400,
    height=900,
    min_size=(1000, 700)
)

webview.start()