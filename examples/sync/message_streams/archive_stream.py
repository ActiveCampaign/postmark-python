import postmark

STREAM_ID = "my-broadcasts"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    result = client.stream.archive(STREAM_ID)

    print(f"Archived stream: {result.id}")
    print(f"Expected purge date: {result.expected_purge_date}")
