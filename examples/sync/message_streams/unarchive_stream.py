import postmark

STREAM_ID = "my-broadcasts"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    stream = client.stream.unarchive(STREAM_ID)

    print(f"Unarchived stream: {stream.id}")
    print(f"Name:        {stream.name}")
    print(f"Type:        {stream.message_stream_type.value}")
    print(f"Archived at: {stream.archived_at}")
