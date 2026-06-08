import postmark
from postmark.models.streams import UnsubscribeHandlingType

STREAM_ID = "my-broadcasts"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    stream = client.stream.edit(
        STREAM_ID,
        name="Updated Broadcast Stream",
        description="Newsletters and product updates",
        unsubscribe_handling_type=UnsubscribeHandlingType.POSTMARK,
    )

    print("Updated stream:")
    print(f"  ID:          {stream.id}")
    print(f"  Name:        {stream.name}")
    print(f"  Description: {stream.description}")
    print(
        f"  Unsubscribe: {stream.subscription_management_configuration.unsubscribe_handling_type.value}"
    )
