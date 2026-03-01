import numpy as np
import httpx

from config import DEEPGRAM_API_KEY


DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"


def resample_audio(pcm_bytes, original_rate=48000, target_rate=16000):
    """
    Downsample 48kHz PCM int16 audio to 16kHz for Deepgram STT.
    """
    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)

    # Simple downsample by decimation (acceptable for demo)
    ratio = original_rate // target_rate
    downsampled = audio[::ratio]

    return downsampled.astype(np.int16).tobytes()


async def transcribe_audio(pcm_bytes: bytes):
    try:
        resampled_audio = resample_audio(pcm_bytes)

        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/raw",
        }

        params = {
            "model": "nova-2",
            "encoding": "linear16",
            "sample_rate": 16000,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                DEEPGRAM_URL,
                headers=headers,
                params=params,
                content=resampled_audio,
            )

        if response.status_code != 200:
            print("Deepgram STT error:", response.text)
            return None

        data = response.json()

        transcript = (
            data["results"]["channels"][0]["alternatives"][0]["transcript"]
        )

        return transcript.strip()

    except Exception as e:
        print("Deepgram transcription error:", e)
        return None