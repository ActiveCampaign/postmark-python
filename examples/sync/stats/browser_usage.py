from datetime import date

import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.stats.browser_usage(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print("Browser totals:")
    for browser, count in result.model_extra.items():
        print(f"  {browser}: {count}")
    print()

    for day in result.days:
        date_str = day.pop("Date", "?")
        print(f"  {date_str}: {day}")
