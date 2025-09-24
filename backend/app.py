import os
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Patient, Appointment, Prescription, MessageMemory
import openai

# LangChain helpers (triage_chain)
from langchain_utils import get_azure_llm, make_triage_chain, memory_to_db

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'dev-token-CHANGE')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL is required')

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title='Healthcare Virtual Assistant')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

# Configure Azure OpenAI for direct OpenAI calls if present
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY:
    openai.api_type = 'azure'
    openai.api_base = AZURE_OPENAI_ENDPOINT
    openai.api_version = '2023-05-15'
    openai.api_key = AZURE_OPENAI_KEY

# Auth dependency
async def require_auth(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization header')
    token = authorization.replace('Bearer ', '')
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail='Invalid token')
    return True

# Pydantic models for requests
class CreatePatient(BaseModel):
    name: str
    phone: str | None = None

class ScheduleReq(BaseModel):
    patient_id: int
    scheduled_at: str
    notes: str | None = ''

class TriageReq(BaseModel):
    patient_id: int
    symptoms: str

@app.get('/health')
async def health():
    return {'status': 'ok', 'time': datetime.utcnow().isoformat()}

@app.post('/patient')
async def create_patient(payload: CreatePatient, auth=Depends(require_auth)):
    db = SessionLocal()
    p = Patient(name=payload.name, phone=payload.phone)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {'id': p.id, 'name': p.name}

@app.post('/schedule')
async def schedule(payload: ScheduleReq, auth=Depends(require_auth)):
    db = SessionLocal()
    try:
        dt = datetime.fromisoformat(payload.scheduled_at)
    except Exception:
        raise HTTPException(status_code=400, detail='scheduled_at must be ISO format')
    appt = Appointment(patient_id=payload.patient_id, scheduled_at=dt, notes=payload.notes)
    db.add(appt)
    db.commit()
    db.refresh(appt)
    mem = MessageMemory(patient_id=payload.patient_id, role='system', content=f'Scheduled appointment at {payload.scheduled_at}')
    db.add(mem)
    db.commit()
    return {'appointment_id': appt.id, 'scheduled_at': appt.scheduled_at.isoformat()}

@app.get('/prescription/{patient_id}')
async def prescription_lookup(patient_id: int, auth=Depends(require_auth)):
    db = SessionLocal()
    rx = db.query(Prescription).filter(Prescription.patient_id == patient_id).order_by(Prescription.created_at.desc()).first()
    if not rx:
        return {'prescription': None}
    return {'medication': rx.medication, 'instructions': rx.instructions, 'created_at': rx.created_at.isoformat()}

@app.post('/triage')
async def triage(payload: TriageReq, auth=Depends(require_auth)):
    db = SessionLocal()
    db.add(MessageMemory(patient_id=payload.patient_id, role='user', content=payload.symptoms))
    db.commit()

    prompt = f"Patient symptoms: {payload.symptoms}\nProvide a brief triage recommendation (not a diagnosis). Include next steps and urgency level."

    if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY and AZURE_OPENAI_DEPLOYMENT:
        try:
            resp = openai.Completion.create(engine=AZURE_OPENAI_DEPLOYMENT, prompt=prompt, max_tokens=300, temperature=0.2)
            text = resp.choices[0].text.strip()
        except Exception as e:
            text = f"(OpenAI error) Please contact your provider. Error: {e}"
    else:
        text = "Fallback triage: contact your primary care provider. If you have difficulty breathing, chest pain or severe bleeding seek emergency care."

    db.add(MessageMemory(patient_id=payload.patient_id, role='assistant', content=text))
    db.commit()
    return {'triage': text}

@app.post('/triage_chain')
async def triage_chain(payload: TriageReq, auth=Depends(require_auth)):
    db = SessionLocal()
    # Save user message
    db.add(MessageMemory(patient_id=payload.patient_id, role='user', content=payload.symptoms))
    db.commit()

    llm = get_azure_llm()
    if llm is None:
        # Fallback if LangChain/Azure not configured
        text = "Fallback triage: contact your primary care provider. If severe symptoms are present, seek emergency care."
        db.add(MessageMemory(patient_id=payload.patient_id, role='assistant', content=text))
        db.commit()
        return {'triage': text, 'used_chain': False}

    chain, memory = make_triage_chain(llm=llm)
    # Run the chain
    result = chain.run({'symptoms': payload.symptoms})

    # Persist memory to DB (best-effort)
    try:
        memory_to_db(db, payload.patient_id, memory)
    except Exception as e:
        print('memory_to_db failed:', e)

    # Save assistant response
    db.add(MessageMemory(patient_id=payload.patient_id, role='assistant', content=result))
    db.commit()
    return {'triage': result, 'used_chain': True}

@app.post('/run-workflow')
async def run_workflow(data: dict, auth=Depends(require_auth)):
    # Placeholder for LangGraph orchestration integration (simulate workflow)
    return {'workflow': data.get('workflow', 'demo'), 'status': 'simulated'}
