"""
Agent Service - Gemini-powered chat for answering questions about model outputs.
Uses Google Gemini (gemini-2.0-flash) with streaming responses.
"""

import os
import json
import streamlit as st
from google import genai
from google.genai import types


GEMINI_MODEL = "gemini-2.0-flash"

SYSTEM_INSTRUCTION = """You are an expert assistant for the Methanex Anomaly Detection System. You help users understand:
- Anomaly timing predictions, lead time, severity, root cause analysis, and recommendations
- What the model outputs mean and how to act on them
- General questions about the pipeline (statistical + ML methods, sensors, early warning)

When the user provides "Current model outputs" context below, base your answers on that data. Be precise and cite specific values (e.g. confidence, predicted time, severity level). When no run-specific context is provided, answer from general knowledge about anomaly detection and this system.

Give clear, detailed responses. Use bullet points or short paragraphs when helpful. If the user asks about something not in the context, say so and explain what information would be needed."""


def get_api_key():
    """Get Gemini API key from Streamlit secrets or environment. Never hardcode."""
    try:
        key = st.secrets.get("gemini_api_key") or st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("gemini_api_key")


def build_context_from_outputs(processed_data, predictions):
    """
    Build a concise text summary of model outputs for the agent context.
    Returns a string suitable for inclusion in the prompt.
    """
    if predictions is None:
        return "No model outputs available yet. The user has not run analysis on this session."
    out = ["Current model outputs (use these to answer the user):", ""]
    # Data summary
    if processed_data is not None and hasattr(processed_data, "__len__"):
        n = len(processed_data)
        out.append(f"Processed data: {n} rows.")
        if hasattr(processed_data, "columns") and "Timestamp" in processed_data.columns:
            ts = processed_data["Timestamp"]
            if len(ts) > 0:
                out.append(f"Time range: {ts.min()} to {ts.max()}.")
        if "anomaly_combined" in getattr(processed_data, "columns", []):
            anomalies = processed_data["anomaly_combined"].sum()
            out.append(f"Anomalies detected in data: {int(anomalies)}.")
        out.append("")
    # Timing
    t = predictions.get("timing") or {}
    out.append("Anomaly timing:")
    out.append(f"  predicted_timestamp: {t.get('predicted_timestamp')}")
    out.append(f"  confidence: {t.get('confidence')}")
    out.append(f"  method: {t.get('method')}")
    out.append(f"  lead_time_hours: {t.get('lead_time_hours')}")
    if t.get("early_indicators"):
        out.append("  early_indicators: " + json.dumps(t.get("early_indicators", [])[:5]))
    out.append("")
    # Lead time
    lt = predictions.get("lead_time") or {}
    out.append("Lead time:")
    out.append(f"  predicted_lead_time_hours: {lt.get('predicted_lead_time_hours')}")
    out.append(f"  confidence: {lt.get('confidence')}")
    out.append(f"  confidence_range: {lt.get('confidence_range')}")
    if lt.get("contributing_sensors"):
        out.append("  contributing_sensors: " + json.dumps(lt.get("contributing_sensors", [])[:5]))
    out.append("")
    # Severity
    sev = predictions.get("severity") or {}
    out.append("Severity:")
    out.append(f"  severity_level: {sev.get('severity_level')}")
    out.append(f"  severity_score: {sev.get('severity_score')}")
    out.append(f"  factors: {sev.get('factors')}")
    out.append("")
    # Root cause
    rc = predictions.get("root_cause") or {}
    out.append("Root cause:")
    out.append(f"  primary_cause: {rc.get('primary_cause')}")
    out.append(f"  confidence: {rc.get('confidence')}")
    if rc.get("contributing_factors"):
        out.append("  contributing_factors: " + json.dumps(rc.get("contributing_factors", [])[:5]))
    out.append("")
    # Recommendations
    recs = predictions.get("recommendations") or []
    out.append("Recommendations:")
    for i, r in enumerate(recs[:10], 1):
        out.append(f"  {i}. [{r.get('priority')}] {r.get('title')}: {r.get('description')}; timeline: {r.get('timeline')}")
    return "\n".join(out)


def stream_gemini_response(user_message, chat_messages, processed_data, predictions, api_key):
    """
    Call Gemini with conversation history and current context; yield text chunks for streaming.
    chat_messages: list of {"role": "user" | "model", "content": str}
    Yields: str chunks (use with st.write_stream).
    """
    if not api_key:
        yield "Agent is not configured. Set GEMINI_API_KEY in the environment or add `gemini_api_key` to Streamlit secrets (e.g. `.streamlit/secrets.toml`)."
        return
    context = build_context_from_outputs(processed_data, predictions)
    system = SYSTEM_INSTRUCTION + "\n\n" + context
    # Build contents: history + new user message
    contents = []
    for msg in chat_messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
    try:
        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.4,
        )
        stream = client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=contents,
            config=config,
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"The agent encountered an error: {str(e)}. Please check your API key and try again."
