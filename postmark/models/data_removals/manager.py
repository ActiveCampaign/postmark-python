from postmark.utils.types import HTTPClient

from .schemas import DataRemoval


class DataRemovalManager:
    def __init__(self, client: HTTPClient):
        self.client = client

    async def create(
        self,
        requested_by: str,
        requested_for: str,
        notify_when_completed: bool = False,
    ) -> DataRemoval:
        response = await self.client.post(
            "/data-removals",
            json={
                "RequestedBy": requested_by,
                "RequestedFor": requested_for,
                "NotifyWhenCompleted": notify_when_completed,
            },
        )
        return DataRemoval(**response.json())

    async def get(self, removal_id: int) -> DataRemoval:
        response = await self.client.get(f"/data-removals/{removal_id}")
        return DataRemoval(**response.json())
