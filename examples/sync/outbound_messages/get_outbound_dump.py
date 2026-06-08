import postmark

MESSAGE_ID = "your-message-id-here"

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    dump = client.outbound.get_dump(MESSAGE_ID)
    print(dump.body)
