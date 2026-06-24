import httpx
import json
from loguru import logger
from core.config import settings


SYSTEM_PROMPT = """You are a Senior Kubernetes SRE with 10 years of experience troubleshooting production clusters.

Your job is to analyze Kubernetes investigation data and provide a clear, actionable diagnosis.

You MUST respond with ONLY valid JSON in this exact structure:
{
  "root_cause": "One clear sentence describing the root cause",
  "explanation": "2-3 sentence technical explanation of what is happening and why",
  "fix": "Clear step-by-step fix instructions",
  "kubectl_commands": ["command1", "command2"],
  "prevention": "One recommendation to prevent this in the future",
  "confidence": 85,
  "severity": "critical|high|medium|low",
  "affected_resources": ["namespace/resource1", "namespace/resource2"]
}

Rules:
- Be specific, not generic. Reference actual pod names, namespaces, error messages.
- kubectl_commands must be real, runnable commands.
- confidence is 0-100 based on how clearly the evidence points to a cause.
- If the cluster is healthy, set root_cause to "No issues detected" and confidence to 95.
- Never guess. Only diagnose based on evidence provided.
- Do not include markdown or backticks in your response. Only valid JSON.
"""


class AIService:
    """
    AI reasoning layer powered by OpenRouter.
    Analyzes Kubernetes investigation evidence and generates diagnosis.
    """

    async def analyze(self, evidence: dict) -> dict:
        """
        Send investigation evidence to LLM for root cause analysis.

        Args:
            evidence: Full investigation payload from InvestigationService

        Returns:
            Structured diagnosis dict
        """
        if not settings.openrouter_api_key:
            logger.warning("No OPENROUTER_API_KEY set - returning mock diagnosis")
            return self._mock_diagnosis(evidence)

        prompt = self._build_prompt(evidence)
        logger.info(f"Sending evidence to AI ({settings.openrouter_model})...")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/ai-kubernetes-agent",
                        "X-Title": "AI Kubernetes Agent"
                    },
                    json={
                        "model": settings.openrouter_model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1000
                    }
                )

                if response.status_code != 200:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return self._error_diagnosis(f"LLM API returned {response.status_code}")

                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Parse JSON response
                try:
                    # Strip markdown fences if model added them
                    clean = content.strip().strip("```json").strip("```").strip()
                    return json.loads(clean)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse AI response as JSON: {content}")
                    return {
                        "root_cause": "AI response parse error",
                        "explanation": content[:500],
                        "fix": "Please review the raw investigation data",
                        "kubectl_commands": [],
                        "prevention": "",
                        "confidence": 0,
                        "severity": "unknown",
                        "affected_resources": []
                    }

        except httpx.TimeoutException:
            logger.error("OpenRouter request timed out")
            return self._error_diagnosis("LLM request timed out after 60 seconds")
        except Exception as e:
            logger.error(f"AI service error: {e}")
            return self._error_diagnosis(str(e))

    def _build_prompt(self, evidence: dict) -> str:
        """Build a structured prompt from investigation evidence."""
        pods = evidence.get("pods", {})
        events = evidence.get("events", {})
        deployments = evidence.get("deployments", {})
        network = evidence.get("network", {})
        logs = evidence.get("logs", {})

        problematic_pods = pods.get("problematic_pods", [])
        critical_events = events.get("critical_events", [])
        unhealthy_deps = deployments.get("unhealthy_deployments", [])
        network_issues = network.get("issues", [])

        # Summarize logs for prompt (keep it concise)
        log_summary = {}
        for pod_key, pod_logs in logs.items():
            if isinstance(pod_logs, dict):
                errors = pod_logs.get("error_lines", [])
                log_summary[pod_key] = errors[:10] if errors else ["No error lines found"]

        prompt = f"""Analyze this Kubernetes cluster investigation data and diagnose the root cause.

CLUSTER CONTEXT: {evidence.get("context", "default")}
OVERALL HEALTHY: {evidence.get("healthy", "unknown")}

POD STATUS:
- Total pods: {pods.get("total_pods", 0)}
- Problematic pods: {json.dumps(problematic_pods, indent=2)}

CRITICAL EVENTS ({len(critical_events)} found):
{json.dumps(critical_events[:10], indent=2)}

DEPLOYMENT HEALTH:
- Total deployments: {deployments.get("total_deployments", 0)}
- Unhealthy deployments: {json.dumps(unhealthy_deps, indent=2)}

NETWORK ISSUES:
{json.dumps(network_issues, indent=2)}

ERROR LOGS:
{json.dumps(log_summary, indent=2)}

Based on this evidence, provide your diagnosis in the required JSON format.
"""
        return prompt

    def _mock_diagnosis(self, evidence: dict) -> dict:
        """Return a mock diagnosis when no API key is configured."""
        pods = evidence.get("pods", {})
        problematic = pods.get("problematic_pods", [])

        if not problematic and evidence.get("healthy", True):
            return {
                "root_cause": "No issues detected",
                "explanation": "The cluster appears healthy. No problematic pods, critical events, or deployment failures were found.",
                "fix": "No action required. Continue monitoring.",
                "kubectl_commands": ["kubectl get pods -A", "kubectl top nodes"],
                "prevention": "Set up monitoring alerts for pod restart counts and deployment availability.",
                "confidence": 95,
                "severity": "low",
                "affected_resources": []
            }

        # Build a simple heuristic diagnosis based on pod statuses
        first_pod = problematic[0] if problematic else {}
        status = first_pod.get("status", "Unknown")
        name = first_pod.get("name", "unknown-pod")
        ns = first_pod.get("namespace", "default")

        diagnoses = {
            "CrashLoopBackOff": {
                "root_cause": f"Pod {ns}/{name} is in CrashLoopBackOff — application is crashing on startup",
                "explanation": "The container starts, crashes, and Kubernetes keeps restarting it. Common causes: missing environment variables, misconfigured secrets, or application bugs.",
                "fix": "1. Check pod logs: kubectl logs {name} -n {ns} --previous\n2. Verify all environment variables and secrets are mounted correctly\n3. Check application startup code for errors",
                "kubectl_commands": [f"kubectl logs {name} -n {ns} --previous", f"kubectl describe pod {name} -n {ns}"],
                "prevention": "Add readiness and liveness probes. Use ConfigMap/Secret validation at deploy time.",
                "confidence": 80,
                "severity": "critical",
                "affected_resources": [f"{ns}/{name}"]
            },
            "ImagePullBackOff": {
                "root_cause": f"Pod {ns}/{name} cannot pull its container image",
                "explanation": "Kubernetes is unable to pull the container image. This is usually due to a wrong image tag, private registry without credentials, or network issues.",
                "fix": "1. Check the image name and tag in the deployment\n2. Verify image registry credentials (imagePullSecrets)\n3. kubectl describe pod {name} -n {ns} for the exact error",
                "kubectl_commands": [f"kubectl describe pod {name} -n {ns}", f"kubectl edit deployment -n {ns}"],
                "prevention": "Use image digest pinning instead of :latest tags. Set up registry credential rotation.",
                "confidence": 90,
                "severity": "high",
                "affected_resources": [f"{ns}/{name}"]
            },
            "OOMKilled": {
                "root_cause": f"Pod {ns}/{name} was killed due to Out-Of-Memory (OOMKilled)",
                "explanation": "The container exceeded its memory limit and was terminated by the kernel OOM killer. The memory limit is too low for the application's actual usage.",
                "fix": "1. Increase memory limits in the deployment spec\n2. Profile application memory usage\n3. kubectl edit deployment -n {ns} and increase resources.limits.memory",
                "kubectl_commands": [f"kubectl top pod {name} -n {ns}", f"kubectl edit deployment -n {ns}"],
                "prevention": "Use Vertical Pod Autoscaler (VPA) to automatically tune memory limits.",
                "confidence": 95,
                "severity": "high",
                "affected_resources": [f"{ns}/{name}"]
            }
        }

        if status in diagnoses:
            return diagnoses[status]

        return {
            "root_cause": f"Pod {ns}/{name} is in {status} state",
            "explanation": f"The pod is not running normally. Status: {status}. Review pod events and logs for details.",
            "fix": f"kubectl describe pod {name} -n {ns}\nkubectl logs {name} -n {ns}",
            "kubectl_commands": [f"kubectl describe pod {name} -n {ns}", f"kubectl logs {name} -n {ns}"],
            "prevention": "Set up monitoring and alerting on pod status changes.",
            "confidence": 60,
            "severity": "medium",
            "affected_resources": [f"{ns}/{name}"]
        }

    def _error_diagnosis(self, error: str) -> dict:
        return {
            "root_cause": "AI analysis unavailable",
            "explanation": f"Could not complete AI analysis: {error}",
            "fix": "Review the raw investigation data manually or check your OPENROUTER_API_KEY.",
            "kubectl_commands": [],
            "prevention": "",
            "confidence": 0,
            "severity": "unknown",
            "affected_resources": []
        }
