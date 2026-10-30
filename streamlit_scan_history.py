"""Per-user scan history stored in Supabase Postgres with Row Level Security."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from typing import Any

from app_supabase_auth import get_authenticated_client


def make_session_key(file_bytes: bytes, filename: str, prediction: str | None = None) -> str:
    payload = (
        file_bytes + b"\0" + str(filename).encode("utf-8")
        + b"\0" + str(prediction or "").encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


def save_scan(
    *,
    user_id: str,
    session_key: str,
    filename: str,
    prediction: str | None,
    confidence: float | None,
    status: str,
    top_predictions: list[dict[str, Any]] | None = None,
) -> int | None:
    client = get_authenticated_client()
    existing = (
        client.table("scan_history")
        .select("id")
        .eq("user_id", str(user_id))
        .eq("session_key", session_key)
        .limit(1)
        .execute()
    )
    if existing.data:
        return int(existing.data[0]["id"])

    response = client.table("scan_history").insert({
        "user_id": str(user_id),
        "session_key": session_key,
        "image_name": filename,
        "predicted_disease": prediction,
        "confidence": confidence,
        "status": status,
        "top_predictions": top_predictions or [],
    }).execute()
    return int(response.data[0]["id"]) if response.data else None


def list_scans(user_id: str | None, limit: int = 50) -> list[dict[str, Any]]:
    if not user_id:
        return []
    safe_limit = max(1, min(int(limit), 200))
    response = (
        get_authenticated_client()
        .table("scan_history")
        .select("id,user_id,image_name,predicted_disease,confidence,status,top_predictions,created_at")
        .eq("user_id", str(user_id))
        .order("created_at", desc=True)
        .limit(safe_limit)
        .execute()
    )
    scans = []
    for row in response.data or []:
        top = row.get("top_predictions") or []
        if isinstance(top, str):
            try:
                top = json.loads(top)
            except Exception:
                top = []
        scans.append({
            "id": int(row["id"]),
            "filename": row.get("image_name") or "Unknown image",
            "prediction": row.get("predicted_disease"),
            "confidence": float(row["confidence"]) if row.get("confidence") is not None else None,
            "status": row.get("status") or ("completed" if row.get("predicted_disease") else "rejected"),
            "top_predictions": top,
            "created_at": row.get("created_at") or "",
        })
    return scans


def dashboard_stats(scans: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [scan for scan in scans if scan.get("status") == "completed"]
    rejected = [scan for scan in scans if scan.get("status") != "completed"]
    confidences = [scan["confidence"] for scan in completed if scan.get("confidence") is not None]
    healthy = [
        scan for scan in completed
        if scan.get("prediction") and "healthy" in str(scan["prediction"]).lower()
    ]
    return {
        "total": len(scans),
        "completed": len(completed),
        "rejected": len(rejected),
        "average_confidence": round(sum(confidences) / len(confidences), 2) if confidences else None,
        "healthy": len(healthy),
        "condition_detected": len([scan for scan in completed if scan not in healthy]),
    }


def scans_to_csv(scans: list[dict[str, Any]]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Filename", "Prediction", "Confidence (%)", "Status", "Created At"])
    for scan in scans:
        writer.writerow([
            scan["id"], scan["filename"], scan.get("prediction") or "",
            scan.get("confidence") if scan.get("confidence") is not None else "",
            scan.get("status", ""), scan.get("created_at", ""),
        ])
    return output.getvalue().encode("utf-8")

