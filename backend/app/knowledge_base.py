
import re


SYNONYMS = {
    "heart": ["cardiology", "cardiologist", "cardiac"],
    "skin": ["dermatology", "dermatologist", "hair", "nail"],
    "itching": ["skin", "dermatology", "dermatologist"],
    "hair": ["skin", "dermatology", "dermatologist"],
    "bones": ["orthopedic", "orthopedics", "joint"],
    "joints": ["orthopedic", "orthopedics", "mobility"],
    "child": ["pediatrics", "pediatrician"],
    "baby": ["pediatrics", "pediatrician"],
    "women": ["gynecology", "gynecologist"],
    "pregnancy": ["gynecology", "gynecologist"],
    "general": ["general physician", "general medicine"],
    "online": ["online consultation", "virtual"],
    "telugu": ["telugu"],
    "hindi": ["hindi"],
    "english": ["english"]
}


def expand_query(query):
    words = normalize(query)
    expanded_words = set(words)

    for word in words:
        if word in SYNONYMS:
            for synonym in SYNONYMS[word]:
                expanded_words.update(normalize(synonym))

    return expanded_words

from app.store import (
    get_doctors,
    get_clinic_info,
    get_faqs
)


def normalize(text):
    return re.sub(
        r"[^a-z0-9\s]",
        " ",
        str(text).lower()
    ).split()


def search_doctors(query):
    query_words = expand_query(query)
    results = []

    for doctor in get_doctors():

        if not doctor.get("active", False):
            continue

        searchable_text = " ".join([
            doctor["name"],
            doctor["specialization"],
            doctor["qualifications"],
            doctor["description"],
            " ".join(doctor["languages"]),
            " ".join(doctor["availability"]),
            " ".join(doctor["appointment_mode"])
        ])

        doctor_words = set(normalize(searchable_text))
        score = len(query_words.intersection(doctor_words))

        if score > 0:
            results.append({
                "doctor": doctor,
                "score": score
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return [item["doctor"] for item in results[:5]]


def search_faqs(query):
    query_words = expand_query(query)
    results = []

    for faq in get_faqs():

        searchable_text = " ".join([
            faq["question"],
            faq["answer"],
            " ".join(faq.get("keywords", [])),
            faq["category"]
        ])

        faq_words = set(normalize(searchable_text))
        score = len(query_words.intersection(faq_words))

        if score > 0:
            results.append({
                "faq": faq,
                "score": score
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return [item["faq"] for item in results[:5]]


def get_knowledge_context(query):

    return {
        "clinic": get_clinic_info(),
        "matching_doctors": search_doctors(query),
        "matching_faqs": search_faqs(query)
    }


def get_all_knowledge():

    return {
        "clinic": get_clinic_info(),
        "doctors": get_doctors(),
        "faqs": get_faqs()
    }
