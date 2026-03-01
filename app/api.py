from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from livekit.api import AccessToken, VideoGrants

from app.config import LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL

ROOM_NAME = "test-room"

app = FastAPI()

@app.get("/token")
def generate_token(identity: str = Query(...)):
    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room="test-room",
            )
        )
        .to_jwt()
    )

    return {
        "token": token,
        "url": LIVEKIT_URL
    }

@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<title>LiveKit AI Voice Agent</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<style>
body {
    margin:0;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto;
    background:radial-gradient(circle at top,#1e293b,#0f172a);
    height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
}

.card {
    width:480px;
    background:rgba(255,255,255,0.05);
    backdrop-filter:blur(20px);
    border:1px solid rgba(255,255,255,0.1);
    border-radius:20px;
    padding:30px;
    box-shadow:0 20px 60px rgba(0,0,0,0.5);
    transition:all 0.3s ease;
}

h1 {margin:0 0 5px 0; font-size:22px}
.sub {opacity:0.6; font-size:13px; margin-bottom:20px}

button {
    padding:10px;
    border:none;
    border-radius:10px;
    font-weight:600;
    cursor:pointer;
    transition:all 0.2s ease;
}

.connect {
    background:linear-gradient(135deg,#6366f1,#8b5cf6);
    color:white;
    width:100%;
}

.disconnect {
    background:#ef4444;
    color:white;
    width:100%;
    margin-top:10px;
}

button:hover {
    transform:translateY(-2px);
}

.visualizer {
    height:60px;
    margin:15px 0;
    display:flex;
    align-items:flex-end;
    justify-content:center;
}

.bar {
    width:6px;
    margin:2px;
    background:#22c55e;
    border-radius:3px;
    transition:height 0.1s ease;
}

.transcript-panel {
    background:rgba(0,0,0,0.3);
    padding:10px;
    border-radius:10px;
    height:120px;
    overflow-y:auto;
    font-size:13px;
    margin-top:15px;
}

.message {
    opacity:0;
    transform:translateY(10px);
    animation:fadeIn 0.3s forwards;
}

.user {color:#22c55e}
.agent {color:#a78bfa}

.latency {
    font-size:12px;
    opacity:0.6;
    margin-top:6px;
}

@keyframes fadeIn {
    to {opacity:1; transform:translateY(0)}
}
</style>
</head>
<body>

<div class="card">
<h1>AI Voice Agent</h1>
<div class="sub">Real-time LiveKit + Deepgram</div>

<div class="visualizer" id="visualizer"></div>

<button class="connect" id="connectBtn">Connect</button>
<button class="disconnect" id="disconnectBtn" style="display:none">Disconnect</button>

<div class="transcript-panel" id="transcripts"></div>
<div class="latency" id="latency"></div>
</div>

<script type="module">
import { Room, createLocalAudioTrack } from "https://cdn.skypack.dev/livekit-client";

let room;
let audioContext;
let analyser;
let dataArray;

const visualizer = document.getElementById("visualizer");
const transcripts = document.getElementById("transcripts");
const latencyLabel = document.getElementById("latency");
const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");

function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = "message " + type;
    div.innerText = text;
    transcripts.appendChild(div);
    transcripts.scrollTop = transcripts.scrollHeight;
}

function setupVisualizer(stream) {
    audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);
    dataArray = new Uint8Array(analyser.frequencyBinCount);

    for (let i = 0; i < 15; i++) {
        const bar = document.createElement("div");
        bar.className = "bar";
        visualizer.appendChild(bar);
    }

    animate();
}

function animate() {
    requestAnimationFrame(animate);
    if (!analyser) return;
    analyser.getByteFrequencyData(dataArray);
    const bars = document.querySelectorAll(".bar");
    bars.forEach((bar, i) => {
        const v = dataArray[i] / 255;
        bar.style.height = (10 + v * 50) + "px";
    });
}

connectBtn.onclick = async () => {
    const identity = "user-" + Math.floor(Math.random() * 1000);
    const res = await fetch(`/token?identity=${identity}`);
    const data = await res.json();

    room = new Room();

    room.on("dataReceived", payload => {
        const msg = JSON.parse(new TextDecoder().decode(payload));
        if (msg.type === "transcript") {
            addMessage("You: " + msg.user, "user");
        }
        if (msg.type === "agent") {
            addMessage("Agent: " + msg.text, "agent");
            latencyLabel.innerText = "Latency: " + msg.latency_ms + " ms";
        }
    });

    room.on("trackSubscribed", (track) => {
        if (track.kind === "audio") {
            const el = track.attach();
            document.body.appendChild(el);
        }
    });

    await room.connect(data.url, data.token);

    const audioTrack = await createLocalAudioTrack();
    await room.localParticipant.publishTrack(audioTrack);

    const stream = new MediaStream([audioTrack.mediaStreamTrack]);
    setupVisualizer(stream);

    connectBtn.style.display = "none";
    disconnectBtn.style.display = "block";
};

disconnectBtn.onclick = async () => {
    if (room) {
        await room.disconnect();
        location.reload();
    }
};
</script>

</body>
</html>
"""