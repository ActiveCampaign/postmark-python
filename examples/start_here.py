"""
start_here.py — the fastest way to send your first email with postmark-python.

BEFORE YOU RUN THIS FILE
─────────────────────────────────────────────────────────────────────────────
1. Replace the three placeholder strings below (SERVER_TOKEN, SENDER, TO)
   with real values from your Postmark account.

2. The token is hard-coded here to keep this file short and self-contained.
   In any real project — even a personal script — use an environment variable
   instead:

       import os
       token = os.environ["POSTMARK_SERVER_TOKEN"]

   A hard-coded token ends up in git history, log files, and tracebacks!!
   *Environment variables keep you safe.*

   The Getting Started wiki page shows several patterns for loading env vars
   (plain os.environ, python-dotenv, and platform secret managers):
   https://github.com/ActiveCampaign/postmark-python/wiki/Getting-Started

3. The try/except blocks below show every exception the SDK can raise.
   In production you almost certainly want to:
     - Log failures with enough context to debug them (request_id is invaluable
       when opening a support ticket with Postmark).
     - Handle InactiveRecipientException by removing the address from your
       send list — Postmark will keep rejecting it until you do.
     - Let InvalidAPIKeyException propagate loudly; it means a deploy-time
       configuration problem, not a per-request transient failure.
     - Treat RateLimitException and TimeoutException as signals to back off —
       the SDK already retries both automatically (3 attempts by default), so
       by the time you catch one, retries are exhausted.
"""

import asyncio

import postmark
from postmark import (
    InactiveRecipientException,
    InvalidAPIKeyException,
    InvalidEmailException,
    PostmarkAPIException,
    PostmarkException,
    RateLimitException,
    ServerException,
    TimeoutException,
    ValidationException,
)

# ── Replace these ────────────────────────────────────────────────────────────
SERVER_TOKEN = "xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx"  # nosec B105
SENDER = "you@your-verified-domain.com"
TO = "recipient@example.com"
# ─────────────────────────────────────────────────────────────────────────────


# ── Async version ─────────────────────────────────────────────────────────────


# Here's a stripped-down version of using an env variable in a sync environment:
async def send_async():
    async with postmark.ServerClient(SERVER_TOKEN) as client:
        response = await client.outbound.send(
            postmark.Email(
                sender=SENDER,
                to=TO,
                subject="Hello from postmark-python",
                text_body="It works! This email was sent with the async client.",
                html_body="<p>It works! This email was sent with the <strong>async</strong> client.</p>",
            )
        )
    print(f"[async] sent — message_id={response.message_id}")


# Here's how to use it in an async production environment:
async def send_async_production():
    """
    Same send, with the error handling you'd want in production.
    Each exception type tells you something different about what went wrong
    and what to do next.
    """
    try:
        async with postmark.ServerClient(SERVER_TOKEN) as client:
            response = await client.outbound.send(
                postmark.Email(
                    sender=SENDER,
                    to=TO,
                    subject="Hello from postmark-python",
                    text_body="It works!",
                )
            )
        print(f"[async] sent — message_id={response.message_id}")

    except InvalidEmailException as e:
        # Pydantic rejected the Email object before it reached the API.
        # Fix the field values in your code; this is never a transient error.
        print(f"[async] bad email data: {e}")

    except InvalidAPIKeyException as e:
        # Wrong or missing server token. This is a configuration problem —
        # alert loudly and stop retrying.
        print(f"[async] invalid API key (check SERVER_TOKEN): {e}")

    except InactiveRecipientException as e:
        # Postmark rejected the address because it previously bounced or
        # unsubscribed. Remove it from your send list.
        print(f"[async] inactive recipient(s): {e.inactive_recipients}")

    except ValidationException as e:
        # The API rejected the request (e.g. missing required field, illegal
        # attachment type). Usually a bug in the calling code.
        print(
            f"[async] validation error [{e.error_code}]: {e}  request_id={e.request_id}"
        )

    except RateLimitException as e:
        # The SDK already retried. Back off and queue the message for later.
        print(f"[async] rate limit hit after retries: {e}  request_id={e.request_id}")

    except TimeoutException as e:
        # The SDK already retried. Treat as transient; try again later.
        print(f"[async] timed out after retries: {e}")

    except ServerException as e:
        # Postmark 5xx. Transient — retry later.
        print(f"[async] Postmark server error: {e}  request_id={e.request_id}")

    except PostmarkAPIException as e:
        # Catch-all for any other API error with an HTTP status.
        print(
            f"[async] API error [{e.error_code}] HTTP {e.http_status}: {e}  request_id={e.request_id}"
        )

    except PostmarkException as e:
        # Catch-all for SDK-level errors that aren't API responses.
        print(f"[async] SDK error: {e}")


# ── Sync version ──────────────────────────────────────────────────────────────


# Here's a stripped-down version of using an env variable for making non-async calls:
def send_sync():
    with postmark.sync.ServerClient(SERVER_TOKEN) as client:
        response = client.outbound.send(
            postmark.Email(
                sender=SENDER,
                to=TO,
                subject="Hello from postmark-python",
                text_body="It works! This email was sent with the sync client.",
                html_body="<p>It works! This email was sent with the <strong>sync</strong> client.</p>",
            )
        )
    print(f"[sync]  sent — message_id={response.message_id}")


# Here's a more production-ready example of the above:
def send_sync_production():
    """
    Same send, with the error handling you'd want in production.
    Identical exception hierarchy to the async version.
    """
    try:
        with postmark.sync.ServerClient(SERVER_TOKEN) as client:
            response = client.outbound.send(
                postmark.Email(
                    sender=SENDER,
                    to=TO,
                    subject="Hello from postmark-python",
                    text_body="It works!",
                )
            )
        print(f"[sync]  sent — message_id={response.message_id}")

    except InvalidEmailException as e:
        print(f"[sync]  bad email data: {e}")

    except InvalidAPIKeyException as e:
        print(f"[sync]  invalid API key (check SERVER_TOKEN): {e}")

    except InactiveRecipientException as e:
        print(f"[sync]  inactive recipient(s): {e.inactive_recipients}")

    except ValidationException as e:
        print(
            f"[sync]  validation error [{e.error_code}]: {e}  request_id={e.request_id}"
        )

    except RateLimitException as e:
        print(f"[sync]  rate limit hit after retries: {e}  request_id={e.request_id}")

    except TimeoutException as e:
        print(f"[sync]  timed out after retries: {e}")

    except ServerException as e:
        print(f"[sync]  Postmark server error: {e}  request_id={e.request_id}")

    except PostmarkAPIException as e:
        print(
            f"[sync]  API error [{e.error_code}] HTTP {e.http_status}: {e}  request_id={e.request_id}"
        )

    except PostmarkException as e:
        print(f"[sync]  SDK error: {e}")


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Bare send — minimal, no error handling.
    asyncio.run(send_async())  # SEND ASYNC NO ERROR HANDLING
    send_sync()  # SEND NON-ASYNC, NO ERROR HANDLING

    print()

    # Production-style send — same operation, full exception handling.
    asyncio.run(send_async_production())  # SEND ASYNC
    send_sync_production()  # SEND NON-ASYNC
