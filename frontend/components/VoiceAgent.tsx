"use client";

import { useCallback, useState } from "react";
import {
  LiveKitRoom,
  useVoiceAssistant,
  RoomAudioRenderer,
  AgentState,
} from "@livekit/components-react";
import Transcript from "./Transcript";

const orbColors: Record<AgentState, string> = {
  disconnected: "#374151",
  connecting: "#ca8a04",
  initializing: "#ca8a04",
  listening: "#6366f1",
  thinking: "#3b82f6",
  speaking: "#8b5cf6",
  "pre-connect-buffering": "#ca8a04",
  failed: "#ef4444",
  idle: "#374151",
};

const barColors: Record<AgentState, string> = {
  disconnected: "rgba(156,163,175,0.3)",
  connecting: "rgba(202,138,4,0.5)",
  initializing: "rgba(202,138,4,0.5)",
  listening: "rgba(99,102,241,0.6)",
  thinking: "rgba(59,130,246,0.6)",
  speaking: "rgba(139,92,246,0.6)",
  "pre-connect-buffering": "rgba(202,138,4,0.5)",
  failed: "rgba(239,68,68,0.6)",
  idle: "rgba(156,163,175,0.3)",
};

const stateLabels: Record<AgentState, string> = {
  disconnected: "Ready",
  connecting: "Connecting",
  initializing: "Initializing",
  listening: "Listening",
  thinking: "Thinking",
  speaking: "Speaking",
  "pre-connect-buffering": "Buffering",
  failed: "Failed",
  idle: "Idle",
};

const barHeights = [6, 14, 20, 10, 18, 8, 16, 6];
const barDelays = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7];

function AgentOrb({ state }: { state: AgentState }) {
  const isActive = ["listening", "thinking", "speaking"].includes(state);
  const color = orbColors[state];
  const barColor = barColors[state];

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
      <div style={{ position: "relative", width: 160, height: 160, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            position: "absolute", inset: 0, borderRadius: "50%",
            border: `1px solid ${color}55`,
            animation: isActive ? "spin 8s linear infinite" : "none",
          }}
        />
        <div
          style={{
            position: "absolute", inset: 14, borderRadius: "50%",
            border: `1px solid ${color}33`,
            animation: isActive ? "spin 12s linear infinite reverse" : "none",
          }}
        />
        <div
          style={{
            width: 110, height: 110, borderRadius: "50%",
            background: color,
            display: "flex", alignItems: "center", justifyContent: "center",
            animation: isActive ? "breathe 2.5s ease-in-out infinite" : "none",
            transition: "background 0.5s ease",
          }}
        >
          <svg width="36" height="36" viewBox="0 0 32 32" fill="none">
            <path d="M16 6a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0v-6a4 4 0 0 1 4-4z" fill="rgba(255,255,255,0.9)" />
            <path d="M10 16a6 6 0 0 0 12 0" stroke="rgba(255,255,255,0.9)" strokeWidth="1.5" strokeLinecap="round" />
            <path d="M16 22v4" stroke="rgba(255,255,255,0.9)" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 3, height: 24 }}>
        {barHeights.map((h, i) => (
          <div
            key={i}
            style={{
              width: 3, borderRadius: 2,
              background: barColor, height: h,
              animation: isActive ? `wave 1s ease-in-out ${barDelays[i]}s infinite` : "none",
              transition: "background 0.5s ease",
            }}
          />
        ))}
      </div>

      <p style={{ fontSize: 11, letterSpacing: "0.08em", color: "rgba(255,255,255,0.4)", textTransform: "uppercase" }}>
        {stateLabels[state]}
      </p>
    </div>
  );
}

function AgentUI({ onDisconnect }: { onDisconnect: () => void }) {
  const { state } = useVoiceAssistant();

  return (
    <div
      style={{
        display: "flex",
        gap: 48,
        alignItems: "center",
        width: "100%",
        maxWidth: 900,
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24, flexShrink: 0 }}>
        <AgentOrb state={state} />
        <button
          onClick={onDisconnect}
          style={{
            padding: "10px 24px", borderRadius: 999,
            background: "transparent", color: "rgba(255,255,255,0.35)",
            fontSize: 13, border: "0.5px solid rgba(255,255,255,0.12)",
            cursor: "pointer", letterSpacing: "0.02em",
          }}
        >
          End Conversation
        </button>
      </div>

      <div style={{ flex: 1 }}>
        <Transcript agentState={state} />
      </div>
    </div>
  );
}

export default function VoiceAgent() {
  const [token, setToken] = useState<string | null>(null);
  const [wsUrl, setWsUrl] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  const connect = useCallback(async () => {
    const res = await fetch("/api/token?room=voice-agent-room&username=user");
    const data = await res.json();
    setToken(data.token);
    setWsUrl(data.url);
    setConnected(true);
  }, []);

  const disconnect = useCallback(() => {
    setToken(null);
    setWsUrl(null);
    setConnected(false);
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh", width: "100%",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        position: "relative", padding: "2rem",
      }}
    >
      {connected && (
        <div
          style={{
            position: "fixed", top: "1.5rem", left: "1.5rem",
            display: "flex", alignItems: "center", gap: 6,
            background: "rgba(255,255,255,0.06)",
            border: "0.5px solid rgba(255,255,255,0.1)",
            borderRadius: 999, padding: "4px 12px",
            fontSize: 11, color: "rgba(255,255,255,0.5)", letterSpacing: "0.04em",
          }}
        >
          <span
            style={{
              width: 6, height: 6, borderRadius: "50%",
              background: "#22c55e", display: "inline-block",
              animation: "pulse 1.5s ease-in-out infinite",
            }}
          />
          Live
        </div>
      )}

      <div style={{ textAlign: "center", marginBottom: "3rem" }}>
        <h1 style={{ fontSize: 28, fontWeight: 500, color: "#fff", letterSpacing: "-0.02em" }}>
          Real-Time Voice Agent
        </h1>
        <p style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", marginTop: 6, letterSpacing: "0.06em" }}>
          LIVEKIT · DEEPGRAM · GPT-4O MINI · CARTESIA
        </p>
      </div>

      {!connected ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 32 }}>
          <AgentOrb state="disconnected" />
          <button
            onClick={connect}
            style={{
              padding: "12px 32px", borderRadius: 999,
              background: "#6366f1", color: "#fff",
              fontSize: 15, fontWeight: 500,
              border: "none", cursor: "pointer", letterSpacing: "0.01em",
            }}
          >
            Start Conversation
          </button>
        </div>
      ) : (
        <LiveKitRoom
          token={token!}
          serverUrl={wsUrl!}
          connect={true}
          audio={true}
          video={false}
          onDisconnected={disconnect}
          style={{ width: "100%", display: "flex", justifyContent: "center" }}
        >
          <RoomAudioRenderer />
          <AgentUI onDisconnect={disconnect} />
        </LiveKitRoom>
      )}

      {connected && (
        <div style={{ position: "fixed", bottom: "2rem", display: "flex", gap: 8 }}>
          {["Noise Cancel", "VAD Active", "Turn Detection"].map((label) => (
            <span
              key={label}
              style={{
                fontSize: 10, padding: "3px 10px", borderRadius: 999,
                border: "0.5px solid rgba(255,255,255,0.1)",
                color: "rgba(255,255,255,0.25)", letterSpacing: "0.04em",
              }}
            >
              {label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}