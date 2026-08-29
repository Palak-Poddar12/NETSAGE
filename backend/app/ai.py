
import os, json, openai
from app.prompts import SYSTEM_PROMPT, build_diagnosis_prompt
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def diagnose(case, evidence_list, rule_findings):
    prompt = build_diagnosis_prompt(case, evidence_list, rule_findings)
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],
            temperature=0.2,
            response_format={"type":"json_object"}
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        data.setdefault("root_cause","")
        data.setdefault("category","")
        data.setdefault("osi_layer","")
        data.setdefault("confidence",0)
        data.setdefault("evidence",[])
        data.setdefault("next_command","")
        data.setdefault("fix_steps",[])
        data.setdefault("verification_command","")
        data.setdefault("human_review_required",True)
        if not data["root_cause"] and not data["evidence"]:
            data["root_cause"] = "INSUFFICIENT_EVIDENCE"
            data["confidence"] = 0
        return data
    except Exception as e:
        return {"root_cause":"AI_ERROR","category":"","osi_layer":"","confidence":0,"evidence":[],"next_command":"","fix_steps":[],"verification_command":"","human_review_required":True}
