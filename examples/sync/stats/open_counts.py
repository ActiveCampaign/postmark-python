from datetime import date

import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.stats.open_counts(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print(f"Total opens:  {result.opens}")
    print(f"Unique opens: {result.unique}")
    print()

    for day in result.days:
        print(f"  {day.date}:  opens={day.opens}  unique={day.unique}")
