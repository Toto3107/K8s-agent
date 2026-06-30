#!/bin/bash
# Apply all test failure scenarios to your Kubernetes cluster
# Usage: ./apply-scenarios.sh [scenario_number]
# Examples:
#   ./apply-scenarios.sh         # Apply all scenarios
#   ./apply-scenarios.sh 1       # Apply only scenario 1

set -e

SCENARIOS_DIR="$(dirname "$0")"

apply_scenario() {
  local file="$1"
  local name="$2"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Applying: $name"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  kubectl apply -f "$file"
  echo "✓ Applied $name"
}

cleanup() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Cleaning up all test scenarios..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  kubectl delete -f "$SCENARIOS_DIR/01-crashloop.yaml" --ignore-not-found=true
  kubectl delete -f "$SCENARIOS_DIR/02-imagepull.yaml" --ignore-not-found=true
  kubectl delete -f "$SCENARIOS_DIR/03-oomkilled.yaml" --ignore-not-found=true
  kubectl delete -f "$SCENARIOS_DIR/04-selector-mismatch.yaml" --ignore-not-found=true
  echo "✓ All scenarios cleaned up"
}

case "$1" in
  "1") apply_scenario "$SCENARIOS_DIR/01-crashloop.yaml" "Scenario 1: CrashLoopBackOff" ;;
  "2") apply_scenario "$SCENARIOS_DIR/02-imagepull.yaml" "Scenario 2: ImagePullBackOff" ;;
  "3") apply_scenario "$SCENARIOS_DIR/03-oomkilled.yaml" "Scenario 3: OOMKilled" ;;
  "4") apply_scenario "$SCENARIOS_DIR/04-selector-mismatch.yaml" "Scenario 4: Selector Mismatch" ;;
  "clean"|"cleanup") cleanup ;;
  *)
    apply_scenario "$SCENARIOS_DIR/01-crashloop.yaml" "Scenario 1: CrashLoopBackOff"
    apply_scenario "$SCENARIOS_DIR/02-imagepull.yaml" "Scenario 2: ImagePullBackOff"
    apply_scenario "$SCENARIOS_DIR/04-selector-mismatch.yaml" "Scenario 4: Selector Mismatch"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✓ All scenarios applied!"
    echo ""
    echo "Watch status: kubectl get pods -w"
    echo ""
    echo "Run investigation: curl -X POST http://localhost:8000/investigate"
    echo ""
    echo "Clean up: ./apply-scenarios.sh clean"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ;;
esac
