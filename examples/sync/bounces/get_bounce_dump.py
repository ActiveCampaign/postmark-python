import postmark

# Bounce ID must have "dump_available" -> True.
bounce_id = 692560173
# Postmark retains raw SMTP dumps for ~30 days after the bounce.

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as client:
    dump = client.bounces.get_dump(bounce_id)
    if dump.body:
        print(dump.body)
    else:
        print("Dump not available (may have expired after 30 days).")
