import os
import sys
import time
import socket
import webbrowser
import threading
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_path))

def get_local_ip():
    """Descobre o IP local do computador na rede Wi-Fi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def open_browser():
    """Abre o HUD do SPUDER no navegador padrão."""
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print(f"\n=======================================================")
    print(f" [S.P.U.D.E.R.] Acessando interface no PC em: {url}")
    print(f"=======================================================\n")
    webbrowser.open(url)

if __name__ == "__main__":
    import uvicorn
    from config import PORT
    
    local_ip = get_local_ip()
    
    print("=======================================================")
    print("       INICIALIZANDO PROTOCOLO S.P.U.D.E.R. 2.0        ")
    print("              CYBERNETIC SPIDER CORE OS                ")
    print("=======================================================")
    print(f" [PC Local]     : http://127.0.0.1:{PORT}")
    print(f" [Celular Wi-Fi]: http://{local_ip}:{PORT}")
    print("=======================================================")
    
    # Inicia abertura do navegador no PC
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Inicia servidor FastAPI
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False, app_dir=str(backend_path))
