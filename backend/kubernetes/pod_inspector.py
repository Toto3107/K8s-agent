import json
from loguru import logger
from kubernetes.kubectl_executor import KubectlExecutor
from typing import Optional

UNHEALTHY_STATUSES = [
    "CrashLoopBackOff",
    "ImagePullBackOff",
    "ErrImagePull",
    "Pending",
    "Error",
    "OOMKilled",
    "CreateContainerConfigError",
    "ContainerCreating",
    "Terminating",
    "Unknown",
    "Init:CrashLoopBackOff",
    "Init:Error"
]


class PodInspector:
    """
    Inspects pods across all namespaces.
    Detects unhealthy pods and returns structured findings.
    """

    def __init__(self, context: Optional[str] = None):
        self.kubectl = KubectlExecutor(context=context)

    def inspect(self) -> dict:
        """
        Get pod status across all namespaces.
        Returns structured JSON with healthy/problematic pods.
        """
        logger.info("Inspecting pods...")
        result = self.kubectl.run("get pods -A -o json")

        if not result["success"]:
            return {
                "error": result["stderr"],
                "healthy": None,
                "total_pods": 0,
                "problematic_pods": [],
                "raw_error": result["stderr"]
            }

        try:
            data = json.loads(result["stdout"])
            pods = data.get("items", [])

            problematic = []
            total = len(pods)

            for pod in pods:
                name = pod["metadata"]["name"]
                namespace = pod["metadata"]["namespace"]
                phase = pod["status"].get("phase", "Unknown")

                # Check container statuses for detailed state
                container_statuses = pod["status"].get("containerStatuses", [])
                init_statuses = pod["status"].get("initContainerStatuses", [])
                all_statuses = container_statuses + init_statuses

                pod_status = phase
                restart_count = 0
                is_problematic = False

                for cs in all_statuses:
                    restart_count += cs.get("restartCount", 0)
                    state = cs.get("state", {})

                    # Check waiting state
                    waiting = state.get("waiting", {})
                    if waiting:
                        reason = waiting.get("reason", "")
                        if reason in UNHEALTHY_STATUSES:
                            pod_status = reason
                            is_problematic = True

                    # Check terminated state
                    terminated = state.get("terminated", {})
                    if terminated:
                        reason = terminated.get("reason", "")
                        if reason in ["OOMKilled", "Error"]:
                            pod_status = reason
                            is_problematic = True

                # Also catch pods stuck in non-Running phase
                if phase not in ["Running", "Succeeded"] and phase != "Unknown":
                    if not is_problematic:
                        is_problematic = True
                        pod_status = phase

                if is_problematic:
                    problematic.append({
                        "name": name,
                        "namespace": namespace,
                        "status": pod_status,
                        "phase": phase,
                        "restart_count": restart_count
                    })

            return {
                "healthy": len(problematic) == 0,
                "total_pods": total,
                "problematic_pods": problematic,
                "problematic_count": len(problematic)
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse pod JSON: {e}")
            return {
                "error": "Failed to parse kubectl output",
                "healthy": None,
                "total_pods": 0,
                "problematic_pods": []
            }
