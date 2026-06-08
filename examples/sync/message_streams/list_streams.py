import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    result = client.stream.list()

    print(f"Total streams: {result.total}")
    print()

    for stream in result.items:
        print(f"  [{stream.id}] {stream.name}")
        print(f"       Type:        {stream.message_stream_type.value}")
        print(f"       Created at:  {stream.created_at}")
        print(f"       Archived:    {stream.archived_at is not None}")
        print("----------------------------------------")
