import streamlit as st
import pandas as pd
import joblib
import os
import re

# Load the trained model
model = joblib.load("log_classifier.pkl")

# Clean log lines (remove timestamps, IPs, etc.)
def clean_log_line(line):
    line = re.sub(r'\d{4}-\d{2}-\d{2}.*?Z', '', line)  # Remove timestamps
    line = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '', line)  # Remove IPs
    line = re.sub(r'\[.*?\]', '', line)  # Remove brackets like [123]
    return line.strip()

# UI Header
st.set_page_config(page_title="AI-Powered Kubernetes Log Analyzer", layout="wide")
st.title("🤖 AI-Powered Kubernetes Log Analyzer")

log_dir = "sample_logs"

# Check for logs
if not os.path.exists(log_dir) or len(os.listdir(log_dir)) == 0:
    st.warning("⚠️ No log files found in `sample_logs/`. Run `collect_logs.py` first.")
else:
    all_logs = []

    for file_name in os.listdir(log_dir):
        if file_name.endswith(".log") or file_name.endswith(".txt"):
            file_path = os.path.join(log_dir, file_name)
            with open(file_path, "r") as f:
                for line in f:
                    cleaned = clean_log_line(line)
                    if cleaned:
                        all_logs.append((file_name, cleaned))

    if all_logs:
        # Predict using the model
        file_names, lines = zip(*all_logs)
        preds = model.predict(lines)

        # Map icons
        icon_map = {
            "info": "✅ info",
            "warning": "⚠️ warning",
            "error": "❌ error"
        }
        severity_labels = [icon_map.get(p, p) for p in preds]

        # Build DataFrame
        df = pd.DataFrame({
            "file": file_names,
            "log": lines,
            "severity": preds,
            "severity (icon)": severity_labels
        })

        # Apply color styling
        def highlight_severity(severity):
            color_map = {
                'error': 'background-color: #ffcccc; color: red;',
                'warning': 'background-color: #fff3cd; color: orange;',
                'info': 'background-color: #d4edda; color: green;',
            }
            return [color_map.get(s, '') for s in severity]

        styled_df = df.style.apply(highlight_severity, subset=['severity'])

        st.subheader("📄 Log Classification Table")
        st.dataframe(styled_df, use_container_width=True)

        st.subheader("📊 Severity Distribution")
        st.bar_chart(df['severity'].value_counts())

    else:
        st.warning("No valid log lines found in files.")

