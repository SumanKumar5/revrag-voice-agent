import asyncio
import json
import time
import numpy as np

from livekit import rtc
from livekit.api import AccessToken, VideoGrants

from config import LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL
from stt_service import transcribe_audio
from tts_service import generate_tts_audio


ROOM_NAME = "test-room"
AGENT_IDENTITY = "voice-agent"

ENERGY_THRESHOLD = 800
MIN_SPEECH_FRAMES = 5
SILENCE_FRAMES_REQUIRED = 20
SILENCE_REMINDER_SECONDS = 20


class AgentState:
    LISTENING = "listening"
    SPEAKING = "speaking"


agent_state = AgentState.LISTENING
tts_task = None
last_user_activity_time = time.time()


async def send_data(room, payload: dict):
    await room.local_participant.publish_data(
        json.dumps(payload).encode("utf-8"),
        reliable=True,
    )


async def play_tts_audio(room: rtc.Room, pcm_audio: bytes):
    global agent_state

    agent_state = AgentState.SPEAKING
    print("Agent speaking...")

    source = rtc.AudioSource(48000, 1)
    track = rtc.LocalAudioTrack.create_audio_track("agent-voice", source)
    await room.local_participant.publish_track(track)

    samples_per_channel = 960
    bytes_per_sample = 2
    frame_size = samples_per_channel * bytes_per_sample
    total_frames = len(pcm_audio) // frame_size

    try:
        for i in range(total_frames):
            if agent_state != AgentState.SPEAKING:
                break

            start = i * frame_size
            end = start + frame_size
            chunk = pcm_audio[start:end]

            frame = rtc.AudioFrame(
                chunk,
                48000,
                1,
                samples_per_channel
            )

            await source.capture_frame(frame)
            await asyncio.sleep(0.02)

    except asyncio.CancelledError:
        print("TTS interrupted.")
    finally:
        agent_state = AgentState.LISTENING
        print("Agent finished speaking.")


async def silence_monitor(room: rtc.Room):
    global last_user_activity_time

    while True:
        await asyncio.sleep(1)

        if (
            agent_state == AgentState.LISTENING
            and time.time() - last_user_activity_time > SILENCE_REMINDER_SECONDS
        ):
            print("Silence detected. Sending reminder.")

            reminder_text = "Are you still there?"
            tts_audio = await generate_tts_audio(reminder_text)

            if tts_audio:
                await send_data(room, {
                    "type": "agent",
                    "text": reminder_text,
                    "latency_ms": 0
                })

                await play_tts_audio(room, tts_audio)

            last_user_activity_time = time.time()


async def handle_audio_track(track: rtc.RemoteAudioTrack, room: rtc.Room):
    global agent_state, tts_task, last_user_activity_time

    print("Audio track subscribed. Listening for frames...")

    audio_stream = rtc.AudioStream(track)

    user_speaking = False
    silence_counter = 0
    speech_counter = 0
    audio_buffer = []

    async for event in audio_stream:
        frame = event.frame
        pcm_data = frame.data

        audio_array = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32)
        rms = np.sqrt(np.mean(audio_array ** 2))

        if rms > ENERGY_THRESHOLD:
            speech_counter += 1
            silence_counter = 0
            last_user_activity_time = time.time()

            if agent_state == AgentState.SPEAKING and tts_task:
                print("User interrupted agent.")
                tts_task.cancel()
                agent_state = AgentState.LISTENING

            if not user_speaking and speech_counter >= MIN_SPEECH_FRAMES:
                print("User started speaking")
                user_speaking = True
                audio_buffer = []

            if user_speaking:
                audio_buffer.append(pcm_data)

        else:
            speech_counter = 0

            if user_speaking:
                silence_counter += 1

                if silence_counter >= SILENCE_FRAMES_REQUIRED:
                    print("User stopped speaking")
                    user_speaking = False

                    if agent_state == AgentState.LISTENING:
                        full_audio = b"".join(audio_buffer)

                        start_time = time.time()
                        transcript = await transcribe_audio(full_audio)

                        if transcript:
                            print("Transcript:", transcript)

                            await send_data(room, {
                                "type": "transcript",
                                "user": transcript
                            })

                            response_text = f"You said: {transcript}"
                            tts_audio = await generate_tts_audio(response_text)

                            latency_ms = int((time.time() - start_time) * 1000)

                            await send_data(room, {
                                "type": "agent",
                                "text": response_text,
                                "latency_ms": latency_ms
                            })

                            if tts_audio:
                                tts_task = asyncio.create_task(
                                    play_tts_audio(room, tts_audio)
                                )

                    audio_buffer = []
                    silence_counter = 0


async def main():
    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(AGENT_IDENTITY)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=ROOM_NAME,
            )
        )
        .to_jwt()
    )

    room = rtc.Room()

    @room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant):
        if publication.kind == rtc.TrackKind.KIND_AUDIO:
            asyncio.create_task(handle_audio_track(track, room))

    print("Connecting to LiveKit...")
    await room.connect(LIVEKIT_URL, token)

    print("Connected successfully.")
    print("Waiting for participants...")

    asyncio.create_task(silence_monitor(room))

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())