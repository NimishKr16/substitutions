from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from brands.yageo.yageo_gen import generate_substitutions

app = FastAPI()

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