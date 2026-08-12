"""
Add this to your Django project's settings.py to send mail through Postmark.

Requires the `django` extra: pip install postmark-python[django]
"""

EMAIL_BACKEND = "postmark.django.EmailBackend"

POSTMARK_SERVER_TOKEN = "<YOUR POSTMARK SERVER TOKEN>"

# Optional settings (all default to off/unset):
POSTMARK_TEST_MODE = (
    False  # When True, sends with Postmark's POSTMARK_API_TEST token instead
)
POSTMARK_TRACK_OPENS = (
    False  # Default TrackOpens for every message, unless overridden per-message
)
POSTMARK_MESSAGE_STREAM = (
    None  # e.g. "broadcasts" — default message stream, unless overridden per-message
)
