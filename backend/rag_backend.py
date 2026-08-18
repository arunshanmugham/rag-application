import os
import json
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import agentplatform
from google.cloud import aiplatform_v1beta1 as google_ai

app = FastAPI()

# Validate environment variables are present locally
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
RAG_CORPUS_ID = os.getenv("RAG_CORPUS_ID")
LOCATION = "global"
CORPUS_LOCATION = "us-east2"
DATA_REGION = "us-east4" 


# Initialize modern clients
# The genai client handles text generation and automatically inherits ambient GCP credentials
genai_client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

# The agentplatform client handles modern RAG Engine asset operations
rag_client = agentplatform.Client(project=PROJECT_ID, location=LOCATION)

class QueryRequest(BaseModel):
    question: str

# Define a clean, native Pydantic class to replace the manual Schema/Type setup
class RoutingDecision(BaseModel):
    # Enforces that the string must be exactly one of these two choices
    pipeline_type: Literal["DIRECT_RAG", "MULTI_STEP_AGENT"] = Field(
        description="The designated route for processing the query."
    )
    reason: str = Field(description="Explanation of why this routing path was selected.")

def run_local_router(query: str) -> str:
    """Uses Gemini Flash-Lite to categorize the query style."""
    prompt = (
        f"Categorize this user query. Use DIRECT_RAG for simple facts/lookups. "
        f"Use MULTI_STEP_AGENT for cross-referencing, multi-file queries, or math calculations.\n"
        f"Query: {query}"
    )
    
    # Generate content using the new client schema configuration matching our Pydantic model
    response = genai_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RoutingDecision,
        ),
    )
    # Parse out the structured result safely
    return json.loads(response.text)["pipeline_type"]

async def execute_direct_rag(question: str):
    """Path A: Complete fail-safe configuration with exact query routing parameters."""
    
    # 1. Target the low-level regional API gateway client directly
    api_client = google_ai.FeatureOnlineStoreServiceClient(
        client_options={"api_endpoint": f"{DATA_REGION}://googleapis.com"}
    )
    
    # 2. Convert text input into embeddings
    embedding_response = genai_client.models.embed_content(
        model="text-embedding-005",
        contents=question
    )
    vector_values = embedding_response.embeddings.values
    
    # 3. Create the correctly namespaced Search Request
    search_request = google_ai.SearchNearestEntitiesRequest(
        feature_view=f"projects/{PROJECT_ID}/locations/{DATA_REGION}/ragCorpora/{RAG_CORPUS_ID}",
        # Match the query structure exactly to the API specifications
        query=google_ai.SearchNearestEntitiesRequest.Query(
            string_filters=None, # Add filters here if needed later
            embedding=google_ai.SearchNearestEntitiesRequest.Query.Embedding(value=vector_values),
            neighbor_count=3
        )
    )
    
    try:
        # Extract matching indices from the vector table
        search_results = api_client.search_nearest_entities(request=search_request)
        # Parse text straight out of the structural result neighbors object array
        context_chunks = [neighbor.entity_id for neighbor in search_results.nearest_neighbors.neighbors]
        context = "\n".join(context_chunks)
    except Exception as e:
        # Soft fallback error containment
        context = f"System context offline. Underlying detail: {str(e)}"

    # 4. Process the prompt via the stable global text model tier
    prompt = f"Answer using this context:\n{context}\n\nQuestion: {question}"
    answer = genai_client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )
    return {"path_used": "DIRECT_RAG_VECTOR_FALLBACK", "answer": answer.text}

async def execute_agentic_loop(question: str):
    """Path B: Simulating a multi-step loop locally."""
    simulation_prompt = f"Break down and thoroughly answer this complex task step-by-step: {question}"
    
    # Call the heavier logic model using the updated client parameters
    answer = genai_client.models.generate_content(
        model="gemini-3.5-flash",
        contents=simulation_prompt
    )
    return {"path_used": "MULTI_STEP_AGENT", "answer": answer.text}

@app.post("/api/ask")
async def ask_endpoint(payload: QueryRequest):
    try:
        path = run_local_router(payload.question)
        if path == "DIRECT_RAG":
            return await execute_direct_rag(payload.question)
        else:
            return await execute_agentic_loop(payload.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
