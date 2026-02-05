import os
import asyncio
from dotenv import load_dotenv
import postmark

# Load the variables from the .env file into os.environ
load_dotenv()


async def list_example():
    """
    Example using .list() (formerly .find())
    Best for: Getting a specific page of results or checking total counts.
    """
    server_token: str = os.getenv("POSTMARK_SERVER_TOKEN")
    server = postmark.ServerClient(server_token=server_token)

    try:
        messages, total = await server.messages.Outbound.list(count=10)

        print(f"Total matches on server: {total}")
        print(f"Retrieved in this page: {len(messages)}")

        if messages:
            for msg in messages[:3]:
                print(f"  - {msg.subject}")
                print(f"    ID: {msg.message_id}")
                print(f"    FROM: {msg.sender}")
                print(f"    TO: {', '.join([e.email for e in msg.to])}")
                print(f"    DATE: {msg.received_at}")
        else:
            print("No messages found")

    except Exception as e:
        print(f"Error in list_example: {e}")


async def stream_example():
    """
    Use .stream() to iterate over large datasets without memory issues.
    """
    server_token: str = os.getenv("POSTMARK_SERVER_TOKEN")
    server = postmark.ServerClient(server_token=server_token)

    print("Streaming messages...")

    try:
        count = 0

        # Get 20 messages
        async for msg in server.messages.Outbound.stream(max_messages=20):
            count += 1

            # Print details for the first 3...
            if count <= 3:
                print(f"  #{count} - {msg.subject}")
                print(f"       ID: {msg.message_id}")
                print(f"       FROM: {msg.sender}")
                print(f"       TO: {', '.join([e.email for e in msg.to])}")

        print(f"Successfully streamed {count} messages.")

    except Exception as e:
        print(f"Error in stream_example: {e}")


async def get_details_example(message_id: str):
    """
    Example using .get() to retrieve full details of a specific message.
    Populates and prints all available data from the returned OutboundMessageDetails object.
    """
    server_token: str = os.getenv("POSTMARK_SERVER_TOKEN")
    server = postmark.ServerClient(server_token=server_token)

    print(f"Fetching details for message ID: {message_id}...")

    try:
        # Get message details
        message = await server.messages.Outbound.get(message_id)

        print("\n--- Message Details ---")
        print(f"Message ID:     {message.message_id}")
        print(f"Status:         {message.status}")
        print(f"Message Stream: {message.message_stream}")
        print(f"Received At:    {message.received_at}")
        print(f"From:           {message.sender}")

        # Helper to format list of EmailAddress objects
        format_emails = lambda emails: ", ".join(
            [f"{e.name} <{e.email}>" if e.name else e.email for e in emails]
        )

        print(f"To:             {format_emails(message.to)}")
        if message.cc:
            print(f"Cc:             {format_emails(message.cc)}")
        if message.bcc:
            print(f"Bcc:            {format_emails(message.bcc)}")

        print(f"Subject:        {message.subject}")
        if message.tag:
            print(f"Tag:            {message.tag}")

        print("\n--- Content Bodies ---")
        print(
            f"Text Body:      {len(message.text_body) if message.text_body else 'None'}"
        )
        print(
            f"HTML Body:      {len(message.html_body) if message.html_body else 'None'}"
        )
        if message.body:
            print(f"Raw Body:       {len(message.body)} chars")

        print("\n--- Configuration ---")
        print(f"Track Opens:    {message.track_opens}")
        print(f"Track Links:    {message.track_links}")
        print(f"Sandboxed:      {message.sandboxed}")

        if message.metadata:
            print(f"\n--- Metadata ---")
            for k, v in message.metadata.items():
                print(f"  {k}: {v}")

        if message.attachments:
            print(f"\n--- Attachments ({len(message.attachments)}) ---")
            for attachment in message.attachments:
                # Check if it's an object (OutboundMessageDetails usually returns Attachment objects)
                if hasattr(attachment, "name"):
                    print(
                        f"  - {attachment.name} ({attachment.content_type}, {attachment.content_length} bytes)"
                    )
                else:
                    print(f"  - {attachment}")

        if message.message_events:
            print(f"\n--- Message Events ({len(message.message_events)}) ---")
            for event in message.message_events:
                # Simplistic dump of details if present
                details_str = (
                    f" - {event.details.model_dump(exclude_none=True)}"
                    if event.details
                    else ""
                )
                print(f"  - [{event.received_at}] {event.type}{details_str}")

    except Exception as e:
        print(f"Error getting message details: {e}")


if __name__ == "__main__":
    print("--- GET SINGLE MESSAGE BY ID EXAMPLE ---")
    asyncio.run(get_details_example(message_id="a32a9dc7-a81c-4c4d-a8a3-32124297d0dd"))

    # print("--- RUNNING LIST EXAMPLE ---")
    # asyncio.run(list_example())

    # print("\n--- RUNNING STREAM EXAMPLE ---")
    # asyncio.run(stream_example())
