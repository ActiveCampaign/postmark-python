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
                print(f"       FROM: {msg.sender}")
                print(f"       TO: {', '.join([e.email for e in msg.to])}")

        print(f"Successfully streamed {count} messages.")

    except Exception as e:
        print(f"Error in stream_example: {e}")


if __name__ == "__main__":
    print("--- RUNNING LIST EXAMPLE ---")
    asyncio.run(list_example())

    print("\n--- RUNNING STREAM EXAMPLE ---")
    asyncio.run(stream_example())
