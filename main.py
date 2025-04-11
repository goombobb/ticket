# requirements.txt
# fastapi>=0.68.0
# psycopg2-binary>=2.9.3
# sentence-transformers>=2.2.2
# python-dotenv>=0.19.0
# uvicorn>=0.15.0
# pgvector>=0.2.0
# requests>=2.26.0

# .env.example
# DB_NAME=ragdb
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432
# HF_API_TOKEN=your_huggingface_token

import os
import logging
from typing import List, Dict, Any

from pgvector.sqlalchemy import Vector
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize application
app = FastAPI()


# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        register_vector(conn)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")


# Initialize embedding model
embedding_model = SentenceTransformer("sentence-t5-large")

# Initialize database tables
# with get_db_connection() as conn:
#     with conn.cursor() as cur:
#         # Enable pgvector extension
#         # cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

#         # Create production tickets table
#         cur.execute(
#             """
#             CREATE TABLE IF NOT EXISTS production_tickets (
#                 ticket_id SERIAL PRIMARY KEY,
#                 title TEXT NOT NULL,
#                 description TEXT NOT NULL,
#                 status TEXT NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 embedding vector(768)
#             )
#         """
#         )

#         # Create FAQ table
#         cur.execute(
#             """
#             CREATE TABLE IF NOT EXISTS faqs (
#                 faq_id SERIAL PRIMARY KEY,
#                 question TEXT NOT NULL UNIQUE,
#                 answer TEXT NOT NULL,
#                 category TEXT,
#                 embedding vector(768)
#             )
#         """
#         )
#         conn.commit()


# Pydantic models
class TicketCreate(BaseModel):
    title: str
    description: str
    status: str


class FAQCreate(BaseModel):
    question: str
    answer: str
    category: str


class QueryRequest(BaseModel):
    text: str
    top_k: int = 3


# Embedding functions
def get_embedding(text: str) -> List[float]:
    return embedding_model.encode(text).tolist()


# Database operations
@app.post("/tickets/")
def create_ticket(ticket: TicketCreate):
    try:
        embedding = get_embedding(f"{ticket.title} {ticket.description}")
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO production_tickets 
                    (title, description, status, embedding)
                    VALUES (%s, %s, %s, %s)
                    RETURNING ticket_id
                """,
                    (ticket.title, ticket.description, ticket.status, embedding),
                )
                conn.commit()
        return {"message": "Ticket created successfully"}
    except Exception as e:
        logger.error(f"Ticket creation failed: {e}")
        raise HTTPException(status_code=500, detail="Ticket creation failed")


@app.post("/faqs/")
def create_faq(faq: FAQCreate):
    try:
        embedding = get_embedding(faq.question)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO faqs 
                    (question, answer, category, embedding)
                    VALUES (%s, %s, %s, %s)
                    RETURNING faq_id
                """,
                    (faq.question, faq.answer, faq.category, embedding),
                )
                conn.commit()
        return {"message": "FAQ created successfully"}
    except Exception as e:
        logger.error(f"FAQ creation failed: {e}")
        raise HTTPException(status_code=500, detail="FAQ creation failed")


# Search functions
def search_tickets(query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT ticket_id, title, description, status,
                    1 - (embedding <=> %s::vector) AS similarity
                    FROM production_tickets
                    ORDER BY similarity DESC
                    LIMIT %s
                """,
                    (query_embedding, top_k),
                )
                return [
                    dict(
                        zip(["id", "title", "description", "status", "similarity"], row)
                    )
                    for row in cur.fetchall()
                ]
    except Exception as e:
        logger.error(f"Ticket search failed: {e}")
        raise HTTPException(status_code=500, detail="Ticket search failed")


def search_faqs(query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT faq_id, question, answer, category,
                1 - (embedding <=> %s::vector) AS similarity
                FROM faqs
                ORDER BY similarity DESC
                LIMIT %s
            """,
                (query_embedding, top_k),
            )
            return [
                dict(zip(["id", "question", "answer", "category", "similarity"], row))
                for row in cur.fetchall()
            ]


# LLM integration
def generate_response(context: str, query: str) -> str:
    try:
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

        prompt = f"""Use the following context to answer the question. 
        If you don't know the answer, say you don't know. Be concise.
        
        Context:
        {context}
        
        Question: {query}
        Answer: """

        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_new_tokens": 500}},
        )

        if response.status_code == 200:
            return response.json()[0]["generated_text"].split("Answer: ")[-1]
        return f"LLM request failed: {response.__dict__}"
        # return "Sorry, I couldn't generate a response at this time."

    except Exception as e:
        logger.error(f"LLM request failed: {e}")
        return "Error generating response"


# Query endpoint
# explain following function
"""
This function handles incoming query requests by:
1. Converting the query text to an embedding
2. Searching for relevant tickets and FAQs using the embedding
3. Combining the search results into context
4. Generating a natural language response using an LLM
5. Returning the answer along with relevant tickets and FAQs

Args:
    query (QueryRequest): Request object containing query text and top_k parameter

Returns:
    dict: Contains generated answer, relevant tickets and FAQs
    
Raises:
    HTTPException: If query processing fails
"""

@app.post("/query/")
def handle_query(query: QueryRequest):
    try:
        # Generate query embedding
        query_embedding = get_embedding(query.text)

        # Search both data sources
        tickets = search_tickets(query_embedding, query.top_k)
        faqs = search_faqs(query_embedding, query.top_k)

        # Prepare context
        context = "PRODUCTION TICKETS:\n" + "\n".join(
            [f"Ticket {t['id']}: {t['title']} - {t['description']}" for t in tickets]
        )

        context += "\n\nFAQs:\n" + "\n".join(
            [f"FAQ {f['id']}: Q: {f['question']} A: {f['answer']}" for f in faqs]
        )

        # Generate response
        answer = generate_response(context, query.text)

        return {"answer": answer, "relevant_tickets": tickets, "relevant_faqs": faqs}

    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail="Query processing error")


# Example usage
if __name__ == "__main__":
    import uvicorn

    print("Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
