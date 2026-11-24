
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from app.prompts import SYSTEM_PROMPT
from app.knowledge_base import get_knowledge_context


# Load environment variables from backend/.env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY missing. Check backend/.env")

MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

client = Groq(api_key=API_KEY)


def generate_response(message, conversation_history=None):

    conversation_history = conversation_history or []

    # Step 1: Get recent conversation history
    recent_history = conversation_history[-8:]

    previous_context = " ".join(
        item.get("text", "")
        for item in recent_history
        if item.get("role") in ("user", "model")
    )

    # Step 2: Retrieve relevant clinic information
    retrieval_query = previous_context + " " + message

    knowledge = get_knowledge_context(retrieval_query)

    # Step 3: Convert knowledge into readable JSON
    knowledge_json = json.dumps(
        knowledge,
        indent=2,
        ensure_ascii=False
    )

    # Step 4: Prepare messages for Groq
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Add recent conversation history
    for item in recent_history:

        role = item.get("role")
        text = item.get("text", "")

        if role == "user" and text.strip():
            messages.append({
                "role": "user",
                "content": text
            })

        elif role == "model" and text.strip():
            messages.append({
                "role": "assistant",
                "content": text
            })

    # Step 5: Add current message and retrieved clinic knowledge
    messages.append({
        "role": "user",
        "content": f"""
PATIENT'S CURRENT MESSAGE:
{message}

VERIFIED WARDLINE CLINIC KNOWLEDGE:
{knowledge_json}

INSTRUCTIONS:
1. Answer the patient's current question.
2. Use conversation history to understand follow-up questions.
3. Use verified clinic information wherever relevant.
4. Never invent missing clinic details.
5. Ask one question at a time when clarification is required.
6. Do not claim appointment availability or confirmation
   without verification.
7. Do not diagnose medical conditions or replace a doctor.
8. For emergencies, advise the patient to seek immediate
   medical attention.
"""
    })

    # Step 6: Generate response using Groq
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.4,
            max_tokens=800
        )

        answer = response.choices[0].message.content

        return answer or "Sorry, could you repeat that?"

    except Exception as error:
        print("GROQ API ERROR:", str(error))
        raise
