# modes/story.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class Story(Base):
  __tablename__ = "stories"

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String, index=True)
  session_id = Column(String, index=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())

  nodes = relationship(argument="StoryNode", back_populates="story") # explain

# this relationship is actually a two-way .
# Story.nodes gives you a list of all StoryNode s for a story, StoryNode.story gives the Story object that owns the node. notice how you do class.relationship

class StoryNode(Base):
  __tablename__ = "story_nodes"

  id = Column(Integer, primary_key=True, index=True)
  story_id = Column(Integer, ForeignKey("stories.id"), index=True)
  content = Column(String)
  is_root  = Column(Boolean, default=False)
  is_ending = Column(Boolean, default=False)
  is_winning_ending = Column(Boolean, default=False)
  options = Column(JSON, default=list) # explain! 
  # what this stores? -- options_list.append({
  #  "text": option_data.text, 
  #  "node_id": child_node.id
  #  })

  story = relationship(argument="Story", back_populates="nodes") # explain
  