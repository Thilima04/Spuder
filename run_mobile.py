import os
import sys
import time
import socket
import subprocess
import threading
import urllib.request
import re
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

def start_cloudflare_tunnel(port=8000):
    """Inicia túnel Cloudflare gratuito sem necessidade de login."""
    cloudflared_path = Path(__file__).resolve().parent / "cloudflared.exe"
    
    # Baixa o cloudflared.exe se ainda não existir
    if not cloudflared_path.exists():
        print("\n[Mobile Link] Configurando túnel seguro HTTPS para celular...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        try:
            urllib.request.urlretrieve(url, str(cloudflared_path))
            print("[Mobile Link] Túnel seguro pronto!")
        except Exception as e:
            print(f"[Mobile Link] Aviso ao baixar túnel: {e}")
            return None

    try:
        cmd = [str(cloudflared_path), "tunnel", "--url", f"http://127.0.0.1:{port}"]
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        
        # Lê a URL gerada pela Cloudflare
        for line in process.stderr:
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                tunnel_url = match.group(0)
                print(f"\n=======================================================")
                print(f" 📱 LINK DE ACESSO REMOTO PARA O CELULAR (4G / 5G / Wi-Fi):")
                print(f" 👉 {tunnel_url}")
                print(f"=======================================================\n")
                return tunnel_url
    except Exception as e:
        print(f"[Mobile Link] Falha no túnel: {e}")
    return None

if __name__ == "__main__":
    import uvicorn
    from config import PORT
    
    local_ip = get_local_ip()
    
    print("=======================================================")
    print("   🕷️ S.P.U.D.E.R. 2.0 // MOBILE & REMOTE SYSTEMS OS   ")
    print("=======================================================")
    print(f" [PC Local]  : http://localhost:{PORT}")
    print(f" [Wi-Fi Cel] : http://{local_ip}:{PORT}")
    print("=======================================================")

    # Inicia o túnel HTTPS em segundo plano
    threading.Thread(target=start_cloudflare_tunnel, args=(PORT,), daemon=True).start()

    # Inicia servidor FastAPI escutando em 0.0.0.0
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False, app_dir=str(backend_path))
