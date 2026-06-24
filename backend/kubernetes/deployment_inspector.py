import json
from loguru import logger
from kubernetes.kubectl_executor import KubectlExecutor
from typing import Optional


class DeploymentInspector:
    """
    Inspects all deployments for availability and rollout failures.
    """

    def __init__(self, context: Optional[str] = None):
        self.kubectl = KubectlExecutor(context=context)

    def inspect(self) -> dict:
        """
        Check all deployments for health issues.
        Returns unhealthy deployments with details.
        """
        logger.info("Inspecting deployments...")
        result = self.kubectl.run("get deployments -A -o json")

        if not result["success"]:
            return {
                "error": result["stderr"],
                "total_deployments": 0,
                "unhealthy_deployments": []
            }

        try:
            data = json.loads(result["stdout"])
            deployments = data.get("items", [])

            unhealthy = []
            total = len(deployments)

            for dep in deployments:
                name = dep["metadata"]["name"]
                namespace = dep["metadata"]["namespace"]
                spec = dep.get("spec", {})
                status = dep.get("status", {})

                desired = spec.get("replicas", 0)
                available = status.get("availableReplicas", 0)
                ready = status.get("readyReplicas", 0)
                unavailable = status.get("unavailableReplicas", 0)

                conditions = status.get("conditions", [])
                condition_issues = []
                for cond in conditions:
                    if cond.get("type") == "Available" and cond.get("status") == "False":
                        condition_issues.append({
                            "type": cond.get("type"),
                            "reason": cond.get("reason"),
                            "message": cond.get("message")
                        })
                    if cond.get("type") == "Progressing" and cond.get("reason") == "ProgressDeadlineExceeded":
                        condition_issues.append({
                            "type": cond.get("type"),
                            "reason": cond.get("reason"),
                            "message": cond.get("message")
                        })

                is_unhealthy = (
                    available < desired or
                    unavailable > 0 or
                    len(condition_issues) > 0
                )

                if is_unhealthy:
                    unhealthy.append({
                        "name": name,
                        "namespace": namespace,
                        "desired_replicas": desired,
                        "available_replicas": available,
                        "ready_replicas": ready,
                        "unavailable_replicas": unavailable,
                        "conditions": condition_issues
                    })

            return {
                "total_deployments": total,
                "unhealthy_deployments": unhealthy,
                "unhealthy_count": len(unhealthy),
                "healthy": len(unhealthy) == 0
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse deployment JSON: {e}")
            return {
                "error": "Failed to parse deployments",
                "total_deployments": 0,
                "unhealthy_deployments": []
            }
