from sqlalchemy.orm import Session
from core.config import settings

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from core.prompts import STORY_PROMPT
from models.story import Story
from core.models import StoryLLMResponse, StoryNodeLLM

class StoryGenerator:

  @classmethod
  def _get_llm(cls):
    return ChatOpenAI(models="gpt-4-turbo")
  
  @classmethod
  def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy") -> Story:
    llm = cls._get_llm()
    story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

    prompt = ChatPromptTemplate.from_messages([
      (
        "system",
        STORY_PROMPT
      ),
      (
        "human",
        f"Create the story with this theme: {theme}"
      )
    ]).partial(format_instructions=story_parser.get_format_instructions())

    raw_response = llm.invoke(prompt.invoke({}))

    response_text = raw_response
    if hasattr(raw_response, "content"):
      response_text = raw_response.content

    story_structure = story_parser.parse(response_text) 
    # till now, we will be able to confirm correct format and pass it into the correct python object--which I think is StoryLLMResponse.

    story_db = Story(title=story_structure.title, session_id=session_id)
    db.add(story_db)
    db.flush() # this is gonna populate this story_db object with the auto-generated fields from the database

    root_node_data = story_structure.rootNode
    if isinstance(root_node_data, dict):
      root_node_data = StoryNodeLLM.model_validate(root_node_data)

    # TODO: process data
    db.commit()
    return story_db
  