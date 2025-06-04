from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
import os
from main import analyze_document
import re
import shutil

app = FastAPI()

# Add CORS middleware (adjust allow_origins if you deploy to a specific domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Serve static files from the 'static_frontend' directory
app.mount("/static", StaticFiles(directory="static_frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static_frontend/index.html")

def parse_analysis(analysis_text: str) -> dict:
    """Parse the analysis text to extract risk score and clauses."""
    result = {
        "risk_score": 0,
        "risky_clauses": []
    }
    
    # Extract risk score
    score_match = re.search(r"Risk Score:\s*(\d+)", analysis_text)
    if score_match:
        result["risk_score"] = int(score_match.group(1))
    
    # Extract risky clauses
    clauses = []
    for line in analysis_text.split('\n'):
        if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
            # Remove the number and dot prefix from the model's list
            clause_text_raw = re.sub(r'^\d+\.\s*', '', line.strip())
            
            # Further remove potential original document numbering at the beginning of the line
            # This regex looks for patterns like '6.5 ', '8.4 ', '9.1 ', etc. at the start of the line
            clause_text_cleaned = re.sub(r'^(\d+(\.\d+)*\s+)', '', clause_text_raw)
            
            if clause_text_cleaned:
                clauses.append(clause_text_cleaned)
    
    result["risky_clauses"] = clauses
    return result

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # Create documents directory if it doesn't exist
    os.makedirs("documents", exist_ok=True)
    
    # Save the uploaded file to the documents folder
    file_path = os.path.join("documents", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze the document using the globally initialized components from main
    analysis = analyze_document(file_path)
    
    # Parse the analysis
    result = parse_analysis(analysis['analysis'])
    
    # Return the response
    return JSONResponse(content=result)

@app.get("/health")
async def health():
    return {"status": "ok"}