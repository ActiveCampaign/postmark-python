from pydantic import BaseModel, ConfigDict, Field


class DataRemoval(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="ID")
    status: str = Field(alias="Status")
