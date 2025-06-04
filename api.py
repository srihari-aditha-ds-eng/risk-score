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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"], 
    allow_headers=["*"],  
    expose_headers=["*"],  
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Serve static files from the 'static_frontend' directory
app.mount("/static", StaticFiles(directory="static_frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static_frontend/index.html")

def parse_analysis(analysis_text: str) -> dict:
    """Parse the analysis text to extract risk score, clauses, risk categories, and clause severity from LLM output."""
    result = {
        "risk_score": 0,
        "risky_clauses": [],
        "risk_categories": [],
        "clause_severity": []
    }

    # Extract risk score
    score_match = re.search(r"Risk Score:\s*(\d+)", analysis_text)
    if score_match:
        result["risk_score"] = int(score_match.group(1))

    # Extract risky clauses, categories, and severity from LLM formatted list
    clauses = []
    categories = []
    severity_tags = [] # Use a new variable name for clarity

    # Regex to capture: Clause Text, Severity, Category, Explanation
    # Format: [Clause Text] [Severity] [Category] - [Explanation]
    clause_regex = re.compile(r'(.+?)\s*\[([^\]]+)\]\s*\[([^\]]+)\]\s*-\s*(.+)')

    for line in analysis_text.split('\n'):
        # Check for numbered list items (1., 2., etc.) from LLM output
        if re.match(r'^\d+\.\s*', line.strip()):
            # Remove the number and dot prefix
            line_cleaned = re.sub(r'^\d+\.\s*', '', line.strip())

            # Remove potential original document numbering at the beginning of the line
            line_cleaned = re.sub(r'^(\d+(\.\d+)*\s+)', '', line_cleaned)

            # Attempt to match the new LLM output format (Clause] [Severity] [Category] - Explanation)
            match = clause_regex.match(line_cleaned)

            if match:
                # Extract groups: (Clause Text), (Severity), (Category), (Explanation)
                clause_text = match.group(1).strip()
                severity = match.group(2).strip()
                category = match.group(3).strip()
                explanation = match.group(4).strip()

                # Combine clause text and explanation for the risky_clauses array
                full_clause_entry = f"{clause_text} - {explanation}"

                clauses.append(full_clause_entry)
                severity_tags.append(severity)
                categories.append(category)
            elif line_cleaned: # Fallback if regex doesn't match but line is not empty
                 # This case might happen if the LLM doesn't follow the format perfectly.
                 # We'll add the cleaned line as clause text, and empty strings for category/severity.
                 clauses.append(line_cleaned)
                 severity_tags.append("")
                 categories.append("")

    result["risky_clauses"] = clauses
    result["risk_categories"] = categories
    result["clause_severity"] = severity_tags # Use the extracted severity tags

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