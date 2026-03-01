from livekit.api import AccessToken, VideoGrants
from config import (
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
)

ROOM_NAME = "test-room"

identity = "test-user"

token = (
    AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    .with_identity(identity)
    .with_grants(
        VideoGrants(
            room_join=True,
            room=ROOM_NAME,
        )
    )
    .to_jwt()
)

print(token)