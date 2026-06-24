from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from services.investigation_service import InvestigationService
from services.ai_service import AIService
from core.config import settings
from typing import Optional

router = APIRouter()
investigation_service = InvestigationService()
ai_service = AIService()


@router.get("/clusters")
async def get_clusters():
    """List all Kubernetes clusters from kubeconfig."""
    try:
        clusters = investigation_service.get_clusters()
        return {"status": "success", "clusters": clusters}
    except Exception as e:
        logger.error(f"Failed to get clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/investigate")
async def investigate(context: Optional[str] = Query(default=None, description="Kubernetes context/cluster name")):
    """Run full Kubernetes investigation and AI diagnosis."""
    try:
        logger.info(f"Starting investigation for context: {context or 'default'}")

        # Step 1: Collect Kubernetes evidence
        evidence = await investigation_service.run_investigation(context=context)

        # Step 2: AI reasoning
        diagnosis = await ai_service.analyze(evidence)

        return {
            "status": "success",
            "context": context or "default",
            "investigation": evidence,
            "diagnosis": diagnosis
        }

    except Exception as e:
        logger.error(f"Investigation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Investigation failed",
                "message": str(e),
                "hint": "Verify kubeconfig path and cluster access. Run: kubectl cluster-info"
            }
        )
