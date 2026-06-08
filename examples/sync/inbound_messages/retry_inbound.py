import postmark

MESSAGE_ID = "id-of-a-failed-message"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    result = client.inbound.retry(MESSAGE_ID)

    print(f"Error code: {result.error_code}")
    print(f"Message:    {result.message}")
