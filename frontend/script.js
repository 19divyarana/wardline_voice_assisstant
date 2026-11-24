
const API_BASE = "https://wardline-voice-assisstant-app.onrender.com";

const doctorGrid = document.getElementById("doctorGrid");
const doctorSearch = document.getElementById("doctorSearch");
const specialtyFilter = document.getElementById("specialtyFilter");
const bookingDoctor = document.getElementById("bookingDoctor");

let doctors = [];
const sessionId = "wardline-" + Math.random().toString(36).slice(2, 10);

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }

  return response.json();
}

function getDoctorName(doctor) {
  return doctor.name || doctor.doctor_name || doctor.full_name || "Doctor";
}

function getDoctorId(doctor) {
  return doctor.doctor_id || doctor.id || doctor.doc_id || "";
}

function getSpecialty(doctor) {
  return doctor.specialization || doctor.specialty || doctor.department || "Specialist";
}

function getExperience(doctor) {
  const years = doctor.experience_years ?? doctor.experience ?? "";
  return years ? `${years} years experience` : "Experienced specialist";
}

function getFee(doctor) {
  const fee = doctor.consultation_fee ?? doctor.fee ?? doctor.consultation_charge;
  return fee !== undefined && fee !== null ? `₹${fee} consultation` : "Contact clinic for fee";
}

function getAvailability(doctor) {
  const days = doctor.available_days || doctor.working_days;
  if (Array.isArray(days)) return days.join(", ");
  return days || "Contact clinic for availability";
}

function normalizeDoctors(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.doctors)) return data.doctors;
  return [];
}

async function loadDoctors() {
  try {
    const data = await apiRequest("/doctors");
    doctors = normalizeDoctors(data);
    renderDoctors(doctors);
    populateBookingDoctors();
  } catch (error) {
    doctorGrid.innerHTML = `
      <p class="loading-text">
        Unable to load doctors. Please check whether the backend is running.
      </p>`;
    console.error("Doctor loading error:", error);
  }
}

function renderDoctors(list) {
  if (!list.length) {
    doctorGrid.innerHTML = `<p class="loading-text">No matching doctors found.</p>`;
    return;
  }

  doctorGrid.innerHTML = list.map((doctor, index) => `
    <article class="doctor-card">
      <div class="doctor-avatar">✚</div>
      <h3>${escapeHTML(getDoctorName(doctor))}</h3>
      <div class="doctor-specialty">${escapeHTML(getSpecialty(doctor))}</div>
      <div class="doctor-meta">
        ${escapeHTML(getExperience(doctor))}<br>
        ${escapeHTML(getFee(doctor))}<br>
        Available: ${escapeHTML(getAvailability(doctor))}
      </div>
      <button type="button" data-doctor-index="${index}">Request appointment ↗</button>
    </article>
  `).join("");

  doctorGrid.querySelectorAll("[data-doctor-index]").forEach(button => {
    button.addEventListener("click", () => {
      const doctor = list[Number(button.dataset.doctorIndex)];
      bookingDoctor.value = getDoctorId(doctor);
      document.getElementById("booking").scrollIntoView({ behavior: "smooth" });
    });
  });
}

function populateBookingDoctors() {
  bookingDoctor.innerHTML = `<option value="">Select a specialist</option>`;

  doctors.forEach(doctor => {
    const option = document.createElement("option");
    option.value = getDoctorId(doctor);
    option.textContent = `${getDoctorName(doctor)} — ${getSpecialty(doctor)}`;
    bookingDoctor.appendChild(option);
  });
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[character]);
}

function filterDoctors() {
  const query = doctorSearch.value.toLowerCase().trim();
  const specialty = specialtyFilter.value.toLowerCase();

  const filtered = doctors.filter(doctor => {
    const searchable = [
      getDoctorName(doctor),
      getSpecialty(doctor),
      getAvailability(doctor)
    ].join(" ").toLowerCase();

    const matchesQuery = searchable.includes(query);
    const matchesSpecialty = !specialty ||
      getSpecialty(doctor).toLowerCase().includes(specialty);

    return matchesQuery && matchesSpecialty;
  });

  renderDoctors(filtered);
}

doctorSearch.addEventListener("input", filterDoctors);
specialtyFilter.addEventListener("change", filterDoctors);


// ---------------- AI CHAT ----------------

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendButton = document.getElementById("sendButton");
const micButton = document.getElementById("micButton");

function addMessage(text, type) {
  const message = document.createElement("div");
  message.className = `message ${type}-message`;
  message.textContent = text;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function cleanTextForSpeech(text) {
  return text
    .replace(/```[\s\S]*?```/g, "Code block omitted.")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/__(.*?)__/g, "$1")
    .replace(/_(.*?)_/g, "$1")
    .replace(/#{1,6}\s*/g, "")
    .replace(/^\s*[-*]\s+/gm, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/[•*_#]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;

  window.speechSynthesis.cancel();

  const cleanText = cleanTextForSpeech(text);
  if (!cleanText) return;

  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = "en-IN";
  utterance.rate = 1;
  utterance.pitch = 1;

  window.speechSynthesis.speak(utterance);
}

async function sendMessage(message) {
  const cleanMessage = message.trim();
  if (!cleanMessage) return;

  addMessage(cleanMessage, "user");
  chatInput.value = "";
  sendButton.disabled = true;
  addMessage("Thinking...", "bot");

  const thinkingMessage = chatMessages.lastElementChild;

  try {
    const data = await apiRequest("/chat", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        message: cleanMessage
      })
    });

    const reply = data.response || data.answer || data.message ||
      "I could not generate a response. Please try again.";

    thinkingMessage.textContent = reply;
    speak(reply);
  } catch (error) {
    thinkingMessage.textContent =
      "I'm having trouble connecting right now. Please check the backend and try again.";
    console.error("Chat error:", error);
  } finally {
    sendButton.disabled = false;
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

sendButton.addEventListener("click", () => sendMessage(chatInput.value));

chatInput.addEventListener("keydown", event => {
  if (event.key === "Enter") sendMessage(chatInput.value);
});

document.querySelectorAll(".suggestion").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.textContent));
});

document.getElementById("clearChat").addEventListener("click", async () => {
  window.speechSynthesis?.cancel();
  chatMessages.innerHTML = "";

  try {
    await apiRequest(`/reset-session/${sessionId}`, { method: "POST" });
  } catch (error) {
    console.warn("Session reset endpoint unavailable:", error);
  }

  addMessage("Your conversation has been reset. How can I help you?", "bot");
});


// ---------------- VOICE INPUT ----------------

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.interimResults = false;
  recognition.continuous = false;

  micButton.addEventListener("click", () => {
    try {
      recognition.start();
      micButton.classList.add("listening");
    } catch (error) {
      console.warn("Voice recognition could not start:", error);
    }
  });

  recognition.onresult = event => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = transcript;
    sendMessage(transcript);
  };

  recognition.onend = () => micButton.classList.remove("listening");
  recognition.onerror = () => micButton.classList.remove("listening");
} else {
  micButton.disabled = true;
  micButton.title = "Voice recognition is not supported in this browser";
}


// ---------------- APPOINTMENT BOOKING ----------------

const bookingForm = document.getElementById("bookingForm");
const bookingStatus = document.getElementById("bookingStatus");

const dateInput = document.getElementById("appointmentDate");
dateInput.min = new Date().toISOString().split("T")[0];

bookingForm.addEventListener("submit", async event => {
  event.preventDefault();

  const formData = new FormData(bookingForm);

  const appointment = {
    patient_name: formData.get("patient_name"),
    phone: formData.get("phone"),
    doctor_id: formData.get("doctor_id"),
    appointment_date: formData.get("appointment_date"),
    appointment_time: formData.get("appointment_time")
  };

  bookingStatus.textContent = "Submitting your appointment request...";

  try {
    const result = await apiRequest("/appointments", {
      method: "POST",
      body: JSON.stringify(appointment)
    });

    bookingStatus.textContent =
      result.message || "Your appointment request has been submitted successfully.";

    bookingForm.reset();
    dateInput.min = new Date().toISOString().split("T")[0];
  } catch (error) {
    bookingStatus.textContent =
      "Could not submit your request. Please check the backend and try again.";
    console.error("Booking error:", error);
  }
});


// ---------------- CLINIC INFORMATION ----------------

async function loadClinic() {
  try {
    const data = await apiRequest("/clinic");
    console.log("Wardline clinic information:", data);
  } catch (error) {
    console.warn("Clinic information could not be loaded:", error);
  }
}

loadDoctors();
loadClinic();
