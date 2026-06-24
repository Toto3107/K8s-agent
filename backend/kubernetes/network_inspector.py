import json
from loguru import logger
from kubernetes.kubectl_executor import KubectlExecutor
from typing import Optional


class NetworkInspector:
    """
    Inspects services and endpoints to detect networking issues.
    Checks for selector mismatches and missing endpoints.
    """

    def __init__(self, context: Optional[str] = None):
        self.kubectl = KubectlExecutor(context=context)

    def inspect(self) -> dict:
        """
        Check services and endpoints for issues.
        Returns structured networking findings.
        """
        logger.info("Inspecting network/services...")

        services_result = self.kubectl.run("get services -A -o json")
        endpoints_result = self.kubectl.run("get endpoints -A -o json")

        issues = []
        services_data = []

        if not services_result["success"]:
            return {
                "error": services_result["stderr"],
                "services": [],
                "issues": []
            }

        try:
            services = json.loads(services_result["stdout"]).get("items", [])
            endpoints_map = {}

            if endpoints_result["success"]:
                endpoints = json.loads(endpoints_result["stdout"]).get("items", [])
                for ep in endpoints:
                    key = f"{ep['metadata']['namespace']}/{ep['metadata']['name']}"
                    subsets = ep.get("subsets", [])
                    # Count ready addresses
                    ready_count = sum(
                        len(s.get("addresses", [])) for s in subsets
                    )
                    endpoints_map[key] = ready_count

            for svc in services:
                name = svc["metadata"]["name"]
                namespace = svc["metadata"]["namespace"]
                svc_type = svc["spec"].get("type", "ClusterIP")
                selector = svc["spec"].get("selector", {})

                if name == "kubernetes":
                    continue  # Skip built-in service

                key = f"{namespace}/{name}"
                ready_endpoints = endpoints_map.get(key, 0)

                service_info = {
                    "name": name,
                    "namespace": namespace,
                    "type": svc_type,
                    "selector": selector,
                    "ready_endpoints": ready_endpoints
                }
                services_data.append(service_info)

                # No selector on non-headless service = potential issue
                if not selector and svc_type not in ["ExternalName"]:
                    issues.append({
                        "service": f"{namespace}/{name}",
                        "issue": "No selector defined",
                        "severity": "warning"
                    })

                # Service has selector but zero ready endpoints
                if selector and ready_endpoints == 0:
                    issues.append({
                        "service": f"{namespace}/{name}",
                        "issue": "Selector mismatch or no ready pods — zero endpoints",
                        "severity": "critical"
                    })

            return {
                "total_services": len(services_data),
                "services": services_data[:20],
                "issues": issues,
                "issue_count": len(issues)
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse network JSON: {e}")
            return {
                "error": "Failed to parse network data",
                "services": [],
                "issues": []
            }
