# Model Selection Rationale

## Overview

This document explains the machine learning models we explored for anomaly detection and why we selected **Isolation Forest** as the primary method, combined with statistical methods.

## Models Explored

### 1. Isolation Forest ✅ **SELECTED (Primary Method)**

**What it is:**
- Unsupervised learning algorithm that identifies anomalies by isolating them in feature space
- Part of scikit-learn library (no heavy dependencies)

**Why we selected it:**
- ✅ **Fast**: Trains in seconds, not minutes
- ✅ **Effective**: Works well with high-dimensional sensor data (169 engineered features)
- ✅ **No heavy dependencies**: Only requires scikit-learn (already in use)
- ✅ **Interpretable**: Results are easier to understand for operations teams
- ✅ **Proven**: Widely used in industrial anomaly detection applications
- ✅ **Works with our features**: Effective with engineered features (rolling stats, residuals, rate of change)

**How it works:**
- Trained on first 70% of data (includes both operating periods and unplanned outages)
- Learns what "normal" patterns look like
- Flags data points that are isolated/different from normal patterns
- Contamination rate: 5% (expects ~5% anomalies)

**Status**: Always runs, core ML detection method

---

### 2. Autoencoder (Optional/Experimental)

**What it is:**
- Neural network that learns to compress and reconstruct data
- High reconstruction error indicates anomalies

**Why we considered it:**
- Can capture complex non-linear relationships between sensors
- Learns compressed representations of normal patterns

**Why we made it optional:**
- ❌ **Heavy dependency**: Requires TensorFlow (~2GB installation)
- ❌ **Slow training**: 50 epochs takes several minutes
- ❌ **Marginal improvement**: May not significantly outperform Isolation Forest for this use case
- ❌ **Complexity**: More difficult to debug and tune
- ❌ **Redundancy**: Isolation Forest already handles complex feature relationships well

**Status**: Optional, only runs if TensorFlow is installed
**Weight in ensemble**: 15% (if available)

---

### 3. LSTM (Long Short-Term Memory) (Optional/Experimental)

**What it is:**
- Recurrent neural network designed for time series data
- Predicts next hour's values based on historical patterns
- High prediction error indicates anomalies

**Why we considered it:**
- Designed specifically for temporal sequences
- Could potentially predict future anomalies

**Why we made it optional:**
- ❌ **Heavy dependency**: Requires TensorFlow (~2GB installation)
- ❌ **Slow training**: 30 epochs takes several minutes
- ❌ **Redundant**: Our statistical methods already capture temporal patterns effectively:
  - Rolling windows (6h and 24h) capture recent and daily patterns
  - Rate of change features capture trends and sudden changes
  - Moving averages capture sustained deviations
- ❌ **Complexity**: More difficult to debug and tune

**Status**: Optional, only runs if TensorFlow is installed
**Weight in ensemble**: 15% (if available)

---

## Final Architecture

### Primary Approach: Isolation Forest + Statistical Methods

**Why this combination works well:**

1. **Statistical Methods** handle temporal patterns:
   - Rolling z-scores (24h windows)
   - Moving average envelopes
   - Rate of change features
   - Percentile-based detection

2. **Isolation Forest** handles complex feature relationships:
   - Learns interactions between 169 engineered features
   - Identifies anomalies that don't violate simple thresholds
   - Captures non-linear patterns

3. **Together** they provide:
   - Comprehensive detection (temporal + feature relationships)
   - Fast execution (no deep learning training)
   - Easy maintenance (no TensorFlow dependency)
   - Interpretable results (important for operations)

### Ensemble Scoring

- **If only Isolation Forest available**: Uses Isolation Forest score directly (weight: 1.0)
- **If ensemble available**: 
  - Isolation Forest: 70% (primary)
  - Autoencoder: 15% (optional)
  - LSTM: 15% (optional)

**Note**: The system works effectively with just Isolation Forest. Autoencoder and LSTM are optional enhancements that may provide marginal improvements but are not required.

---

## Performance Comparison

| Method | Training Time | Inference Speed | Dependencies | Interpretability | Temporal Patterns |
|--------|--------------|-----------------|--------------|-----------------|-------------------|
| **Isolation Forest** | ~5-10 seconds | Very fast | scikit-learn | High | Via statistical methods |
| Autoencoder | ~5-10 minutes | Fast | TensorFlow (~2GB) | Medium | Via statistical methods |
| LSTM | ~3-5 minutes | Fast | TensorFlow (~2GB) | Low | Built-in (redundant) |

---

## Recommendation for Methanox

**Use Isolation Forest + Statistical Methods** because:

1. ✅ **Fast**: Complete pipeline runs in minutes, not hours
2. ✅ **Reliable**: No heavy dependencies to manage
3. ✅ **Comprehensive**: Statistical methods + Isolation Forest cover all anomaly types
4. ✅ **Maintainable**: Easier to debug and tune
5. ✅ **Production-ready**: Can deploy without TensorFlow installation

**Optional**: If Methanox wants to experiment with deep learning methods later, the code already supports Autoencoder and LSTM - just install TensorFlow and they'll run automatically.

---

## Code Implementation

The implementation in `ml_detection.py`:
- Always runs Isolation Forest (primary method)
- Optionally runs Autoencoder and LSTM if TensorFlow is available
- Automatically adjusts ensemble weights based on available methods
- Works effectively with just Isolation Forest

This design provides:
- **Flexibility**: Can add deep learning later if needed
- **Simplicity**: Works out-of-the-box without TensorFlow
- **Performance**: Fast execution for production use

