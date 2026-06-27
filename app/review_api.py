"""Review API — endpoints cho màn duyệt HITL (Phase 3).

GET  /api/review/proposals?tenant=...           — list đề xuất proposed (tenant-scope)
GET  /api/review/proposals/{id}/suggest         — AI prefer assignee (skill match)
POST /api/review/proposals/{id}/approve         — chốt & giao (tạo task)
POST /api/review/proposals/{id}/reject          — bỏ
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.review_service import ReviewService

router = APIRouter(prefix="/api/review", tags=["Review (HITL)"])
_svc = None


def svc():
    global _svc
    if _svc is None:
        _svc = ReviewService()
    return _svc


class ApproveIn(BaseModel):
    assignee: str
    approved_by: Optional[str] = None
    description: Optional[str] = None
    due: Optional[str] = None
    priority: Optional[str] = None


class RejectIn(BaseModel):
    approved_by: Optional[str] = None


@router.get("/proposals")
def list_proposals(tenant: str = Query(..., description="tenant/user id")):
    items = svc().list_pending(tenant)
    return {"count": len(items), "items": items}


@router.get("/proposals/{proposal_id}/suggest")
def suggest(proposal_id: str):
    prop = svc().proposals.get(proposal_id)
    if not prop:
        raise HTTPException(404, "proposal không tồn tại")
    return {"suggestions": svc().suggest_assignees(prop)}


@router.post("/proposals/{proposal_id}/approve")
def approve(proposal_id: str, body: ApproveIn):
    try:
        return svc().approve(proposal_id, assignee=body.assignee, approved_by=body.approved_by,
                             description=body.description, due=body.due, priority=body.priority)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/proposals/{proposal_id}/reject")
def reject(proposal_id: str, body: RejectIn):
    r = svc().reject(proposal_id, approved_by=body.approved_by)
    if not r:
        raise HTTPException(404, "proposal không tồn tại")
    return r
