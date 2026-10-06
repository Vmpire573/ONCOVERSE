"""Public GDC, ClinicalTrials.gov, and PubMed research adapters."""
import json, os, urllib.parse, urllib.request
from typing import Any

def _request(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent":"OncoVerseAcademicPrototype/1.0"})
    with urllib.request.urlopen(req, timeout=25) as response: return response.read()

def _json(url: str) -> Any: return json.loads(_request(url).decode("utf-8"))

def gdc_cases(cancer_type: str, size: int = 20) -> dict[str, Any]:
    filt = {"op":"and","content":[{"op":"in","content":{"field":"project.primary_site","value":[cancer_type]}}]}
    params = urllib.parse.urlencode({"filters":json.dumps(filt),"size":max(1,min(int(size),100)),"fields":"case_id,submitter_id,project.project_id,project.primary_site,demographic.age_at_index,demographic.gender,diagnoses.vital_status,diagnoses.tumor_stage","format":"JSON"})
    return _json("https://api.gdc.cancer.gov/cases?"+params)

def ingest_gdc_metadata(cancer_type: str, size: int = 20, output: str | None = None) -> dict[str, Any]:
    """Persist public case metadata as source JSON, without fabricating canonical fields."""
    from sqlalchemy import select
    from ..db import ExternalDatasetRecord,IngestionRun,SessionLocal,init_db
    import json as json_module
    payload=gdc_cases(cancer_type,size); hits=payload.get("data",{}).get("hits",[]); accepted=skipped=0; seen=set()
    if output:
        from pathlib import Path
        path=Path(output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json_module.dumps(payload,indent=2))
    init_db()
    with SessionLocal() as session:
        for hit in hits:
            ext_id=str(hit.get("case_id") or hit.get("id") or "")
            if not ext_id: continue
            if ext_id in seen: skipped+=1; continue
            seen.add(ext_id)
            existing=session.scalar(select(ExternalDatasetRecord.id).where(ExternalDatasetRecord.source_name=="GDC",ExternalDatasetRecord.external_id==ext_id))
            if existing: skipped+=1; continue
            session.add(ExternalDatasetRecord(source_name="GDC",external_id=ext_id,payload_json=json_module.dumps(hit,default=str)));accepted+=1
        rejected=len(hits)-accepted-skipped
        session.add(IngestionRun(source_name="GDC public metadata",received=len(hits),accepted=accepted,rejected=rejected,details=json_module.dumps({"skipped_existing":skipped,"query":cancer_type})))
        session.commit()
    return {"source":"GDC","query":cancer_type,"received":len(hits),"accepted":accepted,"rejected":rejected,"skipped_existing":skipped,"raw_response_file":output,"notice":"Public metadata stored separately; no unavailable clinical fields were imputed."}

def _clinical_trials_raw(query: str, page_size: int = 10) -> dict[str, Any]:
    params=urllib.parse.urlencode({"query.cond":query,"format":"json","pageSize":max(1,min(int(page_size),100))})
    return _json("https://clinicaltrials.gov/api/v2/studies?"+params)

def clinical_trials(query: str, page_size: int = 10) -> dict[str, Any]:
    raw=_clinical_trials_raw(query,page_size); studies=[]
    for item in raw.get("studies",[]):
        p=item.get("protocolSection",{});ident=p.get("identificationModule",{});status=p.get("statusModule",{})
        design=p.get("designModule",{});elig=p.get("eligibilityModule",{});description=p.get("descriptionModule",{})
        nct=ident.get("nctId")
        studies.append({"nct_id":nct,"title":ident.get("briefTitle"),"status":status.get("overallStatus"),
            "conditions":p.get("conditionsModule",{}).get("conditions",[]),
            "minimum_age":elig.get("minimumAge"),"maximum_age":elig.get("maximumAge"),
            "brief_summary":description.get("briefSummary",""),"study_type":design.get("studyType"),
            "url":f"https://clinicaltrials.gov/study/{nct}"})
    return {"query":query,"total_count":raw.get("totalCount",len(studies)),"studies":studies}

def match_clinical_trials(cancer_type: str, age: int, stage: str, page_size: int = 20) -> dict[str, Any]:
    response=_clinical_trials_raw(cancer_type,page_size); matches=[]
    def years(value):
        try:
            number,unit=value.split()[:2]; return float(number)*{"Years":1,"Year":1,"Months":1/12,"Weeks":1/52,"Days":1/365}.get(unit)
        except (ValueError,IndexError,TypeError): return None
    for source in response.get("studies",[]):
        p=source.get("protocolSection",{});ident=p.get("identificationModule",{});elig=p.get("eligibilityModule",{})
        low,high=years(elig.get("minimumAge") or ""),years(elig.get("maximumAge") or ""); criteria=str(elig.get("eligibilityCriteria",""))
        if (low is None or age>=low) and (high is None or age<=high) and (not criteria or stage.lower() in criteria.lower() or "stage" not in criteria.lower()):
            nct=ident.get("nctId")
            matches.append({"nct_id":nct,"title":ident.get("briefTitle"),"url":f"https://clinicaltrials.gov/study/{nct}","age_range":{"minimum":elig.get("minimumAge"),"maximum":elig.get("maximumAge")}})
    return {"matches":matches,"checked":len(response.get("studies",[])),"warning":"Coarse public-registry discovery only. Verify all eligibility criteria; this is not an eligibility decision or medical advice."}

def pubmed_search(query: str, max_results: int = 10) -> list[dict[str,str]]:
    base="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"; common={"db":"pubmed","retmode":"json","tool":"oncoverse_academic"}
    if os.getenv("NCBI_EMAIL"): common["email"]=os.environ["NCBI_EMAIL"]
    search=_json(base+"esearch.fcgi?"+urllib.parse.urlencode({**common,"term":query,"retmax":max(1,min(int(max_results),30))}))
    ids=search.get("esearchresult",{}).get("idlist",[])
    if not ids:return []
    url=base+"efetch.fcgi?"+urllib.parse.urlencode({"db":"pubmed","id":",".join(ids),"retmode":"xml"})
    import xml.etree.ElementTree as ET
    root=ET.fromstring(_request(url)); output=[]
    for article in root.findall(".//PubmedArticle"):
        pmid=article.findtext(".//PMID",default=""); node=article.find(".//ArticleTitle")
        title="".join(node.itertext()).strip() if node is not None else ""
        abstract=" ".join((n.text or "").strip() for n in article.findall(".//Abstract/AbstractText"))
        output.append({"pmid":pmid,"title":title,"abstract":abstract,"url":f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"})
    return output

def research_assistant(query: str, max_results: int = 5) -> dict[str, Any]:
    """Citation-grounded extractive summaries of PubMed abstracts."""
    import re
    articles=pubmed_search(query,max_results); terms={t.lower() for t in re.findall(r"[A-Za-z0-9]+",query) if len(t)>2}; results=[]
    for article in articles:
        sentences=[s.strip() for s in re.split(r"(?<=[.!?])\s+",article.get("abstract", "")) if s.strip()]
        ranked=sorted(enumerate(sentences),key=lambda pair:(sum(term in pair[1].lower() for term in terms),-pair[0]),reverse=True)
        selected=[sentence for _,sentence in ranked[:2] if sentence]
        results.append({"title":article["title"],"summary":" ".join(selected) if selected else "No abstract text available.","pmid":article["pmid"],"citation_url":article["url"]})
    return {"query":query,"results":results,"method":"PubMed retrieval plus extractive query-term sentence ranking","notice":"Summaries quote selected abstract sentences and link to source; verify full articles. Not medical advice."}
