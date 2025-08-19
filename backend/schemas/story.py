# I wonder if pydantic schema models files import their attributes from sqlalchemy as theres duplication between the two 
# no. because here you're using pydantic's basemodel to inherit from, and using python data attributes, not sql and creating columns
from datetime import datetime
from pydantic import BaseModel

class StoryOptionsSchema(BaseModel):
  text: str
  node_id: int | None = None

class StoryNodeBase(BaseModel):
  content: str
  is_ending: bool = False
  is_winning_ending: bool = False

class CompleteStoryNodeResponse(StoryNodeBase):
  id: int
  options: list[StoryOptionsSchema] = []

  class Config:
    from_attributes = True

class StoryBase(BaseModel):
  title: str
  session_id: str | None = None

  class Config:
    from_attributes = True

class CreateStoryRequest(BaseModel):
  theme: str

class CompleteStoryResponse(StoryBase):
  id: int
  created_at: datetime
  root_node: CompleteStoryNodeResponse
  all_nodes: dict[int, CompleteStoryNodeResponse]

  class Config:
    from_attributes = True