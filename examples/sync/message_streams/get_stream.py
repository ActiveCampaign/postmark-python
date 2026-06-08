import postmark

STREAM_ID = "outbound"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    stream = client.stream.get(STREAM_ID)

    print(f"ID:           {stream.id}")
    print(f"Name:         {stream.name}")
    print(f"Type:         {stream.message_stream_type.value}")
    print(f"Description:  {stream.description}")
    print(f"Created at:   {stream.created_at}")
    print(f"Updated at:   {stream.updated_at}")
    print(
        f"Unsubscribe:  {stream.subscription_management_configuration.unsubscribe_handling_type.value}"
    )
