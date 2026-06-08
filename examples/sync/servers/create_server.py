import postmark
from postmark.models.servers import DeliveryType, ServerColor

with postmark.sync.AccountClient("xxx-YOUR-ACCOUNT-TOKEN-xxxx-xxxxxxx") as account:
    server = account.server.create(
        name="My New Server",
        color=ServerColor.BLUE,
        delivery_type=DeliveryType.SANDBOX,
        track_opens=True,
    )

    print("Created server:")
    print(f"  ID:            {server.id}")
    print(f"  Name:          {server.name}")
    print(f"  Color:         {server.color.value}")
    print(f"  Delivery type: {server.delivery_type.value}")
    print(f"  Inbound address: {server.inbound_address}")
