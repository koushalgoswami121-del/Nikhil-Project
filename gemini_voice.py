import asyncio
import io
import os
import wave
from pathlib import Path

_LAST_ERROR = ""


def _load_env():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _settings():
    _load_env()
    return {
        "api_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "tts_model": os.getenv("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts").strip(),
        "gemini_voice": os.getenv("GEMINI_VOICE", "Kore").strip(),
        "edge_voice": os.getenv("EDGE_TTS_VOICE", "en-US-JennyNeural").strip(),
    }


def last_error():
    return _LAST_ERROR


def _install_edge_tts():
    global _LAST_ERROR
    import subprocess
    import sys

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "edge-tts>=6.1", "-q"],
            timeout=180,
        )
        import edge_tts  # noqa: F401
        return True
    except Exception as exc:
        _LAST_ERROR = f"Could not install edge-tts: {exc}"
        return False


def neural_voice_available():
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        return _install_edge_tts()


def gemini_configured():
    return bool(_settings()["api_key"])


def _coach_script(question_text, role=None, is_first=True):
    if is_first:
        role_bit = f" for a {role} interview" if role else ""
        return (
            f"Hello! I'm your interview coach{role_bit}. "
            f"Here's your question: {question_text}"
        )
    return f"So your next question is: {question_text}"


def _pcm_to_wav(pcm_bytes, channels=1, rate=24000, sample_width=2):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def _try_gemini_tts(text):
    global _LAST_ERROR
    cfg = _settings()
    if not cfg["api_key"]:
        return None, None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=cfg["api_key"])
        response = client.models.generate_content(
            model=cfg["tts_model"],
            contents=f"Say in a warm, natural, professional tone: {text}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=cfg["gemini_voice"],
                        )
                    )
                ),
            ),
        )
        part = response.candidates[0].content.parts[0]
        pcm = part.inline_data.data
        if isinstance(pcm, str):
            import base64
            pcm = base64.b64decode(pcm)
        return _pcm_to_wav(pcm), "audio/wav"
    except Exception as exc:
        _LAST_ERROR = f"Gemini TTS: {exc}"
        return None, None


def _edge_tts_mp3(text):
    global _LAST_ERROR
    import edge_tts

    cfg = _settings()
    out = io.BytesIO()

    async def _run():
        comm = edge_tts.Communicate(text, voice=cfg["edge_voice"])
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                out.write(chunk["data"])

    asyncio.run(_run())
    if out.tell() == 0:
        _LAST_ERROR = "Edge TTS produced no audio"
        return None, None
    return out.getvalue(), "audio/mpeg"


def coach_speech(question_text, role=None, is_first=True):
    """Return (audio_bytes, mime_type) or (None, None)."""
    global _LAST_ERROR
    _LAST_ERROR = ""
    text = _coach_script(question_text, role, is_first=is_first)

    data, mime = _try_gemini_tts(text)
    if data:
        return data, mime

    if neural_voice_available():
        data, mime = _edge_tts_mp3(text)
        if data:
            return data, mime

    if not _LAST_ERROR:
        _LAST_ERROR = "No neural voice backend available"
    return None, None


def coach_speech_wav(question_text, role=None):
    """Backward-compatible: returns WAV/MP3 bytes or None."""
    data, _mime = coach_speech(question_text, role)
    return data
