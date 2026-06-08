import postmark
from postmark.models.streams import MessageStreamType, UnsubscribeHandlingType

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    stream = client.stream.create(
        id="my-broadcasts",
        name="My Broadcast Stream",
        message_stream_type=MessageStreamType.BROADCASTS,
        description="Used for newsletters and announcements",
        unsubscribe_handling_type=UnsubscribeHandlingType.POSTMARK,
    )

    print("Created stream:")
    print(f"  ID:          {stream.id}")
    print(f"  Name:        {stream.name}")
    print(f"  Type:        {stream.message_stream_type.value}")
    print(f"  Description: {stream.description}")
    print(
        f"  Unsubscribe: {stream.subscription_management_configuration.unsubscribe_handling_type.value}"
    )
