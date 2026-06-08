from datetime import date

import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.stats.browser_platform_usage(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print("Browser platform totals:")
    print(f"  Desktop: {result.desktop}")
    print(f"  Mobile:  {result.mobile}")
    print(f"  Unknown: {result.unknown}")
    print()

    for day in result.days:
        print(f"  {day.date}:  desktop={day.desktop}  mobile={day.mobile}")
