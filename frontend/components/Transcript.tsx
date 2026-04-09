"use client";

import { useEffect, useRef } from "react";
import {
  useTranscriptions,
  useLocalParticipant,
} from "@livekit/components-react";

function TypingIndicator() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 4,
        alignItems: "flex-start",
      }}
    >
      <span
        style={{
          fontSize: 10,
          letterSpacing: "0.06em",
          color: "rgba(255,255,255,0.25)",
          textTransform: "uppercase",
        }}
      >
        Agent
      </span>
      <div
        style={{
          background: "rgba(255,255,255,0.06)",
          border: "0.5px solid rgba(255,255,255,0.08)",
          borderRadius: 12,
          borderBottomLeftRadius: 4,
          padding: "10px 16px",
          display: "flex",
          gap: 4,
          alignItems: "center",
        }}
      >
        {[0, 0.2, 0.4].map((delay, i) => (
          <div
            key={i}
            style={{
              width: 5,
              height: 5,
              borderRadius: "50%",
              background: "rgba(255,255,255,0.4)",
              animation: `tdot 1.2s ease-in-out ${delay}s infinite`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

export default function Transcript({ agentState }: { agentState: string }) {
  const transcriptions = useTranscriptions();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcriptions.length]);

  const isThinking = agentState === "thinking";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 8,
        width: "100%",
      }}
    >
      <span
        style={{
          fontSize: 10,
          letterSpacing: "0.08em",
          color: "rgba(255,255,255,0.25)",
          textTransform: "uppercase",
          marginBottom: 4,
        }}
      >
        Conversation
      </span>

      <div
        style={{
          background: "rgba(255,255,255,0.03)",
          border: "0.5px solid rgba(255,255,255,0.08)",
          borderRadius: 14,
          padding: "1.25rem",
          height: 340,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        {transcriptions.length === 0 && !isThinking && (
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "rgba(255,255,255,0.15)",
              fontSize: 13,
              letterSpacing: "0.02em",
            }}
          >
            Conversation will appear here...
          </div>
        )}
        {transcriptions.map((t, i) => {
          const raw = t as any;
          const identity = raw?.participantInfo?.identity ?? "";
          const isUser = identity === "user";
          const isAgent = !isUser;
          const text = t.segment?.text ?? raw.text ?? "";
          if (!text) return null;

          return (
            <div
              key={t.segment?.id ?? i}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 4,
                alignItems: isAgent ? "flex-start" : "flex-end",
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  letterSpacing: "0.06em",
                  color: "rgba(255,255,255,0.25)",
                  textTransform: "uppercase",
                }}
              >
                {isAgent ? "Agent" : "You"}
              </span>
              <div
                style={{
                  maxWidth: "85%",
                  padding: "10px 14px",
                  borderRadius: 12,
                  fontSize: 13,
                  lineHeight: 1.6,
                  ...(isAgent
                    ? {
                        background: "rgba(255,255,255,0.06)",
                        color: "rgba(255,255,255,0.75)",
                        border: "0.5px solid rgba(255,255,255,0.08)",
                        borderBottomLeftRadius: 4,
                      }
                    : {
                        background: "#6366f1",
                        color: "rgba(255,255,255,0.9)",
                        borderBottomRightRadius: 4,
                      }),
                }}
              >
                {text}
              </div>
            </div>
          );
        })}

        {isThinking && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
