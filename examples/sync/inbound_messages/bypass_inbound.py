import postmark

MESSAGE_ID = "your-blocked-message-id-here"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    result = client.inbound.bypass(MESSAGE_ID)

    print(f"Error code: {result.error_code}")
    print(f"Message:    {result.message}")
