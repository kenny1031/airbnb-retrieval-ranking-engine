#!/usr/bin/env bash
set -Eeuo pipefail

# Usage:
#   bash scripts/run_tests.sh
#   bash scripts/run_tests.sh unit
#   bash scripts/run_tests.sh integration
#
# Assumptions:
# - run from project root or anywhere inside repo
# - .venv exists
# - .env exists
# - integration tests require DB + model artifacts + embedding artifacts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_ROOT"

MODE="${1:-all}"

die() {
  echo "ERROR: $1" >&2
  exit 1
}

log() {
  echo
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

[[ -d ".venv" ]] || die ".venv not found in project root."
[[ -f "pytest.ini" ]] || die "pytest.ini not found."

# shellcheck disable=SC1091
source .venv/bin/activate

export PYTHONPATH="$PROJECT_ROOT"
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

run_unit() {
  log "Running unit tests"
  pytest tests/unit -v
}

run_integration() {
  [[ -f ".env" ]] || die ".env not found. Integration tests need app config."
  [[ -f "model/artifacts/xgb_reranker.joblib" ]] || die "Missing model/artifacts/xgb_reranker.joblib"
  [[ -f "model/artifacts/xgb_feature_columns.json" ]] || die "Missing model/artifacts/xgb_feature_columns.json"
  [[ -f "model/artifacts/listing_embeddings.npy" ]] || die "Missing model/artifacts/listing_embeddings.npy"
  [[ -f "model/artifacts/listing_embedding_ids.json" ]] || die "Missing model/artifacts/listing_embedding_ids.json"

  log "Running integration tests"
  pytest tests/integration -v
}

case "$MODE" in
  unit)
    run_unit
    ;;
  integration)
    run_integration
    ;;
  all)
    run_unit
    run_integration
    ;;
  *)
    die "Unknown mode: $MODE. Use: all | unit | integration"
    ;;
esac

log "Tests completed successfully"
