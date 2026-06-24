import asyncio
from loguru import logger
from typing import Optional
from kubernetes.pod_inspector import PodInspector
from kubernetes.logs_collector import LogsCollector
from kubernetes.events_analyzer import EventsAnalyzer
from kubernetes.deployment_inspector import DeploymentInspector
from kubernetes.network_inspector import NetworkInspector
from kubernetes.kubectl_executor import KubectlExecutor
import json


class InvestigationService:
    """
    Orchestrates all Kubernetes investigation components.
    Behaves like a junior DevOps engineer collecting debugging evidence.
    """

    def get_clusters(self) -> list:
        """Get all clusters/contexts from kubeconfig."""
        executor = KubectlExecutor()
        result = executor.run("config get-contexts -o name")
        if not result["success"]:
            return []
        contexts = [c.strip() for c in result["stdout"].split("\n") if c.strip()]

        # Get current context
        current_result = executor.run("config current-context")
        current = current_result["stdout"].strip() if current_result["success"] else ""

        cluster_list = []
        for ctx in contexts:
            # Get cluster info for each context
            info_result = executor.run(f"config get-contexts {ctx} --no-headers")
            cluster_list.append({
                "name": ctx,
                "is_current": ctx == current,
                "raw": info_result["stdout"]
            })

        return cluster_list

    async def run_investigation(self, context: Optional[str] = None) -> dict:
        """
        Run full investigation pipeline.

        Flow:
            Check Pods → Collect Logs → Analyze Events → Inspect Deployments → Check Networking

        Returns a single structured investigation payload.
        """
        logger.info(f"=== Starting Kubernetes Investigation (context: {context or 'default'}) ===")

        # Step 1: Check Pods
        logger.info("Step 1/5: Checking pods...")
        pod_inspector = PodInspector(context=context)
        pods = pod_inspector.inspect()

        # Step 2: Collect Logs (only for problematic pods)
        logger.info("Step 2/5: Collecting logs...")
        logs_collector = LogsCollector(context=context)
        problematic = pods.get("problematic_pods", [])
        logs = logs_collector.collect(problematic)

        # Step 3: Analyze Events
        logger.info("Step 3/5: Analyzing events...")
        events_analyzer = EventsAnalyzer(context=context)
        events = events_analyzer.analyze()

        # Step 4: Inspect Deployments
        logger.info("Step 4/5: Inspecting deployments...")
        deployment_inspector = DeploymentInspector(context=context)
        deployments = deployment_inspector.inspect()

        # Step 5: Check Networking
        logger.info("Step 5/5: Checking networking...")
        network_inspector = NetworkInspector(context=context)
        network = network_inspector.inspect()

        logger.info("=== Investigation complete ===")

        # Determine overall health
        has_issues = (
            not pods.get("healthy", True) or
            events.get("critical_count", 0) > 0 or
            not deployments.get("healthy", True) or
            network.get("issue_count", 0) > 0
        )

        return {
            "healthy": not has_issues,
            "context": context or "default",
            "pods": pods,
            "logs": logs,
            "events": events,
            "deployments": deployments,
            "network": network
        }
