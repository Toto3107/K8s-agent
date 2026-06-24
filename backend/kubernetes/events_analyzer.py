import json
from loguru import logger
from kubernetes.kubectl_executor import KubectlExecutor
from typing import Optional


CRITICAL_REASONS = [
    "FailedScheduling",
    "BackOff",
    "CrashLoopBackOff",
    "FailedMount",
    "FailedPull",
    "ErrImagePull",
    "Unhealthy",
    "OOMKilling",
    "NodeNotReady",
    "FailedCreate",
    "FailedAttachVolume",
    "NetworkNotReady",
    "FailedBinding"
]


class EventsAnalyzer:
    """
    Reads Kubernetes events and surfaces critical warnings.
    Focuses on scheduling, image pull, and health failures.
    """

    def __init__(self, context: Optional[str] = None):
        self.kubectl = KubectlExecutor(context=context)

    def analyze(self) -> dict:
        """
        Fetch and analyze Kubernetes events.
        Returns summarized findings.
        """
        logger.info("Analyzing Kubernetes events...")
        result = self.kubectl.run("get events -A -o json --sort-by='.lastTimestamp'")

        if not result["success"]:
            return {
                "error": result["stderr"],
                "critical_events": [],
                "total_events": 0
            }

        try:
            data = json.loads(result["stdout"])
            events = data.get("items", [])

            critical = []
            warnings = []

            for event in events:
                event_type = event.get("type", "Normal")
                reason = event.get("reason", "")
                message = event.get("message", "")
                namespace = event["metadata"].get("namespace", "")
                name = event["metadata"].get("name", "")
                count = event.get("count", 1)
                last_time = event.get("lastTimestamp", "")

                involved = event.get("involvedObject", {})
                object_name = involved.get("name", "")
                object_kind = involved.get("kind", "")

                entry = {
                    "reason": reason,
                    "message": message,
                    "namespace": namespace,
                    "object": f"{object_kind}/{object_name}",
                    "count": count,
                    "last_seen": last_time
                }

                if reason in CRITICAL_REASONS:
                    critical.append(entry)
                elif event_type == "Warning":
                    warnings.append(entry)

            return {
                "total_events": len(events),
                "critical_events": critical[:20],
                "warnings": warnings[:10],
                "critical_count": len(critical)
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse events JSON: {e}")
            return {
                "error": "Failed to parse events",
                "critical_events": [],
                "total_events": 0
            }
