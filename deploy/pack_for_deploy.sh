#!/bin/bash
# Pack project for GCP deployment (exclude dev/cache files)
set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
DEPLOY_DIR="deploy"
OUTPUT_TAR="$DEPLOY_DIR/app.tar.gz"
mkdir -p "$DEPLOY_DIR"

# Build list of items to include (must exist)
INCLUDES=(app.py config.py train_models.py requirements.txt pages src services utils deploy/setup_vm.sh)
[ -f "Updated Challenge3 Data.csv" ] && INCLUDES+=("Updated Challenge3 Data.csv")
[ -d "test_data" ] && INCLUDES+=("test_data")
[ -d "models" ] && INCLUDES+=("models")

# Avoid macOS extended attributes so Linux tar on VM doesn't warn
export COPYFILE_DISABLE=1 2>/dev/null || true
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.ipynb_checkpoints' \
    --exclude='.venv' --exclude='venv' --exclude='env' \
    --exclude='*.egg-info' --exclude='.DS_Store' \
    -czvf "$OUTPUT_TAR" "${INCLUDES[@]}"
echo "Created $OUTPUT_TAR"
