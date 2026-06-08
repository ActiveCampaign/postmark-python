from datetime import date

import postmark
from postmark.models.suppressions import SuppressionReason

with postmark.sync.ServerClient("xxx-YOUR-SERVER-TOKEN-xxxx-xxxxxxx") as server:
    suppressions = server.suppressions.dump(
        "outbound",
        suppression_reason=SuppressionReason.HARD_BOUNCE,
        from_date=date(2024, 1, 1),
    )

    print(f"Total suppressions: {len(suppressions)}")
    print()

    for s in suppressions:
        print(f"  {s.email_address}")
        print(f"       Reason:  {s.suppression_reason.value}")
        print(f"       Origin:  {s.origin.value}")
        print(f"       Created: {s.created_at}")
        print("----------------------------------------")
