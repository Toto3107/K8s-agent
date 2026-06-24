import subprocess
import shlex
from loguru import logger
from typing import Optional
from core.config import settings


class KubectlExecutor:
    """
    Safe, reusable wrapper to execute kubectl commands via subprocess.
    Returns structured output so callers can handle errors cleanly.
    """

    def __init__(self, context: Optional[str] = None):
        self.context = context
        self.kubeconfig = settings.kubeconfig_path

    def run(self, command: str) -> dict:
        """
        Execute a kubectl command.

        Args:
            command: kubectl command string (e.g., "get pods -A")

        Returns:
            dict with keys: success, stdout, stderr, command
        """
        full_command = self._build_command(command)
        logger.info(f"Running: {' '.join(full_command)}")

        try:
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            if not success:
                logger.warning(f"kubectl failed: {result.stderr.strip()}")

            return {
                "success": success,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "command": " ".join(full_command),
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            logger.error(f"kubectl command timed out: {command}")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 30 seconds",
                "command": command,
                "returncode": -1
            }
        except FileNotFoundError:
            logger.error("kubectl not found. Is it installed?")
            return {
                "success": False,
                "stdout": "",
                "stderr": "kubectl not found. Please install kubectl.",
                "command": command,
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"Unexpected error running kubectl: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "command": command,
                "returncode": -1
            }

    def _build_command(self, command: str) -> list:
        """Build the full kubectl command with context and kubeconfig flags."""
        parts = ["kubectl"] + shlex.split(command)

        if self.context:
            parts += ["--context", self.context]

        if self.kubeconfig:
            parts += ["--kubeconfig", self.kubeconfig]

        return parts
