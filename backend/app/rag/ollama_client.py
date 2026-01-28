import requests
from .config import OLLAMA_URL, OLLAMA_MODEL

def generate_answer(context: str, query: str) -> str:
    prompt = f"""You are a factual assistant.

Rules:
- Answer ONLY from the provided context

- Add your context in answer not just copy it from the document
- Do NOT repeat the context
- Use complete sentences-
- Maintain proper grammar and punctuation
- If the question is not related to the context, respond with:
  "The question is not related to the document."
  

Context:
{context}

Question: {query}

Answer (use only information from the context above):"""

    try:
        r = requests.post(
            OLLAMA_URL, 
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9
                }
            },
            timeout=60  # 60 second timeout
        )
        
        r.raise_for_status()  # Raise an exception for bad status codes
        
        response_data = r.json()
        if "response" not in response_data:
            raise Exception(f"Unexpected response format: {response_data}")
        
        return response_data["response"].strip()
        
    except requests.exceptions.ConnectionError:
        raise Exception(f"Cannot connect to Ollama at {OLLAMA_URL}. Is Ollama running?")
    except requests.exceptions.Timeout:
        raise Exception("Ollama request timed out. The model might be too slow or not responding.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")
