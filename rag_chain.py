import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Groq ka standard model ID
MODEL_NAME = "openai/gpt-oss-120b"

def answer_question(db_collection, query: str) -> str:
    results = db_collection.query(query_texts=[query], n_results=4)
    retrieved_chunks = results['documents'][0]
    
    context = "\n---\n".join(retrieved_chunks)
    
    prompt = f"""
You are an expert tutor and YouTube AI assistant. 
Answer the user's question based strictly on the video transcript context provided below.

CONTEXT FROM VIDEO:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Pay attention to any specific format requested by the user (e.g., 2-3 marks, 5 marks, bullet points, or summary).
2. For 2-3 marks requests: Keep it strictly concise (1 short definition + 2 quick bullet points).
3. For 5 marks requests: Provide a structured breakdown with definitions, key points, and benefits.
4. If no specific mark format is requested, provide a clear, balanced, and direct answer.
5. If the context does not contain enough details, state what is missing.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content


def generate_summary(db_collection) -> str:
    """
    ChromaDB collection se all chunks retrieve karke summary banata hai.
    """
    all_docs = db_collection.get()['documents']
    full_transcript = " ".join(all_docs)
    
    truncated_transcript = full_transcript[:12000]
    
    prompt = f"""
You are an expert content summarizer. Provide a concise, highly engaging summary of the following YouTube video transcript.

TRANSCRIPT:
{truncated_transcript}

FORMAT YOUR RESPONSE AS FOLLOWS:
🎯 **Key Takeaway:** (1-2 sentence core message)
📌 **Main Points:**
- Bullet point 1
- Bullet point 2
- Bullet point 3
- Bullet point 4
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content


def generate_quiz(db_collection) -> str:
    """
    ChromaDB collection se all chunks retrieve karke 3 MCQs banata hai.
    """
    all_docs = db_collection.get()['documents']
    full_transcript = " ".join(all_docs)
    
    truncated_transcript = full_transcript[:12000]
    
    prompt = f"""
Based on the following video transcript, create 3 multiple-choice quiz questions to test user comprehension.

TRANSCRIPT:
{truncated_transcript}

FORMAT EACH QUESTION EXACTLY LIKE THIS:
**Q1: [Question text here]**
A) Option 1
B) Option 2
C) Option 3
D) Option 4
*Correct Answer:* [Correct Option and short 1-line reason]
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content