from pydantic import BaseModel
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from src.rag_pipeline import generate_answer, simple_llm_call
from agents.agent import agent_call
from agents.table_expert_agent import TabularDataExpertAgent
from agents.medical_data_expert_agent import MedicalDataExpertAgent

from agents.query_router_agent import QueryRouterAgent

class QueryRequest(BaseModel):
    message: str

router = APIRouter()

@router.post("/test")
async def chat(request: QueryRequest):
    print('User input received -> ', request.message)
    return {"response": request.message}


@router.post("/echo")
async def chat(request: QueryRequest):
    data = await request.json()
    user_message = data.get("message", "")
    response_message = f"Echo: {user_message}"
    return {"response": response_message}

@router.post("/rag_chat")
async def ask_rag(request: Request, query: QueryRequest):
    embedder = request.app.state.embedder
    vectorstore = request.app.state.vectorstore
    llm = request.app.state.llm

    response = generate_answer(
        question=query.message,
        embedder=embedder,
        vectorstore=vectorstore,
        llm=llm
    )
    print(response)
    return {"response": response}

@router.post("/chat")
def ask_rag(request: Request, query: QueryRequest):
    llm = request.app.state.llm
    stream = False
    if stream:
        # Get generator
        token_generator = simple_llm_call(
            question=query.message,
            llm=llm,
            stream=True)
        return StreamingResponse(
            (token for token in token_generator),
            media_type="text/plain")
    else:
        response = simple_llm_call(
            question=query.message,
            llm=llm,
            stream=False)
        return JSONResponse(content={"response": response})

@router.post("/agent_old")
def agent(request: Request, query: QueryRequest):
    llm = request.app.state.llm
    response = agent_call(
        question=query.message,
        llm=llm)
    return JSONResponse(content={"response": response})

@router.post("/agent")
def agent(request: Request, query: QueryRequest):
    llm = request.app.state.llm
    agent = QueryRouterAgent(llm=llm)
    response = agent.run(user_query=query.message)
    return JSONResponse(content={"response": response})