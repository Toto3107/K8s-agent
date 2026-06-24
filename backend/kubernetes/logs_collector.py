from loguru import logger
from kubernetes.kubectl_executor import KubectlExecutor
from typing import Optional, List


ERROR_KEYWORDS = [
    "exception", "error", "fatal", "failed", "panic",
    "connection refused", "timeout", "oomkilled",
    "cannot find", "no such file", "permission denied",
    "undefined", "missing", "env", "startup", "crash",
    "killed", "segfault", "traceback", "sqlexception"
]

MAX_LOG_LINES = 50


class LogsCollector:
    """
    Fetches and filters logs from problematic pods.
    Focuses on errors, exceptions, and startup failures.
    """

    def __init__(self, context: Optional[str] = None):
        self.kubectl = KubectlExecutor(context=context)

    def collect(self, problematic_pods: List[dict]) -> dict:
        """
        Collect logs from all problematic pods.

        Args:
            problematic_pods: List of pod dicts from PodInspector

        Returns:
            dict mapping pod name to filtered log output
        """
        logger.info(f"Collecting logs for {len(problematic_pods)} problematic pods...")

        if not problematic_pods:
            return {"message": "No problematic pods to collect logs from"}

        logs = {}
        for pod in problematic_pods[:5]:  # Limit to 5 pods max
            name = pod["name"]
            namespace = pod["namespace"]

            pod_logs = self._collect_pod_logs(name, namespace)
            if pod_logs:
                logs[f"{namespace}/{name}"] = pod_logs

        return logs

    def _collect_pod_logs(self, name: str, namespace: str) -> dict:
        """Collect and filter logs for a single pod."""
        result = {}

        # Try current logs
        current = self.kubectl.run(
            f"logs {name} -n {namespace} --tail=100 --all-containers=true"
        )
        if current["success"] and current["stdout"]:
            result["current"] = self._filter_logs(current["stdout"])

        # Try previous container logs (for crashlooping pods)
        previous = self.kubectl.run(
            f"logs {name} -n {namespace} --previous --tail=100 --all-containers=true"
        )
        if previous["success"] and previous["stdout"]:
            result["previous"] = self._filter_logs(previous["stdout"])

        if not result:
            result["message"] = f"No logs available for {name}"

        return result

    def _filter_logs(self, raw_logs: str) -> dict:
        """
        Filter logs to keep only error-relevant lines.
        Avoids returning thousands of lines.
        """
        lines = raw_logs.split("\n")
        error_lines = []
        all_lines = lines[-MAX_LOG_LINES:]  # Always keep last N lines

        for line in lines:
            lower = line.lower()
            if any(kw in lower for kw in ERROR_KEYWORDS):
                if line not in error_lines:
                    error_lines.append(line)

        return {
            "error_lines": error_lines[:30],
            "last_lines": all_lines,
            "total_lines": len(lines)
        }
