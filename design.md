# SD Design

## Env Variables
```
POSTMARK_SERVER_TOKEN     = 'server-key-here'
POSTMARK_SENDER_EMAIL     = 'you@example.com'
POSTMARK_TEST_MODE   = [True/False]
POSTMARK_TRACK_OPENS = [True/False]
POSTMARK_LOG_LEVEL = [1/2/3]
```

## Usage

```
>>> from postmark import PostmarkClient
>>> postmark_server_ONE = PostmarkClient(server_token="EXAMPLE_SERVER_TOKEN_ONE")
>>> postmark_server_TWO = PostmarkClient(server_token="EXAMPLE_SERVER_TOKEN_TWO")
>>> postmark_server_ONE.emails.send(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    ...
)
>>> postmark_server_TWO.emails.send(
    From='sender@example.com',
    To='receiver@example.com',
    Subject='Postmark test',
    ...
)
```





### Questions:
1. Multiple Server Tokens, but only one Account Token?
2. What are the core objects?
    - Emails
    - Messages
    - Templates
    - Messages
    - Domains