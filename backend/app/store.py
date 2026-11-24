
import json
from pathlib import Path
from threading import Lock
from uuid import uuid4
from datetime import datetime, timezone

DATA_DIR = Path(__file__).parent / "data"
APPOINTMENTS_FILE = DATA_DIR / "appointments.json"

_file_lock = Lock()


def load_json(filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Missing data file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_doctors():
    return load_json("doctors.json")


def get_clinic_info():
    return load_json("clinic_info.json")


def get_faqs():
    return load_json("faqs.json")


def save_appointment(patient_name, phone, doctor_id, date, time):
    with _file_lock:
        if APPOINTMENTS_FILE.exists():
            with APPOINTMENTS_FILE.open("r", encoding="utf-8") as file:
                appointments = json.load(file)
        else:
            appointments = []

        appointment = {
            "id": str(uuid4()),
            "patient_name": patient_name,
            "phone": phone,
            "doctor_id": doctor_id,
            "date": date,
            "time": time,
            "status": "requested",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        appointments.append(appointment)

        APPOINTMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

        with APPOINTMENTS_FILE.open("w", encoding="utf-8") as file:
            json.dump(appointments, file, indent=4)

        return appointment


def get_appointments():
    if not APPOINTMENTS_FILE.exists():
        return []

    with _file_lock:
        with APPOINTMENTS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
