import VoiceAgent from "@/components/VoiceAgent";

export default function Home() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#0d1117",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <VoiceAgent />
    </main>
  );
}