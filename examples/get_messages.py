import os
import asyncio
from dotenv import load_dotenv #
import postmark


# Load the variables from the .env file into os.environ
load_dotenv()

async def find():
    server_token: str = os.getenv("POSTMARK_SERVER_TOKEN")
    
    if not server_token:
        print("Please set POSTMARK_SERVER_TOKEN in your .env file")
        return

    try:
        messages, total = await postmark.messages.Outbound.find(server_token=server_token)
        print(messages)
        print(f"Found {total} messages, retrieved {len(messages)} messages.")
        if messages:
            for msg in messages[:3]:
                print(f"  - {msg.subject}")
                print(f"    FROM: {msg.from_}")
                print(f"    TO: {', '.join([e.email for e in msg.to])}")
                print(f"    DATE: {msg.received_at}")
        else:
            print("No messages found")
            
    except Exception as e:
        print(f"Error: {e}")

async def find_all():
    server_token: str = os.getenv("POSTMARK_SERVER_TOKEN")
    
    if not server_token:
        print("Please set POSTMARK_SERVER_TOKEN in your .env file")
        return

    try:
        messages = await postmark.messages.Outbound.find_all(server_token=server_token)
        print(f"Found messages, retrieved {len(messages)} messages.")
        if messages:
            for msg in messages[:3]:
                print(f"  - {msg.subject}")
                print(f"    FROM: {msg.from_}")
                print(f"    TO: {', '.join([e.email for e in msg.to])}")
                print(f"    DATE: {msg.received_at}")
        else:
            print("No messages found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # asyncio.run(find())
    asyncio.run(find_all())