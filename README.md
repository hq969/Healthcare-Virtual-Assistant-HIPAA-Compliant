
# Healthcare Virtual Assistant (HIPAA-Compliant)

A secure, HIPAA-compliant **virtual healthcare assistant** that supports:

- 🗓️ Appointment scheduling  
- 💊 Prescription lookups  
- 🩺 Symptom triage with multi-step dialogue (LangChain + LangGraph)  
- 📱 Mobile app interface (React Native)  
- ☁️ Cloud-ready architecture (Azure OpenAI, AWS RDS, Dockerized backend)

---

## 🚀 Features
- **HIPAA-ready design**: encryption, token-based auth, PHI-safe handling  
- **FastAPI backend**: secure APIs with persistence in PostgreSQL (local or AWS RDS)  
- **LangChain + LangGraph**: multi-turn memory, workflow orchestration  
- **React Native mobile app**: intuitive interface for patients  
- **Containerized deployment**: run with Docker Compose locally or extend to cloud  

---

## 📂 Project Structure

```

healthcare-virtual-assistant/
│
├── backend/                    # FastAPI backend service
│   ├── app.py                  # Main FastAPI app with endpoints
│   ├── models.py               # SQLAlchemy ORM models
│   ├── langchain\_utils.py      # LangChain & memory utilities
│   ├── requirements.txt        # Backend Python dependencies
│   ├── .env.example            # Environment variables template
│   └── Dockerfile              # Backend Dockerfile
│
├── mobile/                     # React Native (Expo) client app
│   ├── App.js                  # Mobile app entry
│   └── package.json            # Dependencies for mobile app
│
├── docker-compose.yml          # Orchestrates backend + Postgres DB
└── README.md                   # Project documentation

````

---

## ⚙️ Setup Instructions

### 1️⃣ Clone repository
```bash
git clone https://github.com/hq969/healthcare-virtual-assistant-hipaa-compliant.git
cd healthcare-virtual-assistant-hipaa-compliant
````

### 2️⃣ Configure environment variables

Copy example `.env`:

```bash
cp backend/.env.example backend/.env
```

Update with your credentials:

```env
DATABASE_URL=postgresql+psycopg2://hcuser:hcpass@db:5432/hcdb
AUTH_TOKEN=dev-token-CHANGE

# Optional: Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment>
```

### 3️⃣ Run services

```bash
docker-compose up --build
```

* Backend: `http://localhost:8000`
* DB: Postgres (via Docker or AWS RDS)

### 4️⃣ Run mobile app

```bash
cd mobile
npm install
npx expo start
```

Edit `BACKEND` in `mobile/App.js`:

```js
const BACKEND = "http://localhost:8000"; // or emulator IP
```

---

## 🔑 API Endpoints

### Health check

```http
GET /health
```

### Patient management

```http
POST /patient
{
  "name": "Alice Example",
  "phone": "1234567890"
}
```

### Appointment scheduling

```http
POST /schedule
{
  "patient_id": 1,
  "scheduled_at": "2025-10-01T10:00:00",
  "notes": "Routine checkup"
}
```

### Prescription lookup

```http
GET /prescription/{patient_id}
```

### Symptom triage

```http
POST /triage_chain
{
  "patient_id": 1,
  "symptoms": "Mild fever and sore throat for 2 days"
}
```

---

## 🛡️ HIPAA Considerations

* Use **TLS/HTTPS** in production
* Store secrets in **AWS Secrets Manager** / **Azure Key Vault**
* Enable **RDS encryption at rest** + IAM least-privilege access
* **Audit logging** for PHI access
* **No PHI in logs**

---

## 📌 Next Steps

* ✅ Add JWT/OAuth2 for authentication
* ✅ Persist conversation memory across sessions (LangGraph workflows)
* 🔄 Integrate with FHIR/EHR APIs
* ☁️ Deploy on AWS ECS/Fargate or Azure App Service

---

## 📜 License

MIT — use freely with attribution.

---

