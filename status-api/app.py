"""API de statut CloudNova — service pédagogique du labo AFORP (labs 4.1, 4.2 et épreuve finale).

Endpoints :
  GET  /health                     sans authentification, renvoie {"status": "ok"}
  GET  /components?page=&per_page= authentification Bearer, liste paginée des composants
  GET  /incidents                  authentification Bearer
  POST /incidents                  authentification Bearer, crée un incident (201)
  GET  /flaky                      renvoie toujours une erreur 500 (test de gestion d'erreurs)
  GET  /slow                       répond après 5 secondes (test de timeout)
"""
import math
import os
import time
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

TOKEN = os.environ.get("STATUS_API_TOKEN", "aforp-demo-token")

app = FastAPI(title="CloudNova Status API", version="1.0")

COMPONENTS = [
    {"id": 1, "name": "site-web", "status": "operational"},
    {"id": 2, "name": "api-commandes", "status": "operational"},
    {"id": 3, "name": "paiements", "status": "degraded_performance"},
    {"id": 4, "name": "base-clients", "status": "operational"},
    {"id": 5, "name": "recherche", "status": "major_outage"},
    {"id": 6, "name": "stockage-s3", "status": "operational"},
]
INCIDENTS: list[dict] = []


class IncidentIn(BaseModel):
    component: str
    title: str
    severity: str = "minor"


def check_token(authorization: str | None = Header(default=None)) -> None:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token manquant")
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=403, detail="Token invalide")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/components", dependencies=[Depends(check_token)])
def components(page: int = Query(1, ge=1), per_page: int = Query(4, ge=1, le=50)):
    pages = max(1, math.ceil(len(COMPONENTS) / per_page))
    if page > pages:
        raise HTTPException(status_code=404, detail="Page inexistante")
    start = (page - 1) * per_page
    return {"items": COMPONENTS[start:start + per_page], "page": page, "pages": pages,
            "total": len(COMPONENTS)}


@app.get("/incidents", dependencies=[Depends(check_token)])
def list_incidents():
    return INCIDENTS


@app.post("/incidents", status_code=201, dependencies=[Depends(check_token)])
def create_incident(incident: IncidentIn):
    item = {"id": len(INCIDENTS) + 1, **incident.model_dump(),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    INCIDENTS.append(item)
    return item


@app.get("/flaky")
def flaky():
    raise HTTPException(status_code=500, detail="Erreur interne simulée")


@app.get("/slow")
def slow():
    time.sleep(5)
    return {"status": "ok", "delay_s": 5}
