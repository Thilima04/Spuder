import os
import json
import base64
import requests
from config import GEMINI_API_KEY, SYSTEM_PROMPT
from vision import vision_system
from screen_vision import screen_vision
from memory_manager import memory_manager
import system_tools

class GeminiBrain:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.supported_models = []
        self.active_model = None
        self._init_model()

    def _init_model(self):
        key = self.api_key.strip() if self.api_key else ""
        if not key:
            print("[Brain] Chave API não configurada. Aguardando chave...")
            return

        self._discover_available_models(key)

    def _discover_available_models(self, key: str):
        """Descobre dinamicamente os modelos exatos disponíveis para esta chave de API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                data = res.json()
                models = data.get("models", [])
                
                self.supported_models = [
                    m["name"].replace("models/", "") 
                    for m in models 
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                ]
                
                preferred_order = [
                    "gemini-3.7-flash",
                    "gemini-3.6-flash",
                    "gemini-3.5-flash",
                    "gemini-flash-latest",
                    "gemini-3-flash-preview",
                    "gemini-3.1-flash-lite",
                    "gemini-2.5-flash-lite",
                    "gemini-flash-lite-latest",
                    "gemini-2.0-flash",
                    "gemini-1.5-flash"
                ]
                
                for pref in preferred_order:
                    if pref in self.supported_models:
                        self.active_model = pref
                        break
                
                if not self.active_model and self.supported_models:
                    flashes = [m for m in self.supported_models if "flash" in m and "tts" not in m and "image" not in m]
                    self.active_model = flashes[0] if flashes else self.supported_models[0]
                
                print(f"[Brain] Modelos suportados: {self.supported_models[:8]}")
                print(f"[Brain] Modelo ativo selecionado para o SPUDER: {self.active_model}")
            else:
                self.active_model = "gemini-3.7-flash"
        except Exception as e:
            print(f"[Brain] Erro na descoberta de modelos: {e}")
            self.active_model = "gemini-3.7-flash"

    def set_api_key(self, key: str):
        self.api_key = key.strip()
        self._init_model()

    def check_system_intent(self, user_text: str):
        """Verifica comandos de sistema locais e memorização antes do envio."""
        lower = user_text.lower()
        
        # Memorização de fatos solicitados pelo usuário
        learned = memory_manager.extract_and_learn(user_text)
        if learned:
            return learned
            
        # Pergunta sobre memórias guardadas
        if any(w in lower for w in ["o que você lembra sobre mim", "quais minhas informações", "o que você sabe sobre mim", "minhas memórias"]):
            summary = memory_manager.get_context_summary()
            return f"Registros de Memória Permanente, Senhor Thiago:\n{summary}"
        
        # Telemetria de hardware
        if any(w in lower for w in ["status do sistema", "diagnóstico", "cpu", "memória", "temperatura", "bateria"]):
            telemetry = system_tools.get_system_telemetry()
            return f"Relatório de Sistemas: Uso de CPU em {telemetry['cpu_usage']}, Memória RAM utilizada em {telemetry['ram_usage']} ({telemetry['ram_used_gb']} de {telemetry['ram_total_gb']}). Bateria em {telemetry['battery']['percent']}%. Todos os subsistemas operando em parâmetros normais, Senhor Thiago."
            
        # Abertura de programas
        if lower.startswith("abrir ") or lower.startswith("abra ") or "iniciar " in lower:
            target = lower.replace("abrir ", "").replace("abra ", "").replace("iniciar ", "").replace("o ", "").replace("a ", "").strip()
            res = system_tools.open_application(target)
            return res

        # Clima
        if "clima" in lower or "temperatura hoje" in lower or "previsão do tempo" in lower:
            city = "Sao Paulo"
            words = user_text.split()
            if "em" in words:
                idx = words.index("em")
                if idx + 1 < len(words):
                    city = words[idx + 1].strip("?.! ")
            return system_tools.get_weather_info(city)

        return None

    def should_use_screen_vision(self, user_text: str) -> bool:
        """Determina se o usuário quer que o SPUDER olhe para o monitor/tela."""
        triggers = [
            "olhe para minha tela", "olhe minha tela", "veja minha tela", 
            "o que está na minha tela", "analise minha tela", "leia minha tela",
            "veja este código", "analise este código", "corrija este código",
            "o que tem no meu monitor", "olhe meu monitor", "print da tela"
        ]
        lower = user_text.lower()
        return any(tr in lower for tr in triggers)

    def should_use_camera_vision(self, user_text: str) -> bool:
        """Determina se a pergunta requer a câmera/visão computacional de ambiente."""
        triggers = [
            "o que você vê", "o que está vendo", "o que tem na minha mão", 
            "quem está", "olhe para", "veja isto", "olhe isto",
            "o que é isso", "minha frente", "descreva o ambiente", 
            "visão", "câmera", "quantos dedos", "expressão", "rosto"
        ]
        lower = user_text.lower()
        return any(trigger in lower for trigger in triggers)

    async def process_user_input(self, user_text: str, force_vision: bool = False, force_screen: bool = False, client_image_base64: str = "") -> str:
        """Processa entrada multimodal do usuário (Texto + Memória + Câmera Local/Celular ou Tela)."""
        user_text = user_text.strip()
        if not user_text:
            return "Estou à disposição, Senhor Thiago. O que deseja?"

        # Verifica ferramentas locais e gravação de memória primeiro
        if not force_vision and not force_screen and not client_image_base64 and not self.should_use_camera_vision(user_text) and not self.should_use_screen_vision(user_text):
            local_response = self.check_system_intent(user_text)
            if local_response:
                return local_response

        # Se não houver chave do Gemini configurada
        if not self.api_key:
            return "Sistemas neurais online, Senhor. Por favor insira sua GEMINI_API_KEY no ícone de engrenagem ⚙️ ou no arquivo .env."

        # Se a lista de modelos ainda não foi descoberta
        if not self.supported_models:
            self._discover_available_models(self.api_key)

        use_screen = force_screen or self.should_use_screen_vision(user_text)
        use_camera = bool(client_image_base64) or ((not use_screen) and (force_vision or self.should_use_camera_vision(user_text)))

        try:
            parts = []
            
            # 1. Anexa Tela do Computador se solicitado
            if use_screen:
                screen_bytes = screen_vision.capture_screen_bytes()
                if screen_bytes:
                    b64_screen = base64.b64encode(screen_bytes).decode("utf-8")
                    parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64_screen
                        }
                    })
                else:
                    return "Senhor Thiago, não foi possível capturar a imagem do monitor no momento."

            # 2. Anexa Câmera (Do celular ou da Webcam)
            elif use_camera:
                if client_image_base64:
                    # Imagem enviada diretamente do navegador do celular!
                    clean_b64 = client_image_base64.split(",")[-1]
                    parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": clean_b64
                        }
                    })
                else:
                    img_bytes = vision_system.get_raw_frame_bytes()
                    if img_bytes:
                        b64_img = base64.b64encode(img_bytes).decode("utf-8")
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_img
                            }
                        })
                    else:
                        return "Senhor Thiago, aponte a câmera do celular ou ative os sensores ópticos."

            # Contexto de Memória Permanente
            memory_context = memory_manager.get_context_summary()
            full_prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"--- REGISTROS DE MEMÓRIA PERMANENTE ---\n{memory_context}\n\n"
                f"--- COMANDO DO SENHOR THIAGO ---\n{user_text}"
            )
            parts.append({"text": full_prompt})

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 900
                }
            }

            preferred_order = [
                "gemini-3.7-flash",
                "gemini-3.6-flash",
                "gemini-3.5-flash",
                "gemini-flash-latest",
                "gemini-3-flash-preview",
                "gemini-3.1-flash-lite",
                "gemini-2.5-flash-lite",
                "gemini-flash-lite-latest"
            ]
            
            candidates = []
            if self.active_model and self.active_model not in candidates:
                candidates.append(self.active_model)
                
            for pref in preferred_order:
                if pref in self.supported_models and pref not in candidates:
                    candidates.append(pref)
                    
            for m in self.supported_models:
                if "flash" in m.lower() and "tts" not in m.lower() and "image" not in m.lower() and m not in candidates:
                    candidates.append(m)

            last_error_msg = ""
            for model_candidate in candidates:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                
                try:
                    res = requests.post(url, json=payload, headers=headers, timeout=25)
                except Exception as req_err:
                    print(f"[Brain] Timeout no modelo '{model_candidate}': {req_err}")
                    continue
                
                if res.status_code == 200:
                    self.active_model = model_candidate
                    result_json = res.json()
                    candidates_resp = result_json.get("candidates", [])
                    if candidates_resp:
                        content = candidates_resp[0].get("content", {})
                        response_parts = content.get("parts", [])
                        if response_parts:
                            return response_parts[0].get("text", "").strip()
                    return "Comando executado com precisão, Senhor Thiago."
                
                err_data = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
                last_error_msg = err_data.get("error", {}).get("message", res.text)
                continue

            if "API_KEY_INVALID" in last_error_msg:
                return "Senhor Thiago, a chave da API do Gemini é inválida. Atualize no ícone de engrenagem ⚙️."
            elif "429" in str(last_error_msg) or "quota" in last_error_msg.lower():
                return "Senhor Thiago, a cota gratuita temporária da API foi atingida. Aguarde alguns segundos."
            
            return f"Perdoe-me, Senhor Thiago. Resposta da rede neural: {last_error_msg[:90]}"

        except Exception as e:
            print(f"[Brain] Exceção na chamada: {e}")
            return f"Perdoe-me, Senhor Thiago. Falha na transmissão: {str(e)[:80]}"

brain = GeminiBrain()
