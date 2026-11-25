# Wardline – AI Voice Doctor Assistant

An AI-powered healthcare assistant that helps users explore doctors, get clinic information, ask healthcare-related questions, and request appointments through conversational text and voice interactions.

## 🌐 Live Demo

- **Frontend:** https://wardlinevoiceassisstant-frontend.vercel.app/
- **Backend API:** https://wardline-voice-assisstant-4.onrender.com/

## ✨ Features

- AI-powered conversational assistant
- Voice input for interacting with the assistant
- Doctor and specialist discovery
- Clinic information and FAQs
- Appointment request handling
- Responsive and interactive healthcare interface

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| HTML | Frontend structure |
| CSS | Styling and responsive UI |
| JavaScript | Frontend interactions |
| Python | Backend development |
| FastAPI | REST API development |
| Groq API | AI-powered responses |
| Vercel | Frontend deployment |
| Render | Backend deployment |

## 📁 Project Structure

```text
wardline-voice-doctor-assistant/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── bot.py
│   │   ├── prompts.py
│   │   ├── store.py
│   │   └── knowledge_base.py
│   │
│   ├── data/
│   │   ├── doctors.json
│   │   ├── clinic_info.json
│   │   └── faqs.json
│   │
│   ├── requirements.txt
│   └── .env
│
└── README.md
```

## ⚙️ How to Run the Project Locally

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate into the project:

```bash
cd wardline-voice-doctor-assistant
```

### 2. Set Up the Backend

Navigate to the backend folder:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the backend folder.

Add your Groq API credentials:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Replace the placeholder with your own API key. Never upload your API key to GitHub.

### 4. Start the Backend Server

From the backend directory, execute:

```bash
uvicorn app.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

You can access the FastAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

### 5. Start the Frontend

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Start a local development server:

```bash
python -m http.server 5500
```

Open the application in your browser:

```text
http://localhost:5500
```

Make sure the frontend API configuration points to your local backend while testing locally.

## 🚀 Deployment

The application uses separate deployment services:

- **Frontend:** Deployed using Vercel.
- **Backend:** Deployed using Render.
- **AI integration:** Groq API.

For deployment, configure the required environment variables on Render and ensure the frontend's API base URL points to the deployed backend.

## 🔐 Security

- API keys are stored using environment variables.
- `.env` files should not be committed to GitHub.
- `.venv` and Python cache files should be excluded using `.gitignore`.

## 🎯 Project Objective

Wardline aims to make healthcare information and appointment assistance more accessible through an interactive AI-powered conversational interface.

---

**Developed as an AI-powered full-stack healthcare application.**
