import os
import json
from pathlib import Path


from google import genai
from google.genai import types


# =========================================================
# 1. GEMINI CLIENT
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=api_key)


# =========================================================
# 2. AI INVESTIGATION FUNCTION
# =========================================================

def investigate_candidate(candidate):

    # -----------------------------------------------------
    # Create prompt
    # -----------------------------------------------------

    prompt = f"""
You are the AI Investigator for CleanMaster AI.

Analyze the following duplicate customer candidate.

Candidate data:

{json.dumps(candidate, indent=4)}

Use ONLY the evidence provided.

Return ONLY valid JSON:

{{
    "decision": "MERGE" or "FLAG" or "KEEP_SEPARATE",
    "confidence": "HIGH" or "MEDIUM" or "LOW",
    "reason": "short explanation",
    "recommendation": "what should happen next"
}}

Rules:

- MERGE = strong evidence that both records are the same customer.
- FLAG = evidence is ambiguous and needs human review.
- KEEP_SEPARATE = evidence suggests different customers.
- Do not invent information.
- Keep the response concise.
"""

    # -----------------------------------------------------
    # Call Gemini
    # -----------------------------------------------------

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=300
        )
    )

    # -----------------------------------------------------
    # Read Gemini response
    # -----------------------------------------------------

    ai_text = response.text.strip()

    result = json.loads(ai_text)

    # -----------------------------------------------------
    # Add system information
    # -----------------------------------------------------

    result["customer_1"] = candidate.get("customer_1")
    result["customer_2"] = candidate.get("customer_2")
    result["investigated_by"] = "CleanMaster AI Investigator"

    return result


# =========================================================
# 3. TEST THE INVESTIGATOR DIRECTLY
# =========================================================

if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[2]

    candidate_file = (
        project_root
        / "data"
        / "candidate_results.json"
    )

    if not candidate_file.exists():
        print("ERROR: candidate_results.json not found.")
        exit()

    with open(candidate_file, "r", encoding="utf-8") as file:
        candidates = json.load(file)

    if not candidates:
        print("ERROR: No duplicate candidates found.")
        exit()

    # -----------------------------------------------------
    # Select first candidate for testing
    # -----------------------------------------------------

    candidate = candidates[0]

    print("\n========================================")
    print("     CLEANMASTER AI - INVESTIGATOR")
    print("========================================")

    print("\nCustomer Pair:")

    print(
        f"{candidate.get('customer_1')} "
        f"<--> "
        f"{candidate.get('customer_2')}"
    )

    try:

        result = investigate_candidate(candidate)

        print("\nAI INVESTIGATION RESULT:\n")

        print(json.dumps(result, indent=4))

    except json.JSONDecodeError:

        print("\nERROR: Gemini did not return valid JSON.")

    except Exception as e:

        print("\nERROR WHILE CALLING GEMINI:")
        print(str(e))