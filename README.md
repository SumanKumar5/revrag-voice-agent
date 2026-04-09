 
# Real-Time Voice Agent

A production-grade real-time AI voice agent built with LiveKit Agents v1.5, featuring speech-to-text, LLM response generation, text-to-speech, adaptive interruption handling, and silence detection — with a polished Next.js frontend.

![LiveKit](https://img.shields.io/badge/LiveKit-Agents_v1.5-FF3B30?style=for-the-badge&logo=webrtc&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Deepgram](https://img.shields.io/badge/Deepgram-Nova--3-13EF93?style=for-the-badge&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o_mini-412991?style=for-the-badge&logo=openai&logoColor=white)
![Cartesia](https://img.shields.io/badge/Cartesia-Sonic--2-F97316?style=for-the-badge&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

---

## Overview

This project implements a full-stack real-time voice agent that:

- Joins a LiveKit room as an audio-only participant
- Listens to user speech via Deepgram Nova-3 STT (streaming)
- Generates responses using GPT-4o mini via LiveKit Inference
- Converts responses to speech using Cartesia Sonic-2 TTS
- Handles interruptions natively using LiveKit's adaptive interruption model
- Sends a gentle reminder after 20 seconds of user silence
- Displays a live conversation transcript in the browser UI

---

## System Architecture

```
Browser (Next.js)
     │
     ├── GET /api/token  →  Next.js Token Server  →  LiveKit Cloud
     │
     └── WebRTC (audio)  ──────────────────────────────────────────┐
                                                                    │
                                                          LiveKit Room
                                                                    │
                                                        Python Agent (backend)
                                                                    │
                                          ┌─────────────────────────┤
                                          │                         │
                                   Silero VAD              MultilingualModel
                                   (voice activity)        (turn detection)
                                          │
                                  Deepgram Nova-3
                                   (STT streaming)
                                          │
                                  GPT-4o mini LLM
                                  (via LiveKit Inference)
                                          │
                                  Cartesia Sonic-2
                                      (TTS)
                                          │
                                   Audio back to room
```

---

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Agent Framework | LiveKit Agents v1.5.1 |
| Speech-to-Text | Deepgram Nova-3 (streaming) |
| LLM | OpenAI GPT-4o mini |
| Text-to-Speech | Cartesia Sonic-2 |
| Voice Activity Detection | Silero VAD (neural) |
| Turn Detection | LiveKit MultilingualModel (transformer-based) |
| Noise Cancellation | LiveKit BVC |
| Package Manager | uv |
| Language | Python 3.12 |

### Frontend
| Layer | Technology |
|---|---|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS 4 |
| LiveKit SDK | @livekit/components-react |
| Token Server | Next.js API Route |

---

## Project Structure

```
voice-agent/
├── backend/
│   ├── agent.py              
│   ├── .env                  
│   ├── .env.example          
│   ├── pyproject.toml        
│   └── README.md
│
└── frontend/
    ├── app/
    │   ├── page.tsx           
    │   ├── layout.tsx         
    │   └── api/token/
    │       └── route.ts       
    ├── components/
    │   ├── VoiceAgent.tsx     
    │   └── Transcript.tsx     
    ├── .env.local             
    └── .env.example
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- [uv](https://astral.sh/uv) package manager
- [LiveKit Cloud](https://livekit.io) account (free tier)

---

### Backend Setup

```bash
cd backend
uv install
```

Copy the environment template and fill in your credentials:

```bash
cp .env.example .env
```

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
DEEPGRAM_API_KEY=your_deepgram_api_key
```

Download required models:

```bash
uv run python agent.py download-files
```

Start the agent:

```bash
uv run python agent.py dev
```

---

### Frontend Setup

```bash
cd frontend
npm install
```

Copy the environment template and fill in your credentials:

```bash
cp .env.example .env.local
```

```env
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud
```

Start the frontend:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Advanced Behavior

### A. No Overlap / Interruption Handling

The agent uses LiveKit Agents v1.5's native adaptive interruption system:

- `allow_interruptions=True` — agent stops speaking the moment user speaks
- `min_interruption_duration=0.5s` — filters out brief sounds and noise
- `resume_false_interruption=True` — agent resumes if the interruption was accidental
- `aec_warmup_duration=3.0s` — prevents echo from triggering false interruptions on startup
- `MultilingualModel` turn detection — transformer-based semantic model that understands when the user has truly finished their turn, reducing premature responses

State machine managed natively by `AgentSession`:

```
User state:   listening → speaking → listening → away
Agent state:  idle → thinking → speaking → idle
```

### B. Silence Handling

- `user_away_timeout=20.0` — SDK marks user as `away` after 20 seconds of silence
- A `user_state_changed` event listener fires when state becomes `away`
- Agent sends a single gentle reminder via `session.generate_reply()`
- Does not loop — resets only when user speaks again

---

## Credentials

All credentials are managed via environment variables and are never committed to version control.

| Variable | Description |
|---|---|
| `LIVEKIT_URL` | LiveKit Cloud WebSocket URL |
| `LIVEKIT_API_KEY` | LiveKit API Key |
| `LIVEKIT_API_SECRET` | LiveKit API Secret |
| `DEEPGRAM_API_KEY` | Deepgram API Key (for STT) |

---
