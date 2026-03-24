# 🏥 Hospital Management System (Flask)

A full-stack **Hospital Management System** built using **Python Flask**, designed for efficient management of patients, doctors, appointments, billing, and a smart AI-based disease prediction system.

---

## 🚀 Features

### 🔐 Authentication

* Simple login system (admin/staff)
* Session-based authentication
* Username displayed on dashboard
* Logout functionality

### 👨‍⚕️ Patient Management

* Add new patients
* View patient records
* Delete patients
* Fields: Name, Age, Gender, Phone, Disease

### 🩺 Doctor Management

* Add doctors
* View doctor list
* Fields: Name, Specialization, Availability

### 📅 Appointment System

* Book appointments
* Assign doctor to patient
* Date & time scheduling
* Prevent duplicate bookings

### 💰 Billing System

* Generate bills
* Store billing history
* Simple cost calculation

### 🧠 AI Disease Predictor (No API)

* Input symptoms (e.g., fever, cough)
* Predict possible diseases with probability
* Rule-based intelligent system
* No external APIs used

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask)
* **Database:** SQLite (SQLAlchemy ORM)
* **Frontend:** HTML, CSS, JavaScript (Jinja Templates)
* **Version Control:** Git (optional)

---

## 📂 Project Structure

```
hospital_management/
│── app.py
│── models.py
│── database.db
│── requirements.txt
│
├── routes/
│   ├── auth.py
│   ├── patient.py
│   ├── doctor.py
│   ├── appointment.py
│   ├── ai.py
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── patients.html
│   ├── doctors.html
│   ├── appointments.html
│   ├── ai.html
│
├── static/
│   ├── css/
│   ├── js/
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone or Download Project

```bash
git clone <repo-url>
cd hospital_management
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### 3️⃣ Activate Virtual Environment

* Windows:

```bash
venv\Scripts\activate
```

* Mac/Linux:

```bash
source venv/bin/activate
```

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 5️⃣ Run Application

```bash
python app.py
```

### 6️⃣ Open in Browser

```
http://127.0.0.1:5000/
```

---

## 🔑 Login Credentials

```
Username: admin
Password: admin123
```

*(Can be modified in code)*

---

## 🧠 AI Disease Prediction Logic

* Uses a **rule-based system**
* Maps symptoms → diseases with weights
* Aggregates probabilities
* Returns top 3 likely conditions

### Example:

Input:

```
fever, headache
```

Output:

```
1. Viral Fever - 80%
2. Flu - 70%
3. Typhoid - 50%
```

---

## 🔄 Functional Flow

1. Login → Dashboard
2. Add Patient / Doctor
3. Book Appointment
4. Generate Bill
5. Use AI Predictor
6. Logout

---

## 🧪 Testing Checklist

* ✅ Login works
* ✅ Username displays correctly
* ✅ CRUD operations working
* ✅ Appointment booking valid
* ✅ AI prediction returns results
* ✅ No broken pages or errors

---

##
