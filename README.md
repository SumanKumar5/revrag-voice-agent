<div align="center">

# Real-Time Voice Agent

**A production-grade, full-stack AI voice agent powered by LiveKit, Deepgram, GPT-4o mini, and Cartesia — with a polished Next.js frontend.**

<br/>

![LiveKit](https://img.shields.io/badge/LiveKit-Agents_v1.5-FF3B30?style=for-the-badge&logo=webrtc&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)

![Deepgram](https://img.shields.io/badge/Deepgram-Nova--3-13EF93?style=for-the-badge&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o_mini-412991?style=for-the-badge&logo=openai&logoColor=white)
![Cartesia](https://img.shields.io/badge/Cartesia-Sonic--2-F97316?style=for-the-badge&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

<br/>

![Version](https://img.shields.io/badge/version-2.0.0-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen?style=flat-square)

</div>

---

## What It Does

This project is a real-time AI voice agent that joins a LiveKit room and interacts with users entirely through audio. It implements a full STT → LLM → TTS pipeline with production-grade interruption handling and silence detection.

| Capability | Details |
|---|---|
| Speech-to-Text | Deepgram Nova-3 — streaming, low-latency |
| Language Model | GPT-4o mini via LiveKit Inference |
| Text-to-Speech | Cartesia Sonic-2 — natural, expressive voice |
| Interruption Handling | Adaptive ML-based interruption detection |
| Silence Detection | 20s away timeout with gentle reminder |
| VAD | Silero neural voice activity detection |
| Turn Detection | MultilingualModel — transformer-based semantic EOU |
| Noise Cancellation | LiveKit BVC (background voice cancellation) |
| Live Transcript | Real-time conversation display in the browser |

---

## System Architecture

```
Browser (Next.js)
     │
     ├── GET /api/token ──► Next.js Token Server ──► LiveKit Cloud
     │
     └── WebRTC (audio) ──────────────────────────────────────────►  LiveKit Room
                                                                           │
                                                               Python Agent (backend)
                                                                           │
                                          ┌────────────────────────────────┤
                                          │                                │
                                   Silero VAD                    MultilingualModel
                                (voice activity)                  (turn detection)
                                          │
                                 Deepgram Nova-3
                                 (STT — streaming)
                                          │
                                 GPT-4o mini LLM
                              (via LiveKit Inference)
                                          │
                                 Cartesia Sonic-2
                                      (TTS)
                                          │
                              Audio published back to room
```

---

## Tech Stack

### Backend
| Layer | Technology | Version |
|---|---|---|
| Agent Framework | LiveKit Agents | v1.5.1 |
| Speech-to-Text | Deepgram Nova-3 | streaming |
| LLM | OpenAI GPT-4o mini | via LiveKit Inference |
| Text-to-Speech | Cartesia Sonic-2 | via LiveKit Inference |
| VAD | Silero VAD | neural |
| Turn Detection | LiveKit MultilingualModel | transformer-based |
| Noise Cancellation | LiveKit BVC | — |
| Package Manager | uv | v0.11+ |
| Language | Python | 3.12 |

### Frontend
| Layer | Technology | Version |
|---|---|---|
| Framework | Next.js (App Router) | 15 |
| Language | TypeScript | 5 |
| Styling | Tailwind CSS | 4 |
| LiveKit SDK | @livekit/components-react | latest |
| Token Server | Next.js API Route | built-in |

---

## Project Structure

```
voice-agent/
│
├── backend/
│   ├── agent.py              
│   ├── .env.example      
│   ├── pyproject.toml    
│   ├── uv.lock           
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
    ├── .env.example           
    └── package.json
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- [`uv`](https://astral.sh/uv) package manager
- [LiveKit Cloud](https://livekit.io) account (free tier)
- [Deepgram](https://deepgram.com) account (free $200 credit)

---

### Backend Setup

```bash
cd backend

# Install dependencies
uv install

# Copy and fill in credentials
cp .env.example .env
```

Edit `.env`:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
DEEPGRAM_API_KEY=your_deepgram_api_key
```

Download required ML models:

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

# Install dependencies
npm install

# Copy and fill in credentials
cp .env.example .env.local
```

Edit `.env.local`:

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

> Run both backend and frontend simultaneously in separate terminals.

---

## Advanced Behavior

### A — No Overlap / Interruption Handling

The agent uses LiveKit Agents v1.5's native adaptive interruption system, requiring no manual state management:

- **`allow_interruptions=True`** — agent stops speaking the instant the user speaks
- **`min_interruption_duration=0.5s`** — filters brief sounds and background noise
- **`resume_false_interruption=True`** — agent automatically resumes if interruption was accidental (e.g. cough, backchannel)
- **`aec_warmup_duration=3.0s`** — prevents echo from triggering false interruptions on startup
- **`MultilingualModel`** — transformer-based semantic end-of-utterance detector, understands conversational context

Native state machine managed by `AgentSession`:

```
User:   listening ──► speaking ──► listening ──► away
Agent:  idle ──► thinking ──► speaking ──► idle
```

### B — Silence Handling

- **`user_away_timeout=20.0`** — SDK marks user as `away` after 20 seconds of silence
- A `user_state_changed` event listener fires when state transitions to `away`
- Agent sends a single gentle reminder via `session.generate_reply()`
- One-shot — does not loop or repeat until user speaks again

---

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| `LIVEKIT_URL` | backend + frontend | LiveKit Cloud WebSocket URL |
| `LIVEKIT_API_KEY` | backend + frontend | LiveKit API Key |
| `LIVEKIT_API_SECRET` | backend + frontend | LiveKit API Secret |
| `DEEPGRAM_API_KEY` | backend | Deepgram API Key for STT |

> All credentials are managed via `.env` files and are never committed to version control.

---

## License

MIT © [Suman Kumar](https://github.com/SumanKumar5)