import { AccessToken, AgentDispatchClient } from "livekit-server-sdk";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const roomName = request.nextUrl.searchParams.get("room") ?? "voice-agent-room";
  const participantName = request.nextUrl.searchParams.get("username") ?? "user";

  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;
  const wsUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL;

  if (!apiKey || !apiSecret || !wsUrl) {
    return NextResponse.json({ error: "Missing LiveKit credentials" }, { status: 500 });
  }

  const token = new AccessToken(apiKey, apiSecret, { identity: participantName });
  token.addGrant({
    roomJoin: true,
    room: roomName,
    canPublish: true,
    canSubscribe: true,
  });

  const jwt = await token.toJwt();

  const httpUrl = wsUrl.replace("wss://", "https://").replace("ws://", "http://");
  const dispatchClient = new AgentDispatchClient(httpUrl, apiKey, apiSecret);
  await dispatchClient.createDispatch(roomName, "voice-agent");

  return NextResponse.json({ token: jwt, url: wsUrl });
}