from datetime import date

import postmark

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    result = server.stats.bounce_counts(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31),
    )

    print("Bounce totals:")
    print(f"  Hard bounces:    {result.hard_bounce}")
    print(f"  Soft bounces:    {result.soft_bounce}")
    print(f"  SMTP API errors: {result.smtp_api_error}")
    print(f"  Transient:       {result.transient}")
    print()

    for day in result.days:
        print(f"  {day.date}:  hard={day.hard_bounce}  soft={day.soft_bounce}")
