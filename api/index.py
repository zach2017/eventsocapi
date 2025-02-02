from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Question(BaseModel):
    text: str

class Response(BaseModel):
    message: str

@app.post("/api/ask", response_model=Response)
async def ask_question(question: Question):
    if not question.text:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Here you would typically process the question or send it to another service
    # For now, we'll just return a simple response
    return Response(message="Working on it")

# Mangum handler to wrap the FastAPI app
handler = Mangum(app)

