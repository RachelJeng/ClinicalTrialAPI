"""
export_openapi.py
=================
Offline exporter for OpenAPI specs.

Generates, from the single live app (no duplicated spec definitions):
  - openapi_full.json          : every endpoint (Swagger / full surface)
  - openapi_methodologist.json : Layer 1 endpoints
  - openapi_protocol.json      : Layer 2 endpoints
  - openapi_hepatology.json    : Layer 3 endpoints
  - openapi_intelligence.json  : Layer 4 endpoints
  - openapi_gpt.json           : GPT surface (<= 30 ops), via main.GPT_SURFACE_PATHS

Run:  python export_openapi.py
"""

import copy
import json

import group1_methodologist
import group2_protocol
import group3_hepatology
import group4_intelligence
from main import app, GPT_SURFACE_PATHS, _prune_unused_components


def _paths_for_router(router) -> set:
    """Collect the path strings declared on a given APIRouter."""
    paths = set()
    for route in router.routes:
        path = getattr(route, "path", None)
        if path:
            paths.add(path)
    return paths


def _subset_schema(full_schema: dict, keep_paths: set, title: str) -> dict:
    sub = copy.deepcopy(full_schema)
    sub["paths"] = {
        path: item
        for path, item in full_schema["paths"].items()
        if path in keep_paths
    }
    sub = _prune_unused_components(sub)
    sub["info"] = dict(full_schema.get("info", {}))
    sub["info"]["title"] = title
    return sub


def main():
    full_schema = app.openapi()

    # Full spec
    _write("openapi_full.json", full_schema)

    # Per-layer specs
    layer_map = {
        "openapi_methodologist.json": (
            "Methodologist OS",
            _paths_for_router(group1_methodologist.router),
        ),
        "openapi_protocol.json": (
            "Protocol Development",
            _paths_for_router(group2_protocol.router),
        ),
        "openapi_hepatology.json": (
            "Hepatology Research OS",
            _paths_for_router(group3_hepatology.router),
        ),
        "openapi_intelligence.json": (
            "Strategic Intelligence Layer",
            _paths_for_router(group4_intelligence.router),
        ),
    }

    for filename, (title, paths) in layer_map.items():
        _write(filename, _subset_schema(full_schema, paths, title))

    # GPT surface spec
    gpt_schema = _subset_schema(
        full_schema,
        GPT_SURFACE_PATHS,
        "Hepatology Research OS (GPT Surface)",
    )
    _write("openapi_gpt.json", gpt_schema)

    # Sanity check on GPT operation count
    op_count = sum(len(item) for item in gpt_schema["paths"].values())
    print(f"\nGPT surface operation count: {op_count} (limit: 30)")
    if op_count > 30:
        print("WARNING: GPT surface exceeds 30 operations — trim "
              "GPT_SURFACE_PATHS in main.py")


def _write(filename: str, schema: dict):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    n_paths = len(schema.get("paths", {}))
    print(f"Wrote {filename:32s} ({n_paths} paths)")


if __name__ == "__main__":
    main()
