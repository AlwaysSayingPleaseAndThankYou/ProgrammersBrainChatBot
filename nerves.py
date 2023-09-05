from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from brain import agent_executor
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Question(BaseModel):
    question: str


@app.get("/")
def read_template(request: Request):
    return templates.TemplateResponse("chat_template.html", {"request": request})


@app.post("/ask")
async def ask_bot(question: str):
    return {"answer": agent_executor.run(question)}
