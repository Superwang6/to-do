import logging
import os

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel

            if not os.environ.get("HF_ENDPOINT"):
                os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

            model_size = os.environ.get("WHISPER_MODEL", "base")
            logger.info(f"[Speech] Loading whisper model: {model_size}, HF_ENDPOINT: {os.environ.get('HF_ENDPOINT')}")
            self._model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info("[Speech] Model loaded successfully")
        except ImportError:
            raise RuntimeError(
                "faster-whisper is not installed. Run: pip install faster-whisper"
            )

    def transcribe(self, audio_path: str) -> str:
        self._load_model()
        logger.info(f"[Speech] Transcribing: {audio_path}")
        segments, _ = self._model.transcribe(audio_path, language="zh")
        text = "".join(seg.text for seg in segments).strip()
        logger.info(f"[Speech] Transcription result: '{text}'")
        return text
