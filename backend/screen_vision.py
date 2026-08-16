import io
import base64
from PIL import Image, ImageGrab

class ScreenVision:
    def __init__(self):
        pass

    def capture_screen_image(self) -> Image.Image:
        """Captura o monitor principal e retorna como PIL Image."""
        try:
            screenshot = ImageGrab.grab()
            # Redimensiona para resolução ideal de análise visual rápida sem perder qualidade de texto
            max_size = (1600, 900)
            screenshot.thumbnail(max_size, Image.Resampling.LANCZOS)
            return screenshot
        except Exception as e:
            print(f"[ScreenVision] Erro ao capturar tela: {e}")
            return None

    def capture_screen_bytes(self) -> bytes:
        """Captura a tela e retorna em bytes JPEG."""
        img = self.capture_screen_image()
        if img is None:
            return None
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return buffer.getvalue()

    def capture_screen_base64(self) -> str:
        """Captura a tela e retorna string base64."""
        b = self.capture_screen_bytes()
        if not b:
            return ""
        return base64.b64encode(b).decode("utf-8")

screen_vision = ScreenVision()
