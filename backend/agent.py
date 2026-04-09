import logging
import asyncio
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)


class VoiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a voice echo assistant. "
                "When the user speaks, respond by saying: You said: followed by "
                "an exact repeat of what they said. "
                "Keep responses short and natural. "
                "Do not use markdown, bullet points, or any special formatting."
            ),
        )


server = AgentServer()

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    logger.info("Session started — room: %s", ctx.room.name)

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=inference.STT("deepgram/nova-3"),
        llm=inference.LLM("openai/gpt-4o-mini"),
        tts=inference.TTS("cartesia/sonic-2"),
        turn_handling=TurnHandlingOptions(
            turn_detection=MultilingualModel(),
            allow_interruptions=True,
            min_interruption_duration=0.5,
            resume_false_interruption=True,
        ),
        aec_warmup_duration=3.0,
        user_away_timeout=20.0,
    )

    @session.on("user_state_changed")
    def on_user_state_changed(event):
        if event.new_state == "away":
            logger.info("User silent for 20s — sending reminder")
            asyncio.ensure_future(
                session.generate_reply(
                    instructions="Gently ask the user if they are still there. Keep it to one short sentence."
                )
            )

    await session.start(
        room=ctx.room,
        agent=VoiceAgent(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user warmly and tell them they can start speaking."
    )


if __name__ == "__main__":
    from livekit.agents import cli, WorkerOptions
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="voice-agent"))