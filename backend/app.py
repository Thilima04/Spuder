import os
import json
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import PORT, HOST, GEMINI_API_KEY
from vision import vision_system
from voice import voice_engine
from gemini_brain import brain
from memory_manager import memory_manager
from screen_vision import screen_vision
import system_tools

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia a captura de visão computacional
    vision_system.start()
    yield
    # Finaliza a câmera
    vision_system.stop()

app = FastAPI(title="SPUDER 2.0 AI System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

class ChatRequest(BaseModel):
    message: str
    force_vision: bool = False
    force_screen: bool = False
    image_base64: str = ""

class KeyRequest(BaseModel):
    api_key: str

class ActiveConnections:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in list(self.connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)

manager = ActiveConnections()

@app.post("/api/chat")
async def handle_chat(req: ChatRequest):
    """Processa uma mensagem do usuário com suporte a visão da câmera ou tela."""
    if req.force_screen or brain.should_use_screen_vision(req.message):
        status = "ANALYZING_SCREEN"
    elif req.force_vision or bool(req.image_base64) or brain.should_use_camera_vision(req.message):
        status = "ANALYZING_VISION"
    else:
        status = "THINKING"
        
    await manager.broadcast({"type": "status", "status": status})

    # Processa raciocínio, tela ou câmera local/celular
    response_text = await brain.process_user_input(
        req.message, 
        force_vision=req.force_vision,
        force_screen=req.force_screen,
        client_image_base64=req.image_base64
    )
    
    # Notifica que está falando e gera áudio
    await manager.broadcast({"type": "status", "status": "SPEAKING", "text": response_text})
    audio_base64 = await voice_engine.synthesize_to_base64(response_text)

    return {
        "user_message": req.message,
        "response_text": response_text,
        "audio_base64": audio_base64,
        "faces_detected": vision_system.faces_detected,
        "gesture": vision_system.current_gesture,
        "owner_detected": vision_system.owner_detected
    }

@app.get("/api/telemetry")
async def get_telemetry():
    """Retorna dados de telemetria de hardware e sensores."""
    data = system_tools.get_system_telemetry()
    data["faces_detected"] = vision_system.faces_detected
    data["gesture"] = vision_system.current_gesture
    data["owner_detected"] = vision_system.owner_detected
    data["vision_online"] = vision_system.is_running
    data["gemini_active"] = bool(brain.api_key)
    return data

@app.get("/api/memory")
async def get_memory():
    """Retorna a memória permanente gravada."""
    return memory_manager.data

@app.post("/api/config/key")
async def update_api_key(req: KeyRequest):
    """Atualiza a chave de API Gemini em tempo de execução e persiste no .env."""
    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="Chave inválida.")
    brain.set_api_key(key)
    
    try:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_content = f"GEMINI_API_KEY={key}\nSPUDER_VOICE=pt-BR-AntonioNeural\nPORT=8000\nHOST=127.0.0.1\n"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
    except Exception as e:
        print(f"[Config] Erro ao salvar .env: {e}")
        
    return {"status": "success", "message": "Chave API do SPUDER gravada e sincronizada com sucesso, Senhor Thiago."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Canal WebSocket bidirecional para telemetria em tempo real, vídeo e gestos."""
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "log",
            "message": "Núcleo Aranha Cibernética SPUDER 2.0 ativado. Dono: THIAGO."
        })
        
        while True:
            frame_b64 = vision_system.get_latest_jpeg_base64()
            if frame_b64:
                await websocket.send_json({
                    "type": "video_frame",
                    "frame": frame_b64,
                    "faces": vision_system.faces_detected,
                    "gesture": vision_system.current_gesture,
                    "owner_detected": vision_system.owner_detected
                })
            
            telemetry = system_tools.get_system_telemetry()
            telemetry["gesture"] = vision_system.current_gesture
            telemetry["owner_detected"] = vision_system.owner_detected
            
            await websocket.send_json({
                "type": "telemetry",
                "data": telemetry
            })

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

# Servir Frontend
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def serve_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({"status": "SPUDER Backend Running", "message": "Frontend não encontrado"})
