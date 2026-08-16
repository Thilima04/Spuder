import io
import asyncio
import base64
import edge_tts
from config import SPUDER_VOICE

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

class VoiceEngine:
    def __init__(self, voice_name=SPUDER_VOICE):
        self.voice_name = voice_name
        self.recognizer = sr.Recognizer() if HAS_SR else None
        
    async def synthesize_to_bytes(self, text: str) -> bytes:
        """Sintetiza texto em áudio MP3 utilizando edge-tts com voz neural."""
        communicate = edge_tts.Communicate(text, self.voice_name, rate="+5%", pitch="+0Hz")
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        return audio_stream.getvalue()

    async def synthesize_to_base64(self, text: str) -> str:
        """Gera áudio em base64 para reprodução direta no HUD web."""
        try:
            audio_bytes = await self.synthesize_to_bytes(text)
            return base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            print(f"[Voice] Erro ao sintetizar áudio: {e}")
            return ""

    def transcribe_audio_bytes(self, audio_bytes: bytes) -> str:
        """Transcreve arquivo de áudio WAV recebido usando SpeechRecognition."""
        if not HAS_SR or not self.recognizer:
            return ""
        try:
            audio_file = io.BytesIO(audio_bytes)
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language="pt-BR")
                return text
        except Exception as e:
            print(f"[Voice] Falha na transcrição: {e}")
            return ""

voice_engine = VoiceEngine()
