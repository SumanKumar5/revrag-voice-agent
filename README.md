# RevRag – Real-Time Voice Agent (LiveKit + Deepgram)

A production-style real-time AI voice agent built using LiveKit, Deepgram STT/TTS, and Python async architecture.

The agent joins a LiveKit room, listens to user speech, converts speech to text, generates a response, converts it back to speech, and streams it back into the room — with proper interruption handling and silence detection.

---

## Features

- Real-time audio streaming via LiveKit
- Speech-to-Text (Deepgram Nova-2)
- Text-to-Speech (Deepgram Aura)
- Async interruption handling
- No-overlap speech control
- RMS-based Voice Activity Detection (VAD)
- 20-second silence reminder
- Latency measurement
- Optional modern UI for testing
- Clean state-machine architecture

---

## System Architecture

User Microphone  
↓  
LiveKit (AudioStream)  
↓  
RMS-based VAD  
↓  
Deepgram STT (Nova-2)  
↓  
Response Generator ("You said: ...")  
↓  
Deepgram TTS (Aura)  
↓  
LiveKit AudioSource  
↓  
Room Playback  

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/SumanKumar5/revrag-voice-agent.git
cd revrag-voice-agent
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
DEEPGRAM_API_KEY=your_deepgram_api_key
```

---

## Running the Agent

### Start the Voice Agent

```bash
python app/main.py
```

The agent will:

- Connect to LiveKit
- Wait for participants
- Process incoming audio

---

## Start Test UI (Browser Testing)

The UI is served using FastAPI and allows you to test the voice agent
directly from your browser.

### Step 1 --- Open Terminal

``` bash
cd revrag-voice-agent
venv\Scripts\activate   # Windows
```

### Step 2 --- Start FastAPI

``` bash
uvicorn app.api:app --reload
```

Open: http://127.0.0.1:8000

### Important

Run in two terminals:

Terminal 1:

``` bash
python app/main.py
```

Terminal 2:

``` bash
uvicorn app.api:app --reload
```

The UI allows:

- Connecting to the room
- Viewing live transcripts
- Seeing latency
- Visualizing microphone activity

---

## Behavior Details

### STT → Response → TTS Flow

- User speech captured via LiveKit
- Downsampled to 16kHz
- Sent to Deepgram STT
- Agent responds:  
  "You said: <transcript>"
- Converted to 48kHz PCM via Deepgram TTS
- Streamed back into room

---

### No Overlap Handling

Implemented using explicit state control:

```python
class AgentState:
    LISTENING
    SPEAKING
```

If user speaks while agent is speaking:

- TTS async task is cancelled
- Agent immediately returns to listening state

This prevents overlapping speech and ensures natural conversational behavior.

---

### Voice Activity Detection (VAD)

RMS-based audio energy detection:

- Energy threshold filtering
- Minimum speech frame requirement
- Silence frame confirmation

This prevents background noise from triggering responses.

---

### Silence Handling

A background async task monitors inactivity.

If:

No user speech for 20+ seconds  
AND agent is not speaking  

The agent plays:

"Are you still there?"

The reminder is triggered once per silence window and does not loop.

---

## Tech Stack

- Python 3.12
- LiveKit Python SDK
- LiveKit API SDK (JWT generation)
- Deepgram REST API (STT + TTS)
- FastAPI (optional UI)
- Asyncio

---

## Design Decisions

- Explicit state machine over implicit flags
- Async task cancellation for interruption
- RMS-based VAD (lightweight, no ML dependency)
- Frame-based streaming for real-time playback
- Separation of concerns:

  - main.py → orchestration
  - stt_service.py → STT logic
  - tts_service.py → TTS logic
  - api.py → UI + token generation

---
