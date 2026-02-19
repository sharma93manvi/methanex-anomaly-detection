#!/bin/bash
# Run this script from your LOCAL machine (requires gcloud CLI and auth).
# Usage: ./deploy/deploy_to_gcp.sh
set -e
PROJECT="excursions-early-detection"
ZONE="us-west1-b"
INSTANCE="instance-20260218-062354"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== 1. Packing application ==="
./deploy/pack_for_deploy.sh

echo "=== 2. Copying to VM ==="
gcloud compute scp --project="$PROJECT" --zone="$ZONE" \
  deploy/app.tar.gz \
  "$INSTANCE:~/app.tar.gz"

echo "=== 3. Extracting and setting up on VM ==="
gcloud compute ssh --project="$PROJECT" --zone="$ZONE" "$INSTANCE" -- \
  "mkdir -p ~/app && cd ~/app && tar --warning=no-unknown-keyword -xzf ~/app.tar.gz && chmod +x deploy/setup_vm.sh && ./deploy/setup_vm.sh"

echo "=== 4. Opening firewall for port 8501 (if needed) ==="
gcloud compute firewall-rules create allow-streamlit8501 \
  --project="$PROJECT" \
  --allow=tcp:8501 \
  --source-ranges=0.0.0.0/0 \
  --description="Streamlit app" 2>/dev/null || echo "Firewall rule may already exist; continuing."

echo "=== 5. Getting VM external IP ==="
EXTERNAL_IP=$(gcloud compute instances describe "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --format='get(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null || true)
echo ""
echo "=== Deployment complete ==="
if [ -n "$EXTERNAL_IP" ]; then
  echo "Open in your browser:  http://$EXTERNAL_IP:8501"
else
  echo "Get your VM external IP with:"
  echo "  gcloud compute instances describe $INSTANCE --project=$PROJECT --zone=$ZONE --format=\"get(networkInterfaces[0].accessConfigs[0].natIP)\""
  echo "Then open: http://<EXTERNAL_IP>:8501"
fi
