# TensorFlow on Mac – Why It’s Not Working & How to Fix

## Create a virtual environment (recommended first step)

Using a virtual environment keeps this project’s dependencies isolated and makes TensorFlow easier to get working.

1. **Create the environment** (from the project root):

   ```bash
   python3 -m venv .venv
   ```

2. **Activate it** (macOS/Linux):

   ```bash
   source .venv/bin/activate
   ```

   (On Windows: `.venv\Scripts\activate`)

3. **Upgrade pip** (optional but recommended):

   ```bash
   pip install --upgrade pip
   ```

4. **Install project dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **On Apple Silicon**, if TensorFlow fails or crashes at import, use the Mac builds instead:

   ```bash
   pip install tensorflow-macos tensorflow-metal
   ```

6. **Use this environment for Jupyter**: register it as a kernel so the notebook uses it:

   ```bash
   pip install ipykernel
   python -m ipykernel install --user --name=anomaly-detection --display-name="Python (Anomaly Detection)"
   ```

   Then in your notebook, choose the kernel **"Python (Anomaly Detection)"**, restart the kernel, and re-run. TensorFlow should be available and Autoencoder/LSTM will run.

---

## What we found on your Mac

- **Error:** `ModuleNotFoundError: No module named 'tensorflow'`
- **Cause:** TensorFlow is **not installed** in the Python environment you’re using (e.g. the one that runs the notebook or `python3` in the terminal).
- **Your setup:** macOS (darwin), **arm64** (Apple Silicon), **Python 3.13.7**.

So the issue is **missing installation**, not a code bug. Once TensorFlow is installed in the same environment where you run the notebook, the Autoencoder and LSTM steps can run.

---

## Fix 1: Install TensorFlow in the same environment (recommended first step)

Use the **same** Python/pip that you use to run the notebook or scripts.

From the project folder:

```bash
# If you use python3 / pip3 (e.g. from Homebrew or system)
pip3 install "tensorflow>=2.12.0"

# Or, if you use a venv
source .venv/bin/activate   # or whatever your venv is called
pip install "tensorflow>=2.12.0"
```

Then **restart the Jupyter kernel** (or restart the terminal) and re-run the notebook. The pipeline will set `TENSORFLOW_AVAILABLE = True` and run Autoencoder and LSTM.

---

## Fix 2: If you get “Illegal instruction” or a crash on Apple Silicon (M1/M2/M3)

On **arm64 Macs**, the default `tensorflow` wheel can sometimes crash at import (e.g. “Illegal instruction”). In that case use the **Apple Silicon–optimized** stack:

```bash
pip3 install tensorflow-macos
pip3 install tensorflow-metal   # optional: uses GPU (Metal)
```

- **tensorflow-macos**: TensorFlow built for Apple Silicon (avoids the usual crash).
- **tensorflow-metal**: Uses the Mac GPU; optional but can speed up training.

Then restart the kernel and try again.

---

## Fix 3: If you’re on Python 3.12 or 3.13 and TensorFlow won’t install

TensorFlow often lags support for the newest Python. If `pip install tensorflow` (or `tensorflow-macos`) fails or no wheel is found:

- Use a **Python 3.10 or 3.11** environment (e.g. `pyenv`, conda, or a venv with that version), then install TensorFlow there and run the notebook from that environment.

---

## Quick check after installing

In a terminal (using the same Python that runs your notebook):

```bash
python3 -c "import tensorflow as tf; print('TensorFlow', tf.__version__, 'OK')"
```

If that prints a version and “OK”, the notebook will see TensorFlow and run Autoencoder and LSTM (no code changes needed).

---

## Summary

| Issue | Cause | Fix |
|--------|--------|-----|
| `No module named 'tensorflow'` | TensorFlow not installed in current env | `pip3 install tensorflow` (or `tensorflow-macos` on M1/M2) in that env, then restart kernel |
| “Illegal instruction” / crash on M1/M2 | Default TensorFlow wheel on arm64 | Install `tensorflow-macos` (and optionally `tensorflow-metal`) |
| Install fails on Python 3.12/3.13 | TensorFlow may not support that version yet | Use Python 3.10 or 3.11 in a separate env and install TensorFlow there |

Your current failure is **Fix 1**: install TensorFlow in the environment you use to run the notebook.
