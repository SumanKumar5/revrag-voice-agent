import httpx

from config import DEEPGRAM_API_KEY


DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"


async def generate_tts_audio(text: str):
    """
    Generate 48kHz mono PCM int16 audio using Deepgram TTS.
    Returns raw PCM bytes.
    """
    try:
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json",
        }

        params = {
            "model": "aura-asteria-en",
            "encoding": "linear16",
            "sample_rate": 48000,
        }

        payload = {
            "text": text
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                DEEPGRAM_TTS_URL,
                headers=headers,
                params=params,
                json=payload,
            )

        if response.status_code != 200:
            print("Deepgram TTS error:", response.text)
            return None

        return response.content  # raw PCM int16

    except Exception as e:
        print("Deepgram TTS error:", e)
        return None