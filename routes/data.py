from fastapi import APIRouter
import json
import os

router = APIRouter(prefix="/api/data", tags=["data"])

@router.get("/catalog")
def catalog():
    schema_path = os.path.join(os.path.dirname(__file__), '../../schema_catalog.json')
    if not os.path.exists(schema_path):
        return {"error": "Schema catalog not found. Run scripts/data_catalog.py first."}
    with open(schema_path) as f:
        return json.load(f)
