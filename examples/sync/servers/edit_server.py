import postmark
from postmark.models.servers import ServerColor, TrackLinks

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    server = client.server.edit(
        name="My Updated Server",
        color=ServerColor.GREEN,
        track_opens=True,
        track_links=TrackLinks.HTML_AND_TEXT,
        inbound_spam_threshold=5,
    )

    print(f"ID:            {server.id}")
    print(f"Name:          {server.name}")
    print(f"Color:         {server.color}")
    print(f"Track opens:   {server.track_opens}")
    print(f"Track links:   {server.track_links}")
    print(f"Spam threshold: {server.inbound_spam_threshold}")
