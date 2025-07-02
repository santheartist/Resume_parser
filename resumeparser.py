import openai
import yaml
import json

CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH) as file:
    config = yaml.safe_load(file)

client = openai.OpenAI(api_key=config.get("OPENAI_API_KEY") or config.get("openai", {}).get("api_key"))

def ats_extractor(resume_text, target_role):
    extract_prompt = '''
    You are a resume parsing expert AI. Extract the following from the given resume:
    1. Full Name
    2. Email ID
    3. GitHub Portfolio
    4. LinkedIn ID
    5. Employment Details (Company, Role, Duration)
    6. Technical Skills
    7. Soft Skills

    Return only a clean, structured JSON with this data.
    '''

    extract_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": extract_prompt},
            {"role": "user", "content": resume_text}
        ],
        temperature=0.0,
        max_tokens=1500
    )

    raw_json = extract_response.choices[0].message.content

    try:
        parsed_data = json.loads(raw_json)
    except json.JSONDecodeError:
        return {
            "error": "❌ Failed to parse structured resume output from OpenAI.",
            "raw": raw_json
        }

    evaluation_prompt = f'''
    You are a senior HR recruiter. Based on the following extracted resume data:
    {json.dumps(parsed_data, indent=2)}

    Please do the following:
    1. Evaluate if this candidate is suitable for the role of "{target_role}".
    2. Rate them out of 10 based on skills, experience, and relevance.
    3. Give a short recommendation.
    4. State whether to proceed with the candidate or not.

    Return in JSON: {{
      "score": 8,
      "recommendation": "...",
      "proceed": "Yes" or "No"
    }}
    '''

    eval_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a senior recruiter assistant."},
            {"role": "user", "content": evaluation_prompt}
        ],
        temperature=0.0,
        max_tokens=500
    )

    try:
        evaluation_data = json.loads(eval_response.choices[0].message.content)
    except json.JSONDecodeError:
        evaluation_data = {
            "score": "N/A",
            "recommendation": "❌ Could not generate evaluation.",
            "proceed": "N/A"
        }

    return {**parsed_data, "evaluation": evaluation_data}
