async function requestJSON(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
    }
    return data;
}

function pagePathEnds(path) {
    return window.location.pathname.endsWith(path);
}

function showMessage(message) {
    if (message) {
        alert(message);
    }
}

async function loadPatients() {
    const tbody = document.querySelector("#patients-table tbody");
    if (!tbody) return;

    const patients = await requestJSON("/patients/api");
    tbody.innerHTML = patients
        .map(
            (p) => `
            <tr>
                <td>${p.id}</td>
                <td>${p.name}</td>
                <td>${p.age}</td>
                <td>${p.gender}</td>
                <td>${p.phone}</td>
                <td>${p.disease}</td>
                <td><button class="danger-btn" onclick="deletePatient(${p.id})">Delete</button></td>
            </tr>
        `
        )
        .join("");
}

async function deletePatient(patientId) {
    if (!confirm("Delete this patient record?")) return;
    try {
        const data = await requestJSON(`/patients/api/${patientId}`, { method: "DELETE" });
        showMessage(data.message);
        await loadPatients();
    } catch (error) {
        showMessage(error.message);
    }
}

async function setupPatientPage() {
    const form = document.getElementById("patient-form");
    if (!form) return;

    await loadPatients();
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            name: document.getElementById("patient-name").value.trim(),
            age: document.getElementById("patient-age").value.trim(),
            gender: document.getElementById("patient-gender").value.trim(),
            phone: document.getElementById("patient-phone").value.trim(),
            disease: document.getElementById("patient-disease").value.trim(),
        };

        try {
            const data = await requestJSON("/patients/api", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            showMessage(data.message);
            form.reset();
            await loadPatients();
        } catch (error) {
            showMessage(error.message);
        }
    });
}

async function loadDoctors() {
    const tbody = document.querySelector("#doctors-table tbody");
    if (!tbody) return;
    const doctors = await requestJSON("/doctors/api");
    tbody.innerHTML = doctors
        .map(
            (d) => `
            <tr>
                <td>${d.id}</td>
                <td>${d.name}</td>
                <td>${d.specialization}</td>
                <td>${d.availability}</td>
            </tr>
        `
        )
        .join("");
}

async function setupDoctorPage() {
    const form = document.getElementById("doctor-form");
    if (!form) return;

    await loadDoctors();
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            name: document.getElementById("doctor-name").value.trim(),
            specialization: document.getElementById("doctor-specialization").value.trim(),
            availability: document.getElementById("doctor-availability").value.trim(),
        };
        try {
            const data = await requestJSON("/doctors/api", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            showMessage(data.message);
            form.reset();
            await loadDoctors();
        } catch (error) {
            showMessage(error.message);
        }
    });
}

async function loadAppointmentMeta() {
    const meta = await requestJSON("/appointments/api/meta");
    const patientSelect = document.getElementById("appointment-patient");
    const doctorSelect = document.getElementById("appointment-doctor");
    if (patientSelect) {
        patientSelect.innerHTML = `<option value="">Select Patient</option>${meta.patients
            .map((p) => `<option value="${p.id}">${p.name}</option>`)
            .join("")}`;
    }
    if (doctorSelect) {
        doctorSelect.innerHTML = `<option value="">Select Doctor</option>${meta.doctors
            .map((d) => `<option value="${d.id}">${d.name}</option>`)
            .join("")}`;
    }
}

async function loadAppointments() {
    const tbody = document.querySelector("#appointments-table tbody");
    const billAppointmentSelect = document.getElementById("bill-appointment");
    if (!tbody) return;

    const appointments = await requestJSON("/appointments/api");
    tbody.innerHTML = appointments
        .map(
            (a) => `
            <tr>
                <td>${a.id}</td>
                <td>${a.patient_name}</td>
                <td>${a.doctor_name}</td>
                <td>${a.appointment_datetime}</td>
                <td>${a.has_bill ? "Generated" : "Pending"}</td>
            </tr>
        `
        )
        .join("");

    if (billAppointmentSelect) {
        billAppointmentSelect.innerHTML =
            `<option value="">Select Appointment</option>` +
            appointments
                .filter((a) => !a.has_bill)
                .map((a) => `<option value="${a.id}">#${a.id} - ${a.patient_name} / ${a.doctor_name}</option>`)
                .join("");
    }
}

async function loadBills() {
    const tbody = document.querySelector("#bills-table tbody");
    if (!tbody) return;
    const bills = await requestJSON("/appointments/bills/api");
    tbody.innerHTML = bills
        .map(
            (b) => `
            <tr>
                <td>${b.id}</td>
                <td>${b.appointment_id}</td>
                <td>${b.patient_name}</td>
                <td>${b.consultation_fee.toFixed(2)}</td>
                <td>${b.medicine_fee.toFixed(2)}</td>
                <td>${b.test_fee.toFixed(2)}</td>
                <td>${b.total_amount.toFixed(2)}</td>
            </tr>
        `
        )
        .join("");
}

async function setupAppointmentPage() {
    const form = document.getElementById("appointment-form");
    const billForm = document.getElementById("bill-form");
    if (!form || !billForm) return;

    await loadAppointmentMeta();
    await loadAppointments();
    await loadBills();

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            patient_id: document.getElementById("appointment-patient").value,
            doctor_id: document.getElementById("appointment-doctor").value,
            appointment_datetime: document.getElementById("appointment-datetime").value,
        };
        try {
            const data = await requestJSON("/appointments/api", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            showMessage(data.message);
            form.reset();
            await loadAppointments();
            await loadBills();
        } catch (error) {
            showMessage(error.message);
        }
    });

    billForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            appointment_id: document.getElementById("bill-appointment").value,
            consultation_fee: document.getElementById("consultation-fee").value || 0,
            medicine_fee: document.getElementById("medicine-fee").value || 0,
            test_fee: document.getElementById("test-fee").value || 0,
        };

        try {
            const data = await requestJSON("/appointments/bills/api", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            showMessage(`${data.message} Total: ${data.total_amount.toFixed(2)}`);
            billForm.reset();
            await loadAppointments();
            await loadBills();
        } catch (error) {
            showMessage(error.message);
        }
    });
}

async function setupAIPage() {
    const form = document.getElementById("ai-form");
    const output = document.getElementById("prediction-output");
    if (!form || !output) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = { symptoms: document.getElementById("symptoms").value.trim() };
        try {
            const data = await requestJSON("/predict", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            output.textContent = data.message || "No prediction available.";
        } catch (error) {
            output.textContent = error.message;
        }
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        if (pagePathEnds("/patients")) await setupPatientPage();
        if (pagePathEnds("/doctors")) await setupDoctorPage();
        if (pagePathEnds("/appointments")) await setupAppointmentPage();
        if (pagePathEnds("/ai")) await setupAIPage();
    } catch (error) {
        console.error("Page initialization failed:", error);
        showMessage(error.message);
    }
});
