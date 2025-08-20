from sqlalchemy.orm import Session
from core.config import settings

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
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

    cls._process_story_node(db, story_db.id, root_node_data, is_root=True)
    # notice how we're passing the same db session to the processor as we are using in this generate_story func.
    db.commit()
    return story_db
  
  #we're gonna write the class method for processing the llm's json return into the necessary pydantic class, but what had we been doing, isn't it the same?

  @classmethod
  def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
    node = StoryNode(
      story_id=story_id,
      content=node_data.content if hasattr(node_data, "content") else node_data["content"],
      is_root=is_root,
      is_ending=node_data.isEnding if hasattr(node_data, "isEnding") else node_data["isEnding"],
      is_winning_ending=node_data.isWinningEnding if hasattr(node_data, "isWinningEnding") else node_data["isWinningEnding"],
      options=[]
    )
    db.add(node)
    db.flush

    if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
      options_list = []
      # if so, process the options returned from the llm and store them as nodes in our database.
      for option_data in node_data.options:
        next_node = option_data.nextNode # each option is meant to have a next node?
        # validate that it's correct if this next node is a dictionary
        if isinstance(next_node, dict):
          next_node = StoryNodeLLM.model_validate(next_node)    
        
        child_node = cls._process_story_node(db, story_id, next_node, is_root=False)

        options_list.append({
          "text": option_data.text,
          "node_id": child_node.id
        })

      node.options = options_list

    db.flush()
    return node