import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.stats.read_times()

    print("Read-time distribution (totals):")
    for bucket, count in result.model_extra.items():
        print(f"  {bucket}: {count}")

    print(f"\nDaily breakdown ({len(result.days)} day(s)):")
    for day in result.days:
        print(f"  {day}")
