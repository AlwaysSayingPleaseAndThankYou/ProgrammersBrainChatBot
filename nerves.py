from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from brain import agent_executor
from pydantic import BaseModel
# import panel as pn
# import time
#
# # Global list to store chat history
# chat_history = []
#
#
# def chatbot_response(user_input):
#     # Simple echo chatbot for demonstration
#     return agent_executor.run(user_input)
#
#
# def update_chat(event):
#     # Show loading animation
#     chat_history.append('<div class="loader"></div>')
#     chat_display.object = '\n'.join(chat_history)
#
#     # Get user message from text input
#     user_input = text_input.value
#     chat_history.pop()  # Remove loader
#     chat_history.append(f"<div class='user-msg'>You: {user_input}</div>")
#
#     # Get chatbot response
#     response = chatbot_response(user_input)
#     chat_history.append(f"<div class='bot-msg'>Bot: {response}</div>")
#
#     # Update chat display
#     chat_content = '\n'.join(chat_history)
#     chat_display.object = f"""
# <style>
# .user-msg, .bot-msg {{
#     display: inline-block;
#     padding: 5px 10px;
#     border-radius: 8px;
#     margin: 3px 5px;
# }}
# .user-msg {{
#     text-align: right;
#     background-color: #cce5ff;
# }}
# .bot-msg {{
#     text-align: left;
#     background-color: #d4d4d4;
# }}
# .loader {{
#     border: 5px solid #f3f3f3;
#     border-top: 5px solid #3498db;
#     border-radius: 50%;
#     width: 30px;
#     height: 30px;
#     animation: spin 2s linear infinite;
#     margin: 0 auto;
# }}
# @keyframes spin {{
#     0% {{ transform: rotate(0deg); }}
#     100% {{ transform: rotate(360deg); }}
# }}
# </style>
# <div>
# {chat_content}
# </div>
# """
#     text_input.value = ""  # Clear input
#
#
# # Create a text input widget with a button to submit
# text_input = pn.widgets.TextInput(width=400, placeholder="Type a message...")
# submit_button = pn.widgets.Button(name="Submit", button_type="primary", width=100)
# submit_button.on_click(update_chat)
#
# # Create a display for chat history
# chat_display = pn.pane.Markdown("", width=500, height=400, margin=(10, 25))
#
# # Combine input and button into a single row
# input_row = pn.Row(text_input, submit_button, align="center", width=500)
#
# # Arrange widgets in a layout
# layout = pn.Column(
#     chat_display,
#     input_row,
#     align="center",
#     background="#f5f5f5",
#     sizing_mode="stretch_both",
#     width_policy="max",
# )
#
# layout.servable()
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
