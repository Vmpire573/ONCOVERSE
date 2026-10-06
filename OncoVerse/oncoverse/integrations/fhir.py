"""Limited FHIR R4 client and review extraction. Not a certified mapper."""
from datetime import date
import json,urllib.parse,urllib.request
from typing import Any

def _coding(resource: dict[str, Any]) -> str:
    for item in resource.get("code", {}).get("coding", []):
        if item.get("display"): return str(item["display"])
        if item.get("code"): return str(item["code"])
    return "Unknown"

def bundle_to_records(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    if bundle.get("resourceType") != "Bundle": raise ValueError("Expected a FHIR R4 Bundle")
    patients, conditions = {}, []
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {}); rid = resource.get("id")
        if resource.get("resourceType") == "Patient" and rid: patients[str(rid)] = resource
        elif resource.get("resourceType") == "Condition": conditions.append(resource)
    rows = []
    for condition in conditions:
        pid = condition.get("subject", {}).get("reference", "").rsplit("/", 1)[-1]
        patient = patients.get(pid)
        if not patient: continue
        age = None
        try:
            born = date.fromisoformat(patient["birthDate"]); today = date.today()
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        except (KeyError, ValueError): pass
        gender = str(patient.get("gender", "unknown")).title()
        rows.append({"source_id": f"FHIR-{pid}-{condition.get('id', len(rows))}", "age": age,
            "sex": gender if gender in {"Male", "Female", "Other"} else "Unknown", "condition": _coding(condition),
            "stage_text": condition.get("stage", {}).get("summary", {}).get("text"),
            "unmapped_fields": ["tumor_size_mm", "grade", "smoking_status", "outcome_label"]})
    return rows

def fetch_patient_bundle(base_url: str, patient_id: str, token: str | None = None) -> dict[str, Any]:
    """Read one Patient and its Conditions from a configured FHIR R4 server."""
    base=base_url.rstrip("/")
    if not base.startswith("https://") and not base.startswith("http://localhost") and not base.startswith("http://127.0.0.1"):
        raise ValueError("FHIR server URL must use HTTPS (HTTP is allowed only for localhost demos)")
    headers={"Accept":"application/fhir+json","User-Agent":"OncoVerseAcademicPrototype/1.0"}
    if token: headers["Authorization"]="Bearer "+token
    def get(path):
        req=urllib.request.Request(base+path,headers=headers)
        with urllib.request.urlopen(req,timeout=25) as response:return json.loads(response.read().decode())
    patient=get("/Patient/"+urllib.parse.quote(patient_id,safe=""))
    conditions=get("/Condition?subject="+urllib.parse.quote("Patient/"+patient_id,safe=""))
    if patient.get("resourceType")!="Patient" or conditions.get("resourceType")!="Bundle":
        raise ValueError("FHIR server returned an unexpected resource type")
    return {"resourceType":"Bundle","type":"collection","entry":[{"resource":patient}]+conditions.get("entry",[])}
