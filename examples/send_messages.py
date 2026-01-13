import os
import asyncio
from dotenv import load_dotenv
import postmark
from postmark.models.messages import Email

# Load the variables from the .env file into os.environ
load_dotenv()


async def send_single_email():
    """
    Example: Sending a single email.
    """
    server_token = os.getenv(
        "POSTMARK_SERVER_TOKEN"
    )  # Set a verified sender signature in your .env file
    server = postmark.ServerClient(server_token=server_token)
    send_email = os.getenv("POSTMARK_SENDER_EMAIL")
    print("--- Sending Single Email ---")
    try:
        # You can pass a dictionary or an Email object
        response = await server.messages.Outbound.send(
            {
                "From": send_email,
                "To": "receiver@example.com",
                "Subject": "Hello from Postmark Python SDK",
                "TextBody": "This is a test email sent using the Python SDK.",
                "HtmlBody": "<html><body><strong>Hello</strong> from Postmark Python SDK.</body></html>",
                "MessageStream": "outbound",
            }
        )

        print(f"Email sent! Message ID: {response.message_id}")
        print(f"Status: {response.message}")

    except Exception as e:
        print(f"Error sending email: {e}")


async def send_using_model():
    """
    Example: Sending an email using the Pydantic Email model for better type safety.
    """
    server_token = os.getenv("POSTMARK_SERVER_TOKEN")
    server = postmark.ServerClient(server_token=server_token)
    send_email = os.getenv("POSTMARK_SENDER_EMAIL")

    print("\n--- Sending Email using Model ---")
    try:
        # Create the email object first
        email = Email(
            from_=send_email,  # Note: use from_ to avoid Python keyword conflict
            to="receiver@example.com",
            subject="Hello via Model",
            text_body="This email was built using the Pydantic model.",
            metadata={"user_id": "12345"},
        )

        response = await server.messages.Outbound.send(email)

        print(f"Email sent! Message ID: {response.message_id}")

    except Exception as e:
        print(f"Error sending email: {e}")


async def send_batch_emails():
    """
    Example: Sending a batch of emails (up to 500).
    """
    server_token = os.getenv("POSTMARK_SERVER_TOKEN")
    server = postmark.ServerClient(server_token=server_token)
    send_email = os.getenv("POSTMARK_SENDER_EMAIL")

    print("\n--- Sending Batch Emails Using JSON---")
    try:
        messages = [
            {
                "From": send_email,
                "To": "receiver1@example.com",
                "Subject": "Batch Email 1",
                "TextBody": "Hello Receiver 1",
            },
            {
                "From": send_email,
                "To": "receiver2@example.com",
                "Subject": "Batch Email 2",
                "TextBody": "Hello Receiver 2",
            },
        ]

        responses = await server.messages.Outbound.send_batch(messages)

        print(f"Batch processed. Sent {len(responses)} emails.")
        for i, resp in enumerate(responses):
            print(
                f"  Email {i+1}: ID {resp.message_id} (Error Code: {resp.error_code})"
            )

    except Exception as e:
        print(f"Error sending batch: {e}")


if __name__ == "__main__":

    async def main():
        await send_single_email()
        # await send_using_model()
        # await send_batch_emails()

    asyncio.run(main())
