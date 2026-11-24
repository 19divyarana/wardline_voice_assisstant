
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from app.store import (
    get_doctors,
    get_clinic_info,
    get_faqs
)

from app.tools import (
    find_doctor,
    request_appointment
)

from app.bot import generate_response


app = FastAPI(
    title="Wardline Voice Doctor Assistant",
    description="Conversational AI assistant for clinic information",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Temporary in-memory conversation history.
# Replace with persistent session storage for production.
conversation_sessions = {}


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


class AppointmentRequest(BaseModel):
    patient_name: str
    phone: str
    doctor_id: str
    appointment_date: str
    appointment_time: str


class DoctorSearchRequest(BaseModel):
    specialization: Optional[str] = None
    language: Optional[str] = None
    max_fee: Optional[int] = Field(default=None, ge=0)


@app.get("/")
def home():
    return {
        "message": "Welcome to Wardline Voice Doctor Assistant",
        "status": "active"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/doctors")
def doctors():
    return get_doctors()


@app.get("/clinic")
def clinic():
    return get_clinic_info()


@app.get("/faqs")
def faqs():
    return get_faqs()


@app.post("/doctors/search")
def doctor_search(request: DoctorSearchRequest):
    return find_doctor(
        specialization=request.specialization,
        language=request.language,
        max_fee=request.max_fee
    )


@app.post("/chat")
def chat(request: ChatRequest):
    session_id = request.session_id
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    history = conversation_sessions.get(session_id, [])

    try:
        answer = generate_response(message, history)

        history.append({
            "role": "user",
            "text": message
        })

        history.append({
            "role": "model",
            "text": answer
        })

        conversation_sessions[session_id] = history[-24:]

        return {
            "session_id": session_id,
            "user_message": message,
            "response": answer
        }

    except Exception as error:
     print("GEMINI ERROR:", str(error))

    raise HTTPException(
        status_code=503,
        detail="Wardline AI is temporarily unavailable. Please try again shortly."
    )


@app.post("/appointments")
def appointments(request: AppointmentRequest):
    try:
        return request_appointment(
            patient_name=request.patient_name,
            phone=request.phone,
            doctor_id=request.doctor_id,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.post("/reset-session/{session_id}")
def reset_session(session_id: str):
    conversation_sessions.pop(session_id, None)

    return {
        "success": True,
        "message": "Conversation session reset."
    }
