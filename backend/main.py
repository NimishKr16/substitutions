from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from concurrent.futures import ThreadPoolExecutor
from brands.yageo.yageo_gen import generate_substitutions

app = FastAPI()

class BatchRequest(BaseModel):
    brand: str
    mpns: List[str]

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def read_health():
    return {"status": "Healthy"}

@app.get("/api/generate")
def generate_part_substitutions(
    brand: str = Query(..., description="Brand name (e.g., yageo)"),
    mpn: str = Query(..., description="Manufacturer Part Number")
):
    """
    Generate substitutions for a given part number.
    Currently supports Yageo parts.
    """
    if brand.lower() != "yageo":
        return {
            "error": "Only Yageo brand is currently supported",
            "series": "UNKNOWN",
            "substitutions": []
        }
    
    result = generate_substitutions(mpn)
    
    return {
        "brand": brand,
        "mpn": mpn,
        "series": result["series"],
        "substitutions": result["substitutions"]
    }

@app.post("/api/generate/batch")
def generate_batch_substitutions(request: BatchRequest):
    """
    Generate substitutions for multiple part numbers in parallel.
    Currently supports Yageo parts.
    """
    if request.brand.lower() != "yageo":
        return {
            "error": "Only Yageo brand is currently supported",
            "brand": request.brand,
            "total": 0,
            "results": []
        }
    
    def process_single_mpn(mpn: str):
        result = generate_substitutions(mpn)
        return {
            "mpn": mpn,
            "series": result["series"],
            "substitutions": result["substitutions"]
        }
    
    # Process MPNs in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(process_single_mpn, request.mpns))
    
    return {
        "brand": request.brand,
        "total": len(results),
        "results": results
    }