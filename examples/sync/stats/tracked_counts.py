from datetime import date

import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.stats.tracked_counts(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print(f"Total tracked emails: {result.tracked}")
    print()

    for day in result.days:
        print(f"  {day.date}:  tracked={day.tracked}")
