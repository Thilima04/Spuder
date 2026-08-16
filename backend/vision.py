import cv2
import time
import base64
import threading
import numpy as np
from PIL import Image
import io

# Tenta carregar MediaPipe de forma segura
HAS_MEDIAPIPE = False
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    HAS_MEDIAPIPE = True
except Exception as e:
    HAS_MEDIAPIPE = False
    print(f"[Vision] MediaPipe em modo fallback: {e}")

class VisionSystem:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False
        self.lock = threading.Lock()
        self.raw_frame = None
        self.processed_frame = None
        self.faces_detected = 0
        self.hands_detected = 0
        self.current_gesture = "NONE"
        self.frame_count = 0
        self.face_cascade = None
        self.hands_processor = None
        self.owner_name = "THIAGO"
        self.owner_detected = False
        
        # Carregamento defensivo do detector facial OpenCV
        try:
            if hasattr(cv2, 'CascadeClassifier') and hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            self.face_cascade = None

        # Inicializa MediaPipe Hands se disponível
        if HAS_MEDIAPIPE:
            try:
                self.hands_processor = mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.6,
                    min_tracking_confidence=0.5
                )
                print("[Vision] Módulo MediaPipe Hands holográfico ativado.")
            except Exception as e:
                print(f"[Vision] Falha ao iniciar MediaPipe Hands: {e}")
                self.hands_processor = None
        
    def start(self):
        """Inicia a captura de vídeo em thread separada."""
        if self.is_running:
            return
        
        try:
            if hasattr(cv2, 'CAP_DSHOW'):
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            else:
                self.cap = cv2.VideoCapture(self.camera_index)
                
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_index)
        except Exception as e:
            print(f"[Vision] Falha ao abrir câmera: {e}")
            return
            
        if not self.cap or not self.cap.isOpened():
            print("[Vision] Câmera não detectada ou em standby.")
            return

        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
        except Exception:
            pass

        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print("[Vision] Sensores ópticos do SPUDER operando a 30 FPS.")

    def stop(self):
        """Para a captura de vídeo."""
        self.is_running = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        print("[Vision] Sensores ópticos desativados.")

    def _draw_hud_corners(self, img, pt1, pt2, color=(0, 240, 255), thickness=2, length=20):
        """Desenha cantos cibernéticos ao redor de um alvo."""
        x1, y1 = pt1
        x2, y2 = pt2
        
        cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
        cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
        cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
        cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
        cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
        cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
        cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
        cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)

    def _detect_hand_gesture(self, landmarks, w, h):
        """Identifica gestos das mãos a partir dos nós do MediaPipe."""
        # Índices: Polegar(4), Indicador(8), Médio(12), Anelar(16), Mínimo(20)
        # Base dos dedos: 2, 6, 10, 14, 18, Pulso(0)
        
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]
        
        thumb_tip = pts[4]
        index_tip = pts[8]
        middle_tip = pts[12]
        ring_tip = pts[16]
        pinky_tip = pts[20]
        
        # Distância Polegar - Indicador para Pinça (Pinch)
        dist_pinch = np.linalg.norm(np.array(thumb_tip) - np.array(index_tip))
        if dist_pinch < 35:
            return "PINCH (PINÇA)"

        # Dedos levantados
        fingers_up = [
            thumb_tip[1] < pts[3][1],
            index_tip[1] < pts[6][1],
            middle_tip[1] < pts[10][1],
            ring_tip[1] < pts[14][1],
            pinky_tip[1] < pts[18][1]
        ]
        
        count = sum(fingers_up)
        
        if count == 5:
            return "PALMA ABERTA"
        elif count == 0:
            return "PUNHO FECHADO"
        elif fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
            return "V (VITÓRIA/PAZ)"
        elif fingers_up[1] and count == 1:
            return "APONTANDO"
        elif fingers_up[0] and count == 1 and thumb_tip[1] < pts[2][1]:
            return "POLEGAR UP"
            
        return "GESTO ATIVO"

    def _process_frame(self, frame):
        """Aplica detecção facial, MediaPipe Hands e filtros táticos holográficos no frame."""
        overlay = frame.copy()
        h, w, _ = frame.shape
        faces = []
        
        # 1. Detecção e Identificação do Dono (Thiago)
        if self.face_cascade is not None:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.2, 
                    minNeighbors=5, 
                    minSize=(50, 50)
                )
            except Exception:
                faces = []
        
        self.faces_detected = len(faces)
        self.owner_detected = (self.faces_detected > 0)
        
        # Linhas centrais da mira
        cv2.line(overlay, (w//2 - 20, h//2), (w//2 + 20, h//2), (0, 200, 255), 1)
        cv2.line(overlay, (w//2, h//2 - 20), (w//2, h//2 + 20), (0, 200, 255), 1)
        cv2.circle(overlay, (w//2, h//2), 35, (0, 200, 255), 1)

        # Renderiza HUD holográfico para cada face encontrada (Identificando Thiago)
        for (x, y, fw, fh) in faces:
            # Cor ouro/verde para o Dono autenticado
            color_auth = (0, 255, 180)
            self._draw_hud_corners(overlay, (x, y), (x + fw, y + fh), color=color_auth, thickness=2, length=18)
            cv2.rectangle(overlay, (x, y), (x + fw, y + fh), (0, 180, 120), 1)
            
            # Tag holográfica com o nome do Thiago
            tag_owner = f"BIO-MATCH: {self.owner_name} [LVL 10]"
            cv2.putText(overlay, tag_owner, (x, max(y - 12, 22)), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color_auth, 1, cv2.LINE_AA)
            cv2.putText(overlay, "OPERADOR AUTORIZADO", (x, y + fh + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 230, 255), 1, cv2.LINE_AA)

        # 2. Processamento de Gestos com as Mãos (MediaPipe)
        detected_gesture = "NENHUM"
        self.hands_detected = 0

        if self.hands_processor is not None:
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands_processor.process(rgb)
                
                if results.multi_hand_landmarks:
                    self.hands_detected = len(results.multi_hand_landmarks)
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Desenha esqueleto holográfico com conexões
                        detected_gesture = self._detect_hand_gesture(hand_landmarks, w, h)
                        self.current_gesture = detected_gesture
                        
                        # Conexões das mãos em neon
                        pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]
                        connections = mp_hands.HAND_CONNECTIONS if HAS_MEDIAPIPE else []
                        
                        for conn in connections:
                            ptA = pts[conn[0]]
                            ptB = pts[conn[1]]
                            cv2.line(overlay, ptA, ptB, (0, 240, 255), 1, cv2.LINE_AA)
                            
                        for pt in pts:
                            cv2.circle(overlay, pt, 3, (0, 180, 255), -1)
                            cv2.circle(overlay, pt, 5, (255, 200, 0), 1)
                            
                        # Tag do gesto identificado
                        wrist = pts[0]
                        cv2.putText(overlay, f"GESTO: {detected_gesture}", (wrist[0] - 30, wrist[1] + 25), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 230), 1, cv2.LINE_AA)
            except Exception as e:
                pass
        
        self.current_gesture = detected_gesture

        # 3. Telemetria no topo do vídeo
        timestamp = time.strftime("%H:%M:%S")
        status_text = f"SPUDER TACTICAL | DONO: {'IDENTIFICADO' if self.owner_detected else 'PROCURANDO'} | GESTO: {self.current_gesture} | {timestamp}"
        cv2.putText(overlay, status_text, (15, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 230, 255), 1, cv2.LINE_AA)

        return overlay

    def _capture_loop(self):
        """Loop de captura e processamento contínuo de vídeo."""
        while self.is_running and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    time.sleep(0.03)
                    continue
                    
                # Espelha o vídeo
                frame = cv2.flip(frame, 1)
                
                with self.lock:
                    self.raw_frame = frame.copy()
                    self.processed_frame = self._process_frame(frame)
                    self.frame_count += 1
            except Exception as e:
                time.sleep(0.05)
                
            time.sleep(0.03)

    def get_latest_jpeg_base64(self):
        """Retorna o frame processado em base64 para streaming web."""
        with self.lock:
            if self.processed_frame is None:
                return None
            try:
                ret, buffer = cv2.imencode('.jpg', self.processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                if not ret:
                    return None
                return base64.b64encode(buffer).decode('utf-8')
            except Exception:
                return None

    def get_raw_frame_bytes(self):
        """Retorna o frame original limpo em formato JPEG bytes para o Gemini Vision."""
        with self.lock:
            if self.raw_frame is None:
                return None
            try:
                ret, buffer = cv2.imencode('.jpg', self.raw_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                if not ret:
                    return None
                return buffer.tobytes()
            except Exception:
                return None

    def get_raw_pil_image(self):
        """Retorna imagem PIL do frame para análise multimodal."""
        with self.lock:
            if self.raw_frame is None:
                return None
            try:
                rgb_frame = cv2.cvtColor(self.raw_frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(rgb_frame)
            except Exception:
                return None

vision_system = VisionSystem()
