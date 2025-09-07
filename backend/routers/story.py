import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import CompleteStoryNodeResponse, CompleteStoryResponse, CreateStoryRequest
from schemas.job import StoryJobResponse

from core.story_generator import StoryGenerator # this is a class, remember
router = APIRouter(
  prefix="/story",
  tags=["stories"]
)

def get_session_id(session_id: str | None = Cookie(None)):
  if session_id is None:
    session_id = str(uuid.uuid4())
  return session_id

@router.post("/create", response_model=StoryJobResponse) # how come we respond with a StoryJobResponse for a create_story route?
def create_story(
  request: CreateStoryRequest,
  background_tasks: BackgroundTasks,
  response: Response, # what is this, how is it a query parameter, who is gonna pass it in?
  session_id: str = Depends(get_session_id), # does this just call the func to generate a session id?
  db: Session = Depends(get_db)
):
  response.set_cookie(key="session_id", value=session_id, httponly=True)# explain this

  job_id = str(uuid.uuid4())

  job = StoryJob(
    job_id=job_id,
    session_id=session_id,
    theme=request.theme,
    status="pending"
  )
  db.add(job)
  db.commit()
  # notice that this job can be found within the database before the background task is finished

  background_tasks.add_task(generate_story_task, job_id, request.theme, session_id)
  # what does the add_task method do with these arguments? they're the same arguments as the parameter of generate_story_task.
  return job

def generate_story_task(job_id: str, theme: str, session_id: str):
  db = SessionLocal()

  # with this nested try block, we make sure that the database connection is closed even if an exception is raised
  try:
    job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

    if not job: return

    try:
      job.status = "processing"
      db.commit() # is this really necessary?

      story = StoryGenerator.generate_story(db, session_id, theme) # this only returns the story id and root node, so you still have to create the tree

      job.story_id = story.id
      job.status = "completed"
      job.completed_at = datetime.now()
      db.commit()
    except Exception as e:
      job.status = "failed"
      job.completed_at = datetime.now()
      job.error = str(e)
      db.commit()

  finally:
    db.close()


@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
  # how come this endpoint accepts a db session, because it's not called anywhere else? does it have something to do with dependency injection?
  story = db.query(Story).filter(Story.id == story_id).first()
  if not story:
    raise HTTPException(status_code=404, detail="Story not found")
  
  # parse the story
  complete_story = build_complete_story_tree(db, story)

  return complete_story

def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse:
  # we collect all the nodes created by the generator, all the ones that reference this story, build the tree, which is returned to the frontend
  nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()

  node_dict = {}
  for node in nodes:
    # node as is a type of StoryNode, right, so why do we need to convert it to a CompleteStoryNodeResponse?
    node_response = CompleteStoryNodeResponse(
      id=node.id,
      content=node.content,
      is_ending=node.is_ending,
      is_winning_ending=node,
      options=node.options
    )
    node_dict[node.id] = node_response

  root_node = next((node for node in nodes if node.is_root), None)
  if not root_node:
    raise HTTPException(status_code=500, detail="Story root node not found")
  
  return CompleteStoryResponse(
    id=story.id,
    title=story.title,
    session_id=story.session_id,
    created_at=story.created_at,
    root_node=node_dict[root_node.id],
    all_nodes=node_dict
  )
# so this doesn't actually build the tree? it provides the story, root node, and all related nodes. I guess that is all you need from the backend