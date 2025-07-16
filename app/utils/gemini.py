from google import genai
import os
import json
import re

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyAcWZnWArOVBvBNPNSbJngJ1Wj5Eeq6phw")

def assess_job_feasibility(job_data: dict) -> str:
    # Remove `feasibility_status` if present
    job_data.pop('feasibility_status', None)


    prompt = f"""
    You are an Upwork job analyzer. Your job is to assess whether a given job post is:
    - valid (real and trustworthy),
    - scam (fraudulent or suspicious), or
    - unsure (not enough information).

    Here is the job data in JSON:
    {job_data}

    Based on the data above, respond only with one of the following:
    - valid
    - scam
    - unsure
    """


    try:
        
        response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
        )
        status = response.text.strip().lower()


        if status not in ['valid', 'scam', 'unsure']:
            print(status)
            return 'unsure'  # fallback if Gemini returns something unexpected
        return status
    except Exception as e:
        print("Error in Gemini call:", e)
        return 'unsure'





def assess_proposal_from_job(job_data: dict) -> dict:

    prompt = f"""
    You are a senior Upwork bidding assistant AI.

    Given this job data, return a JSON with the following fields:

    - "cover_letter": A professional Upwork cover letter in natural language.
    - "proposal": A professional Upwork cproposal in natural language.
    - "feasibility_score": A float between 0 and 100 (how feasible this job is to win).
    - "feasibility_reason": 1-2 sentence reason explaining the score.
    - "summary": A 1-2 sentence summary of the job.
    - "project_duration": Estimated duration (e.g., "2-3 weeks", "1-2 months").
    - "overall_score": Float between 0 and 100 representing AI confidence in job quality.

    Job data:
    {json.dumps(job_data, indent=2)}
    """

    try:
        response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
        )
        output = response.text.strip()


        result = extract_json_from_text(output)


        return {
            "cover_letter": result["cover_letter"],
            "proposal": result["proposal"],
            "feasibility_score": float(result["feasibility_score"]),
            "feasibility_reason": result["feasibility_reason"],
            "summary": result["summary"],
            "project_duration": result["project_duration"],
            "overall_score": float(result["overall_score"]),
        }

    except Exception as e:
        print("[Gemini Error]", e)
        return {
            "cover_letter": "",
            "feasibility_score": 0,
            "feasibility_reason": "Gemini failed to analyze the job.",
            "summary": "",
            "project_duration": "",
            "overall_score": 0,
        }
    
def generate_dummy_upwork_jobs() -> list:
    prompt = """
Create 10 realistic Upwork job postings in JSON format. Each job should follow this exact structure:

{
  "job_id": "cloud-devops-terraform-2025",
  "title": "Cloud DevOps Engineer with Terraform Experience",
  "description": "Need an AWS DevOps engineer to create IaC scripts using Terraform for scalable infrastructure. Jenkins + Kubernetes knowledge is a plus.",
  "skills": ["AWS", "Terraform", "DevOps", "CI/CD", "Jenkins", "Kubernetes"],
  "tags": ["devops", "terraform", "aws", "ci/cd"],
  "category": "DevOps & Cloud",
  "client_country": "Australia",
  "client_payment_verified": true,
  "client_total_spent": 12000.00,
  "client_jobs_posted": 11,
  "client_hire_rate": "89%",
  "client_reviews": "Knows what he wants. Very clear expectations.",
  "budget": 2800.00,
  "budget_type": "fixed",
  "project_length": "1-3 months",
  "hours_per_week": "40 hrs/week",
  "proposals_submitted": 30,
  "interviewing": 5,
  "invites_sent": 9,
  "connect_required": 6,
  "expected_cost": 2500.00,
  "expected_earnings": 2200.00,
  "posted_at": "2025-07-13T12:00:00Z",
  "job_url": "https://www.upwork.com/job/cloud-devops-terraform-2025"
}

Return only the list of 10 jobs as JSON array.
"""


    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
        )
    
    # Extract the JSON string
    raw_text = response.candidates[0].content.parts[0].text.strip()

    # Remove markdown code block (```json ... ```)
    cleaned_text = re.sub(r"^```json|```$", "", raw_text).strip()

    # Parse into Python list of jobs
    try:
        jobs = json.loads(cleaned_text)
        return jobs
    except json.JSONDecodeError as e:
        print(f"Failed to parse jobs JSON: {e}")
        return []
    


def extract_json_from_text(text):
    """
    Extract the JSON object from a string that may be wrapped in ```json ... ```
    """
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:

        match = re.search(r"({.*})", text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
        else:
            raise ValueError("No JSON content found in Gemini output.")
    print(json_str)
    return json.loads(json_str)