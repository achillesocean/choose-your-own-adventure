when you post to your endpoint to try and create a story, what you get back is a job_id and the status of that job!?
--so the story creating endpoint registers a job, gives it its own story_id, then calls to the LLM?
---then do we await it or does its corresponding job watch it for us?
we have the LLM generate us a complete story, that means its branches all the way to the end
an option is just a child node
? how will you modularize your entities?
? what will your pydantic models look like?
? how did he know that the parser would parse his models like the json, or did he know the json beforehand? or was it enough to know the best representation of a tree using json?
