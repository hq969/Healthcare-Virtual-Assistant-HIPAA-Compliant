import os
from typing import Tuple, Any
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

def get_azure_llm(temperature: float = 0.2, max_tokens: int = 300):
    """
    Return an AzureChatOpenAI instance if Azure variables are set; otherwise None.
    """
    if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY and AZURE_OPENAI_DEPLOYMENT):
        return None
    # AzureChatOpenAI will read AZURE_* env vars internally via configuration in many setups.
    llm = AzureChatOpenAI(deployment_name=AZURE_OPENAI_DEPLOYMENT, temperature=temperature, max_tokens=max_tokens)
    return llm

def make_triage_chain(llm=None) -> Tuple[LLMChain, ConversationBufferMemory]:
    """
    Build an LLMChain with a prompt template and a ConversationBufferMemory.
    Returns (chain, memory).
    """
    prompt = PromptTemplate(
        input_variables=['symptoms', 'history'],
        template=(
            "You are a clinical assistant (non-diagnostic). Patient symptoms: {symptoms}\n"
            "Conversation history: {history}\n"
            "Provide a brief triage recommendation (not a diagnosis). Include next steps and urgency level."
        )
    )
    # memory_key 'history' corresponds to prompt variable
    memory = ConversationBufferMemory(memory_key='history', input_key='symptoms', return_messages=False)
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    return chain, memory

def memory_to_db(db_session, patient_id: int, memory: Any):
    """
    Persist conversation buffer memory into message_memory DB table.
    Works with common LangChain memory internals; best-effort extraction.
    """
    from models import MessageMemory

    msgs = []
    try:
        # Many LangChain memory implementations have chat_memory.messages
        if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
            for m in memory.chat_memory.messages:
                role = getattr(m, 'type', None) or getattr(m, 'role', 'assistant')
                content = getattr(m, 'content', str(m))
                msgs.append((role, content))
        elif hasattr(memory, 'buffer') and isinstance(memory.buffer, str):
            # fallback: a single combined string
            msgs = [('assistant', memory.buffer)]
        else:
            # best-effort string representation
            msgs = [('assistant', str(memory))]
    except Exception:
        msgs = [('assistant', str(memory))]

    for role, content in msgs:
        mm = MessageMemory(patient_id=patient_id, role=role, content=content)
        db_session.add(mm)
    db_session.commit()
