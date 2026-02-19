#!/bin/bash
# Run this script ON the GCP VM (e.g. after extracting app.tar.gz in ~/app).
# Use current directory so path is correct on the VM (avoid $HOME expanding on your local machine).
set -e
APP_DIR="${1:-.}"
cd "$APP_DIR"
echo "=== Setting up app in $APP_DIR ==="

# Ensure Python3 and venv support (Debian/Ubuntu need python3-venv for "python3 -m venv")
if ! command -v python3 &>/dev/null; then
  echo "Installing python3..."
  sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip python3-venv
fi
echo "Installing python3-venv if needed..."
sudo apt-get update -qq
sudo apt-get install -y python3-venv 2>/dev/null || true
# Some systems use versioned package (e.g. python3.11-venv)
PYVER=$(python3 -c 'import sys; print(f"python3.{sys.version_info.minor}-venv")' 2>/dev/null)
sudo apt-get install -y "$PYVER" 2>/dev/null || true
python3 --version

# Create venv (recreate if broken or incomplete from a previous run)
if [ ! -f "venv/bin/activate" ]; then
  rm -rf venv
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
# Core deps required for the app (TensorFlow is optional and heavy)
pip install pandas numpy scikit-learn matplotlib seaborn streamlit plotly -q
pip install -r requirements.txt -q 2>/dev/null || true
which streamlit

# Train models if not present
if [ ! -f "models/metadata.pkl" ]; then
  echo "Training models (this may take a few minutes)..."
  [ -f "Updated Challenge3 Data.csv" ] && python train_models.py || echo "No training CSV; skipping. Upload/Stream may need models."
else
  echo "Models directory already present."
fi

# Run Streamlit on 0.0.0.0 so it's reachable from outside
echo "Starting Streamlit on 0.0.0.0:8501 ..."
nohup streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true > streamlit.log 2>&1 &
echo $! > streamlit.pid
sleep 3
echo "Streamlit started. PID=$(cat streamlit.pid). Log: $APP_DIR/streamlit.log"
