"""
main.py
=======
Layer 5 entry point — assembles all group routers into a single FastAPI app
and exposes a dynamically filtered GPT-surface OpenAPI schema.

Key design decision (the agreed correction):
  We do NOT hand-maintain a separate openapi_gpt.json. The full app remains the
  single source of truth. The GPT surface is derived at runtime by filtering the
  live OpenAPI schema down to a whitelisted set of paths, so the GPT spec can
  never drift from the backend.

  - Swagger / full OpenAPI:  GET /openapi.json   (all endpoints)
  - GPT Builder OpenAPI:     GET /openapi-gpt.json (<= 30 operations)
"""

import copy

from fastapi import FastAPI
from fastapi.responses import JSONResponse

import group1_methodologist
import group2_protocol
import group3_hepatology
import group4_intelligence


import os

API_VERSION = "2.0.0"
SYSTEM_NAME = "Hepatology Research OS"

SERVER_URL = os.getenv(
    "SERVER_URL",
    "https://clinicaltrialapi-dqml.onrender.com"
)

from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Rachel Hepatology Research OS",
    version=API_VERSION,
    servers=[
        {
            "url": SERVER_URL
        }
    ],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        servers=app.servers,
    )
    schema["openapi"] = "3.0.3"
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi

# =========================
# Router Assembly
# =========================
# Registry maps a logical layer name to its router, so health/validation can
# report live endpoint counts without anyone hand-maintaining numbers.

ROUTERS = {
    "methodologist": group1_methodologist.router,
    "protocol": group2_protocol.router,
    "hepatology": group3_hepatology.router,
    "intelligence": group4_intelligence.router,
}

for router in ROUTERS.values():
    app.include_router(router)


def _router_endpoint_counts() -> dict:
    """Count distinct routed paths per layer, computed live from the routers."""
    return {
        name: len({getattr(r, "path", None) for r in router.routes} - {None})
        for name, router in ROUTERS.items()
    }

GPT_SURFACE_PATHS = {

    # =====================
    # Foundation Layer
    # =====================

    "/orchestrator/query-intelligence",
    "/orchestrator/evidence-review",
    "/orchestrator/trial-landscape",
    "/orchestrator/unmet-need",
    "/orchestrator/analogous-trials",

    # =====================
    # Methodologist Layer
    # =====================

    "/orchestrator/design-discussion",
    "/orchestrator/design-selection",
    "/orchestrator/design-architecture",
    "/orchestrator/design-tradeoff",
    "/orchestrator/advanced-statistical-design",

    # =====================
    # Endpoint Intelligence
    # =====================

    "/orchestrator/endpoint-intelligence",
    "/orchestrator/design-patterns",

    # =====================
    # Statistics
    # =====================

    "/sample-size/proportion",
    "/sample-size/ttest",
    "/sample-size/survival",

    "/protocol/estimand",

    "/sap/statistical-analysis-plan",

    # =====================
    # Hepatology Research OS
    # =====================

    "/orchestrator/hepatology-intelligence",
    "/orchestrator/research-opportunity",
    "/orchestrator/precision-hepatology",
    "/orchestrator/future-methodology",

    # Disease Intelligence

    "/orchestrator/disease-knowledge",

    # =====================
    # Trial Planning
    # =====================

    "/orchestrator/study-concept",
    "/orchestrator/feasibility-analysis",
    "/orchestrator/budget-estimation",

    # =====================
    # Protocol Generation
    # =====================

    "/protocol/endpoints",

    # =====================
    # Operations
    # =====================

    "/orchestrator/clinicaltrialsgov-package-v2",
    "/orchestrator/crf-builder",
    "/orchestrator/redcap-builder-v3",
}

ADVANCED_GPT_SURFACE_PATHS = {

    # Noninferiority

    "/sample-size/noninferiority/binary",
    "/sample-size/noninferiority/continuous",
    "/sample-size/noninferiority/survival",

    # Methodologist

    "/orchestrator/assumption-analysis",
    "/orchestrator/bias-analysis",
    "/orchestrator/methodologist-critique",
    "/orchestrator/statistical-consequence",

    # Target Trial Emulation

    "/orchestrator/tte-design",
    "/orchestrator/tte-design-v2",
    "/orchestrator/tte-design-v3",

    # Advanced Statistics

    "/orchestrator/advanced-sap",

    # Interim Analysis

    "/orchestrator/interim-analysis",
    "/orchestrator/interim-analysis-v2",
    "/orchestrator/interim-analysis-v3",

    # Operations

    "/orchestrator/brochure-generator",

    "/orchestrator/redcap-builder-v2",

    "/orchestrator/clinicaltrialsgov-package",

    # Intelligence Update

    "/orchestrator/hepatology-intelligence-update",
}

# =========================
# Root Endpoint
# =========================

@app.get("/")
def root():
    return {"message": "Rachel Clinical Trial API"}

@app.get("/")
def root():
    return {
        "message": "Rachel Clinical Trial API"
    }



@app.get("/health", tags=["System"])
def health():
    """
    System-validation endpoint.

    Returns liveness plus live per-layer endpoint counts, so a successful
    response also confirms every router was assembled. Counts are computed
    from the live routers, never hand-maintained.
    """
    counts = _router_endpoint_counts()
    return {
        "status": "ok",
        "version": API_VERSION,
        "system": SYSTEM_NAME,
        "modules": {name: (count > 0) for name, count in counts.items()},
        "routers": counts,
        "total_endpoints": sum(counts.values()),
    }


# =========================
# Dynamic GPT OpenAPI Schema
# =========================

@app.get("/openapi-gpt.json", include_in_schema=False)
def openapi_gpt():
    """
    Return a filtered copy of the live OpenAPI schema containing only the
    GPT_SURFACE_PATHS. Generated fresh from app.openapi() on every call, so it
    always reflects the current backend (no static drift).
    """
    full_schema = app.openapi()
    gpt_schema = copy.deepcopy(full_schema)

    # Keep only whitelisted paths
    gpt_schema["paths"] = {
        path: item
        for path, item in full_schema["paths"].items()
        if path in GPT_SURFACE_PATHS
    }

    # Prune component schemas down to those still referenced, to keep the
    # GPT spec small. (Simple reachability pass over $ref strings.)
    gpt_schema = _prune_unused_components(gpt_schema)

    gpt_schema["info"] = dict(full_schema.get("info", {}))
    gpt_schema["info"]["title"] = "Hepatology Research OS (GPT Surface)"

    return JSONResponse(gpt_schema)

@app.get("/openapi-gpt-advanced.json", include_in_schema=False)
def openapi_gpt_advanced():

    full_schema = app.openapi()

    advanced_schema = copy.deepcopy(full_schema)

    advanced_schema["paths"] = {
        path: item
        for path, item in full_schema["paths"].items()
        if path in ADVANCED_GPT_SURFACE_PATHS
    }

    advanced_schema = _prune_unused_components(
        advanced_schema
    )

    advanced_schema["info"] = dict(
        full_schema.get("info", {})
    )

    advanced_schema["info"]["title"] = (
        "Hepatology Research OS (Advanced GPT Surface)"
    )

    return JSONResponse(
        advanced_schema
    )

def _prune_unused_components(schema: dict) -> dict:
    """Remove component schemas not reachable from the retained paths."""
    components = schema.get("components", {}).get("schemas", {})
    if not components:
        return schema

    import json
    import re

    ref_pattern = re.compile(r"#/components/schemas/([A-Za-z0-9_.\-]+)")

    def refs_in(obj) -> set:
        return set(ref_pattern.findall(json.dumps(obj)))

    # Seed with refs used by the retained paths.
    reachable = refs_in(schema.get("paths", {}))

    # Transitively expand: a kept schema may reference other schemas.
    changed = True
    while changed:
        changed = False
        for name in list(reachable):
            if name in components:
                new_refs = refs_in(components[name])
                if not new_refs.issubset(reachable):
                    reachable |= new_refs
                    changed = True

    schema["components"]["schemas"] = {
        name: defn
        for name, defn in components.items()
        if name in reachable
    }
    return schema
