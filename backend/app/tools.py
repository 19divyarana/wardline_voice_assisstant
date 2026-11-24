
from datetime import date
from app.store import (
    get_doctors,
    get_clinic_info,
    save_appointment
)
from app.knowledge_base import search_doctors, search_faqs


def find_doctor(
    specialization=None,
    language=None,
    max_fee=None
):
    results = []

    for doctor in get_doctors():
        if not doctor.get("active", False):
            continue

        if specialization:
            if specialization.lower() not in doctor["specialization"].lower():
                continue

        if language:
            if language.lower() not in [
                item.lower() for item in doctor["languages"]
            ]:
                continue

        if max_fee is not None:
            if doctor["consultation_fee"] > max_fee:
                continue

        results.append(doctor)

    return results


def get_doctor_details(doctor_id):
    for doctor in get_doctors():
        if doctor["id"] == doctor_id:
            return doctor

    return None


def get_clinic_details():
    return get_clinic_info()


def answer_faq(question):
    results = search_faqs(question)

    if not results:
        return {
            "found": False,
            "message": "I couldn't find verified information for that question. Please contact clinic reception."
        }

    return {
        "found": True,
        "results": results
    }


def request_appointment(
    patient_name,
    phone,
    doctor_id,
    appointment_date,
    appointment_time
):
    if not patient_name.strip():
        raise ValueError("Patient name is required.")

    digits = "".join(ch for ch in phone if ch.isdigit())

    if len(digits) < 10 or len(digits) > 15:
        raise ValueError("Please provide a valid phone number.")

    doctor = get_doctor_details(doctor_id)

    if not doctor:
        raise ValueError("Doctor not found.")

    try:
        selected_date = date.fromisoformat(appointment_date)
    except ValueError:
        raise ValueError("Use YYYY-MM-DD for the appointment date.")

    if selected_date < date.today():
        raise ValueError("Appointment date cannot be in the past.")

    appointment = save_appointment(
        patient_name=patient_name.strip(),
        phone=phone.strip(),
        doctor_id=doctor_id,
        date=appointment_date,
        time=appointment_time
    )

    return {
        "success": True,
        "message": "Your appointment request has been submitted. It is not confirmed yet. Clinic reception must verify availability.",
        "appointment": appointment
    }
