from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import requests
from pathlib import Path
import os
import json
import asyncio
from dotenv import load_dotenv
from clinical_trial_matcher import ClinicalTrialMatcher, TrialMatch

# Load environment variables
load_dotenv()

app = FastAPI(title="Clinical Trial Qualifier - PHI De-identifier & AI Matcher")

# Skyflow API configuration
SKYFLOW_URL = "https://a370a9658141.vault.skyflowapis-preview.com/v1/detect/deidentify/string"
SKYFLOW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2MiOiJ1ODE3NDBkMzIxNWU0NTgzYjI2NTgxZGQ4MzU4M2ZhNiIsImF1ZCI6Imh0dHBzOi8vbWFuYWdlLnNreWZsb3dhcGlzLXByZXZpZXcuY29tIiwiZXhwIjoxNzYzODQyMTI2LCJpYXQiOjE3NjM3NTU3MjYsImlzcyI6InNhLWF1dGhAbWFuYWdlLnNreWZsb3dhcGlzLXByZXZpZXcuY29tIiwianRpIjoiZGE0MTg4YzkyZmY4NGNjNWJlMDI0ZThlYTc5NDk5MzkiLCJzdWIiOiJwOTBiZDM5YjQ5YjQ0OTg2YWI4MGIzNTMxOTcyNTBmYyJ9.T-XWBw2IVy7JHgzy7IktTP9m5Xkkxmojiz9mzumOq4Y3WROor1qSvH5p-YuheBSWa2J8f3bNHsuNEe0NHSegaVFj_rtYZvsWg9FpcIgSt9qmJyRrzgzFuzot2jYI5FvhEnnFtJkbeT5vZ7So0Jpl2nJsZorNoZjrgAd8aauOuG79wPgPuB3WwxNW_6hmHywnIFEdoo0tc1wBxseJtS_SrmhLDcdfP5r25R55KbOp_GrMm4XI1X37KIsrfl12buZxMR_DBzrx8UAnMXJu-PTQqlWDqfARHBvzDTJxNpmvreAp_zz6zVTuG8heGoSZZ5tUq1l3YnzyG6PdYBA2nt8cOQ"
VAULT_ID = "fe079a24274f448fa5fd4c471a07d08a"


# Pydantic models for request/response
class DeidentifyRequest(BaseModel):
    text: str


class DeidentifyResponse(BaseModel):
    text: str


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None


class TrialMatchRequest(BaseModel):
    deidentified_text: str
    max_trials: Optional[int] = 10


class TrialMatchResponse(BaseModel):
    matches: List[TrialMatch]
    report: str


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main page"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    with open(template_path, "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/deidentify", response_model=DeidentifyResponse)
async def deidentify(request: DeidentifyRequest):
    """De-identify medical information using Skyflow"""
    try:
        medical_text = request.text
        
        if not medical_text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Call Skyflow API
        response = requests.post(
            SKYFLOW_URL,
            headers={
                "Authorization": f"Bearer {SKYFLOW_TOKEN}"
            },
            json={
                "text": medical_text,
                "vault_id": VAULT_ID,
                "entity_types": [
                    "name",
                    "phone_number",
                    "account_number",
                    "ssn",
                    "dob",
                    "location_address_street",
                    "healthcare_number"
                ],
                "token_type": {
                    "default": "vault_token"
                }
            },
        )
        
        if response.status_code == 200:
            skyflow_response = response.json()
            # Extract only the de-identified text from the response
            # Skyflow returns 'processed_text' as the key
            deidentified_text = skyflow_response.get('processed_text', '')
            return DeidentifyResponse(text=deidentified_text)
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Skyflow API error: {response.text}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match_trials", response_model=TrialMatchResponse)
async def match_trials(request: TrialMatchRequest):
    """
    Match deidentified patient data against clinical trials using Claude AI.
    This endpoint uses advanced AI to intelligently evaluate eligibility criteria.
    """
    try:
        # Check if API key is configured
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY not configured. Please set it in your .env file."
            )
        
        # Initialize the matcher
        trials_file = Path(__file__).parent / "clinical_trials.txt"
        matcher = ClinicalTrialMatcher(trials_file_path=str(trials_file))
        
        # Match patient to trials
        matches = matcher.match_patient_to_trials(
            deidentified_patient_data=request.deidentified_text,
            max_trials_to_return=request.max_trials or 10
        )
        
        # Generate report
        report = matcher.generate_report(matches)
        
        return TrialMatchResponse(matches=matches, report=report)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching trials: {str(e)}")


@app.post("/deidentify_and_match_stream")
async def deidentify_and_match_stream(request: DeidentifyRequest):
    """
    Streaming version: Shows Claude's thinking as it evaluates each trial
    """
    async def generate():
        try:
            # Step 1: De-identify
            yield f"data: {json.dumps({'type': 'status', 'text': 'Deidentifying with Skyflow...'})}\n\n"
            deidentify_result = await deidentify(request)
            deidentified_text = deidentify_result.text
            
            msg = 'PHI redacted. Starting Claude AI evaluation...\n'
            yield f"data: {json.dumps({'type': 'status', 'text': msg})}\n\n"
            
            # Step 2: Stream Claude's thinking
            trials_file = Path(__file__).parent / "clinical_trials.txt"
            matcher = ClinicalTrialMatcher(trials_file_path=str(trials_file))
            
            # Get trials
            trials = matcher._parse_trials(matcher.trials_database)
            system_prompt = """You are an expert clinical trial coordinator helping find reasonable matches. Be flexible with data format and focus on main criteria, not minor details."""
            
            all_matches = []
            
            for i, trial in enumerate(trials, 1):
                trial_name = trial.get("trial_name", "Unknown")
                header = f'\n\n=== Trial {i}/{len(trials)}: {trial_name} ===\n'
                yield f"data: {json.dumps({'type': 'thinking', 'text': header})}\n\n"
                await asyncio.sleep(0.1)
                
                # Evaluate trial
                match = matcher._evaluate_single_trial(deidentified_text, trial, system_prompt)
                if match:
                    all_matches.append(match)
                    # Show the decision and reasoning
                    decision = f'Decision: {match.match_status} (Confidence: {match.confidence_score:.0%})\n'
                    reasoning_text = f'Reasoning: {match.reasoning}\n'
                    yield f"data: {json.dumps({'type': 'thinking', 'text': decision})}\n\n"
                    await asyncio.sleep(0.1)
                    yield f"data: {json.dumps({'type': 'thinking', 'text': reasoning_text})}\n\n"
                    await asyncio.sleep(0.1)
            
            # Send final result
            report = matcher.generate_report(all_matches)
            result = {
                "type": "complete",
                "deidentified_text": deidentified_text,
                "matches": [m.dict() for m in all_matches],
                "report": report
            }
            yield f"data: {json.dumps(result)}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/deidentify_and_match")
async def deidentify_and_match(request: DeidentifyRequest):
    """
    Complete workflow: De-identify patient data, then match to clinical trials.
    This combines both PHI redaction and AI-powered trial matching.
    """
    try:
        # Step 1: De-identify the data
        deidentify_result = await deidentify(request)
        deidentified_text = deidentify_result.text
        
        # Step 2: Match to trials
        match_request = TrialMatchRequest(deidentified_text=deidentified_text)
        trial_matches = await match_trials(match_request)
        
        return {
            "deidentified_text": deidentified_text,
            "matches": trial_matches.matches,
            "report": trial_matches.report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in complete workflow: {str(e)}")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

