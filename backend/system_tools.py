import os
import psutil
import datetime
import subprocess
import webbrowser
import requests

def get_system_telemetry():
    """Retorna métricas de saúde do sistema (CPU, Memória, Bateria, Disco)."""
    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    battery = psutil.sensors_battery()
    
    battery_info = {
        "percent": battery.percent if battery else 100,
        "power_plugged": battery.power_plugged if battery else True
    }
    
    return {
        "cpu_usage": f"{cpu_percent}%",
        "cpu_cores": psutil.cpu_count(logical=True),
        "cpu_freq_mhz": f"{cpu_freq.current:.1f} MHz" if cpu_freq else "N/A",
        "ram_usage": f"{mem.percent}%",
        "ram_used_gb": f"{mem.used / (1024**3):.1f} GB",
        "ram_total_gb": f"{mem.total / (1024**3):.1f} GB",
        "disk_usage": f"{disk.percent}%",
        "disk_free_gb": f"{disk.free / (1024**3):.1f} GB",
        "battery": battery_info,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def open_application(app_name: str):
    """Abre aplicativos comuns do sistema operacional Windows."""
    name = app_name.lower().strip()
    try:
        if "navegador" in name or "chrome" in name or "google" in name or "browser" in name:
            webbrowser.open("https://www.google.com")
            return "Navegador aberto com sucesso, Senhor."
        elif "calculadora" in name or "calc" in name:
            subprocess.Popen("calc.exe")
            return "Calculadora inicializada."
        elif "bloco de notas" in name or "notepad" in name:
            subprocess.Popen("notepad.exe")
            return "Bloco de Notas aberto."
        elif "vscode" in name or "code" in name:
            subprocess.Popen("code", shell=True)
            return "Visual Studio Code acionado."
        elif "terminal" in name or "cmd" in name or "powershell" in name:
            subprocess.Popen("wt.exe" if os.system("where wt >nul 2>nul") == 0 else "powershell.exe")
            return "Terminal do sistema aberto."
        elif "youtube" in name:
            webbrowser.open("https://www.youtube.com")
            return "Acessando YouTube."
        elif "spotify" in name:
            os.system("start spotify:")
            return "Iniciando Spotify."
        else:
            # Tenta executar pelo nome
            os.system(f"start {name}")
            return f"Comando de inicialização para '{name}' enviado."
    except Exception as e:
        return f"Falha ao abrir {app_name}: {str(e)}"

def get_weather_info(city: str = "Sao Paulo"):
    """Consulta informações meteorológicas em tempo real."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            temp = current['temp_C']
            feels = current['FeelsLikeC']
            desc = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            return f"Condições atuais em {city}: {temp}°C (sensação de {feels}°C), {desc}, com umidade em {humidity}%."
    except Exception:
        pass
    return f"Não foi possível obter dados meteorológicos precisos de {city} no momento."

def search_web_google(query: str):
    """Abre pesquisa no Google."""
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    webbrowser.open(url)
    return f"Pesquisa por '{query}' realizada no navegador."
