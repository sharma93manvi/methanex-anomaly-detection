# Deploy Anomaly Detection App to GCP VM

## Prerequisites on your machine

- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) installed and initialized:
  ```bash
  gcloud auth login
  gcloud config set project excursions-early-detection
  ```

## One-command deploy (from project root)

From the project directory run:

```bash
chmod +x deploy/deploy_to_gcp.sh
./deploy/deploy_to_gcp.sh
```

This will: pack the app, copy it to the VM, extract and run setup (Python venv, install deps, train models if needed, start Streamlit).

## Manual steps (if you prefer)

### 1. Pack (on your machine)

```bash
cd "/Users/manvisharma/Documents/MBAN/Hackathon/Early Detection of Process Excursions from Sensor data"
./deploy/pack_for_deploy.sh
```

### 2. Copy tarball to VM

```bash
gcloud compute scp --project=excursions-early-detection --zone=us-west1-b \
  deploy/app.tar.gz \
  instance-20260218-062354:~/app.tar.gz
```

### 3. SSH into VM and setup

```bash
gcloud compute ssh --project=excursions-early-detection --zone=us-west1-b instance-20260218-062354
```

Then on the VM:

```bash
mkdir -p ~/app
cd ~/app
tar -xzf ~/app.tar.gz
chmod +x deploy/setup_vm.sh
./deploy/setup_vm.sh $HOME/app
```

### 4. Open firewall for port 8501 (on your machine)

```bash
gcloud compute firewall-rules create allow-streamlit8501 \
  --project=excursions-early-detection \
  --allow=tcp:8501 \
  --source-ranges=0.0.0.0/0 \
  --description="Streamlit app"
```

(If the rule already exists, the command will fail; that’s fine.)

### 5. Get VM external IP (on your machine)

```bash
gcloud compute instances describe instance-20260218-062354 \
  --project=excursions-early-detection \
  --zone=us-west1-b \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

## How to test the app online

1. After deploy, get the external IP (step 5 above).
2. In your browser open: **http://<EXTERNAL_IP>:8501**
3. You should see the Methanex Anomaly Detection System home page. Use “Upload & Analyze” and “Mock Stream” to test.

## Subdomain shows IP in the browser URL

If you use a subdomain (e.g. **http://gc-team4.themanvisharma.com/**) but the browser address bar shows **http://35.233.130.33/** instead, the cause is almost always **DNS/hosting configuration**, not the server.

- **Wrong:** A **URL redirect** (forwarding) from the subdomain to the IP. The provider returns `301/302 Location: http://35.233.130.33/`, so the browser follows it and shows the IP.
- **Correct:** An **A record** so the subdomain resolves to the same IP but no redirect is sent. The browser then connects with `Host: gc-team4.themanvisharma.com`, and the URL stays as the subdomain.

**Fix:** In your DNS provider for **themanvisharma.com**, remove any "URL redirect" or "forwarding" for **gc-team4** and add an **A record**: host `gc-team4`, value `35.233.130.33`. After DNS propagates, **http://gc-team4.themanvisharma.com/** should keep the subdomain in the URL. Nginx on the server is already configured to serve the app for that host and redirect direct IP access to the subdomain.

## Restarting Streamlit on the VM

SSH into the VM, then:

```bash
cd ~/app
source venv/bin/activate
# Optional: kill existing
kill $(cat streamlit.pid 2>/dev/null) 2>/dev/null || true
# Start again
nohup streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true > streamlit.log 2>&1 &
echo $! > streamlit.pid
```

## Stopping the app

On the VM:

```bash
kill $(cat ~/app/streamlit.pid)
```
