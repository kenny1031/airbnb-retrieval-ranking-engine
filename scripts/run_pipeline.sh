#!/usr/bin/env bash
set -Eeuo pipefail

# Usage:
#   bash scripts/run_pipeline.sh
#   bash scripts/run_pipeline.sh --csv data/raw/listings.csv
#   bash scripts/run_pipeline.sh --skip-load
#   bash scripts/run_pipeline.sh --skip-embeddings
#
# Assumptions:
# - Run from project root, or anywhere inside the repo
# - .venv exists
# - PostgreSQL is already up
# - tables already created
#
# Pipeline:
# 1) load listings CSV into Postgres
# 2) build listing_text field
# 3) build training data
# 4) train XGBoost reranker
# 5) build dense listing embeddings

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_ROOT"

CSV_PATH="data/raw/listings.csv"
SKIP_LOAD=0
SKIP_TEXT=0
SKIP_TRAINING_DATA=0
SKIP_TRAIN=0
SKIP_EMBEDDINGS=0

log() {
  echo
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

die() {
  echo "ERROR: $1" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --csv)
      CSV_PATH="$2"
      shift 2
      ;;
    --skip-load)
      SKIP_LOAD=1
      shift
      ;;
    --skip-text)
      SKIP_TEXT=1
      shift
      ;;
    --skip-training-data)
      SKIP_TRAINING_DATA=1
      shift
      ;;
    --skip-train)
      SKIP_TRAIN=1
      shift
      ;;
    --skip-embeddings)
      SKIP_EMBEDDINGS=1
      shift
      ;;
    -h|--help)
      sed -n '2,25p' "$0"
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
done

[[ -d ".venv" ]] || die ".venv not found in project root."
[[ -f ".env" ]] || die ".env not found. Create it from .env.example first."

# shellcheck disable=SC1091
source .venv/bin/activate

export PYTHONPATH="$PROJECT_ROOT"
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

mkdir -p model/artifacts

log "Python environment"
python --version
which python

if [[ "$SKIP_LOAD" -eq 0 ]]; then
  [[ -f "$CSV_PATH" ]] || die "CSV not found: $CSV_PATH"
  log "Loading listings from CSV into PostgreSQL"
  python scripts/load_listings.py --csv "$CSV_PATH"
else
  log "Skipping CSV load"
fi

if [[ "$SKIP_TEXT" -eq 0 ]]; then
  log "Building listing_text"
  python scripts/build_listing_text.py
else
  log "Skipping listing_text build"
fi

if [[ "$SKIP_TRAINING_DATA" -eq 0 ]]; then
  [[ -f "model/queries.txt" ]] || die "model/queries.txt not found."
  log "Building training data"
  python model/build_training_data.py
else
  log "Skipping training data build"
fi

if [[ "$SKIP_TRAIN" -eq 0 ]]; then
  log "Training XGBoost reranker"
  python model/train_reranker.py
else
  log "Skipping reranker training"
fi

if [[ "$SKIP_EMBEDDINGS" -eq 0 ]]; then
  log "Building listing embeddings"
  python model/build_listing_embeddings.py
else
  log "Skipping embedding build"
fi

log "Pipeline completed successfully"
echo "Artifacts directory: $PROJECT_ROOT/model/artifacts"