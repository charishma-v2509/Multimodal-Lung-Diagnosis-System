"""
================================================================================
  evaluate_fusion.py
  Automated Multimodal Evaluation Pipeline — Lung Diagnosis System
================================================================================

DESCRIPTION:
    Authenticates against a FastAPI/JWT backend, sends all 30 multimodal test
    cases (image + clinical text + vitals) to the /patient/complete-diagnosis
    endpoint, collects predictions, and produces a full evaluation report
    including accuracy, precision, recall, F1, confusion matrix, and CSV output.

USAGE:
    python evaluate_fusion.py

REQUIRED PACKAGES:
    pip install pandas requests scikit-learn matplotlib seaborn

EXPECTED FOLDER STRUCTURE:
    project/
    ├── evaluate_fusion.py              ← this script
    ├── fusion_evaluation_dataset.csv   ← evaluation dataset
    └── evaluationImages/               ← folder extracted from evaluationImages.zip
        ├── img1.jpg
        ├── img2.jpg
        └── ... img30.jpg

    Extract the zip before running:
        unzip evaluationImages.zip

OUTPUTS (created in the same folder):
    ├── fusion_results.csv              ← per-sample predictions + ground truth
    └── fusion_confusion_matrix.png     ← confusion matrix heatmap

CONFIGURATION (edit the block below before running):
    BASE_URL    — your backend URL
    LOGIN_EMAIL — doctor login email
    LOGIN_PASS  — doctor login password
    CSV_PATH    — path to the evaluation CSV
    IMG_DIR     — folder containing the 30 test images
================================================================================
"""

# ── Standard library ──────────────────────────────────────────────────────────
import os
import sys
import json
import time

# ── Third-party ───────────────────────────────────────────────────────────────
import pandas as pd
import requests
import matplotlib
matplotlib.use("Agg")           # headless — no display needed
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# ══════════════════════════════════════════════════════════════════════════════
#  ① CONFIGURATION  — edit this block before running
# ══════════════════════════════════════════════════════════════════════════════
BASE_URL   = "http://localhost:8000"
LOGIN_EMAIL = "marshmello@gmail.com"   # ← your doctor login email  (sent as "email" in JSON)
LOGIN_PASS  = "123456789"             # ← your doctor password    (sent as "password" in JSON)

CSV_PATH   = "fusion_evaluation_dataset.csv"
IMG_DIR    = "evaluationImages"        # folder extracted from the zip

OUTPUT_CSV = "fusion_results.csv"
OUTPUT_IMG = "fusion_confusion_matrix.png"

# Label mapping — DO NOT change unless your backend uses different strings
LABEL_MAP = {"Normal": 0, "Disease": 1}

# ══════════════════════════════════════════════════════════════════════════════
#  ② HELPER — response parser tuned to your backend's actual schema
# ══════════════════════════════════════════════════════════════════════════════
#
# Your API response structure:
#   urgency_indicator     : "Normal" | "High Risk" | "Moderate Risk" ...
#   health_risk_summary   : "Low Risk" | "Moderate Risk" | "High Risk" ...
#   modality_contribution : { image_model, text_model, vitals_model, symptom_model }
#
# Fusion logic:
#   Primary  → urgency_indicator
#   Fallback → health_risk_summary
#   Tiebreak → majority vote across modality_contribution values
#   Confidence = fraction of modality votes that agree with final label

NORMAL_STRINGS  = {"normal", "low risk", "no risk", "negative",
                   "no finding", "healthy", "0"}
DISEASE_STRINGS = {"high risk", "moderate risk", "disease", "abnormal",
                   "positive", "1", "pneumonia", "effusion", "fibrosis",
                   "infiltration", "consolidation", "pleural effusion"}


def _to_binary(raw: str) -> str | None:
    """Map a single string value to 'Normal' or 'Disease'. None if unknown."""
    r = raw.strip().lower()
    if r in NORMAL_STRINGS:
        return "Normal"
    if r in DISEASE_STRINGS:
        return "Disease"
    return None


def normalise_label(raw: str | None) -> str | None:
    """Thin wrapper kept for call-site compatibility."""
    if raw is None:
        return None
    return _to_binary(raw)


def extract_prediction(resp_json: dict) -> tuple[str | None, float | None]:
    """
    Derive final binary prediction and confidence from your backend response.

    1. urgency_indicator  → primary label
    2. health_risk_summary → secondary label
    3. modality_contribution majority vote → tiebreaker
    4. confidence = fraction of modality votes matching final label
    """
    # ── Primary signal ────────────────────────────────────────────────────────
    urgency_raw = resp_json.get("urgency_indicator", "")
    primary     = _to_binary(urgency_raw) if urgency_raw else None

    risk_raw  = resp_json.get("health_risk_summary", "")
    secondary = _to_binary(risk_raw) if risk_raw else None

    # ── Modality votes ────────────────────────────────────────────────────────
    contrib      = resp_json.get("modality_contribution", {})
    vote_labels  = [_to_binary(str(v)) for v in contrib.values()]
    vote_labels  = [v for v in vote_labels if v is not None]

    disease_votes = vote_labels.count("Disease")
    normal_votes  = vote_labels.count("Normal")
    total_votes   = len(vote_labels)
    majority      = ("Disease" if disease_votes > normal_votes else "Normal") if total_votes else None

    # ── Final label: primary → secondary → majority ───────────────────────────
    final = primary or secondary or majority

    # ── Confidence from modality agreement ───────────────────────────────────
    if final and total_votes > 0:
        confidence = round(vote_labels.count(final) / total_votes, 3)
    else:
        confidence = None

    return final, confidence


# ══════════════════════════════════════════════════════════════════════════════
#  ③ AUTHENTICATION
# ══════════════════════════════════════════════════════════════════════════════

def authenticate() -> str:
    """
    POST /login, extract JWT token.
    Exits with error message if authentication fails.
    """
    print("\n" + "="*60)
    print("  STEP 1 — Authenticating with backend")
    print("="*60)

    url = f"{BASE_URL}/login"

    # Your backend expects a JSON body (Pydantic model), not OAuth2 form-data.
    # The 422 "Input should be a valid dictionary" error confirms this.
    try:
        resp = requests.post(
            url,
            json={"email": LOGIN_EMAIL, "password": LOGIN_PASS},
            timeout=15
        )
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to backend at {BASE_URL}.")
        print("        Make sure your FastAPI server is running.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("[ERROR] Login request timed out.")
        sys.exit(1)

    if resp.status_code != 200:
        print(f"[ERROR] Login failed — HTTP {resp.status_code}")
        print(f"        Response: {resp.text[:300]}")
        sys.exit(1)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("[ERROR] Login response is not valid JSON.")
        print(f"        Raw response: {resp.text[:300]}")
        sys.exit(1)

    token = data.get("access_token")
    if not token:
        print("[ERROR] 'access_token' not found in login response.")
        print(f"        Response keys: {list(data.keys())}")
        sys.exit(1)

    role = data.get("role", "unknown")
    print(f"  ✓  Authenticated successfully  |  role = {role}")
    print(f"  ✓  Token received (first 20 chars): {token[:20]}...")
    return token


# ══════════════════════════════════════════════════════════════════════════════
#  ④ LOAD DATASET
# ══════════════════════════════════════════════════════════════════════════════

def load_dataset() -> pd.DataFrame:
    """Load and validate the evaluation CSV."""
    print("\n" + "="*60)
    print("  STEP 2 — Loading evaluation dataset")
    print("="*60)

    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] CSV not found: {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)

    required_cols = [
        "image_path", "report_text", "symptoms",
        "oxygen", "heart_rate", "temperature", "respiratory_rate", "label"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"[ERROR] Missing columns in CSV: {missing}")
        sys.exit(1)

    print(f"  ✓  Loaded {len(df)} rows")
    print(f"  ✓  Label distribution: {df['label'].value_counts().to_dict()}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  ⑤ SEND ONE REQUEST
# ══════════════════════════════════════════════════════════════════════════════

def send_request(row: pd.Series, token: str, idx: int, total: int) -> dict:
    """
    Build multipart/form-data request for one test case and POST it.
    Returns a result dict with prediction, confidence, and status.
    """
    # ── Resolve image path ────────────────────────────────────────────────────
    img_filename = os.path.basename(row["image_path"])   # e.g. img1.jpg
    img_full     = os.path.join(IMG_DIR, img_filename)

    print(f"\n[{idx}/{total}] Processing {img_filename} ...", end=" ", flush=True)

    result = {
        "image_path"    : row["image_path"],
        "ground_truth"  : row["label"],
        "predicted_label": None,
        "confidence"    : None,
        "status"        : "failed",
        "error"         : None,
    }

    # ── Check image exists ────────────────────────────────────────────────────
    if not os.path.exists(img_full):
        msg = f"Image not found: {img_full}"
        print(f"✗  SKIPPED — {msg}")
        result["error"] = msg
        return result

    # ── Build form fields (EXACT backend names) ───────────────────────────────
    form_data = {
        "symptoms"          : str(row["symptoms"]),
        "impression"        : str(row["report_text"]),   # CSV col = report_text → backend = impression
        "oxygen"            : str(row["oxygen"]),
        "heart_rate"        : str(row["heart_rate"]),
        "temperature"       : str(row["temperature"]),
        "respiratory_rate"  : str(row["respiratory_rate"]),
    }

    # ── Send request ──────────────────────────────────────────────────────────
    try:
        with open(img_full, "rb") as img_file:
            files = {"image": (img_filename, img_file, "image/jpeg")}
            resp = requests.post(
                f"{BASE_URL}/patient/complete-diagnosis",
                data    = form_data,
                files   = files,
                headers = {"Authorization": f"Bearer {token}"},
                timeout = 30
            )
    except requests.exceptions.Timeout:
        print("✗  TIMEOUT")
        result["error"] = "Request timed out"
        return result
    except requests.exceptions.ConnectionError as e:
        print(f"✗  CONNECTION ERROR — {e}")
        result["error"] = str(e)
        return result

    # ── Parse response ────────────────────────────────────────────────────────
    if resp.status_code == 401:
        print("✗  UNAUTHORIZED — token may have expired")
        result["error"] = "HTTP 401 Unauthorized"
        return result

    if resp.status_code not in (200, 201):
        print(f"✗  HTTP {resp.status_code}")
        result["error"] = f"HTTP {resp.status_code}: {resp.text[:200]}"
        return result

    try:
        resp_json = resp.json()
    except json.JSONDecodeError:
        print("✗  Invalid JSON response")
        result["error"] = f"Non-JSON response: {resp.text[:200]}"
        return result

    # ── Extract prediction ────────────────────────────────────────────────────
    raw_pred, confidence = extract_prediction(resp_json)
    normalised           = normalise_label(raw_pred)

    if normalised is None:
        print(f"✗  Unrecognised prediction: '{raw_pred}'")
        result["error"]  = f"Unrecognised label from API: {raw_pred}"
        result["status"] = "unexpected_label"
        return result

    result["predicted_label"] = normalised
    result["confidence"]      = confidence
    result["status"]          = "success"

    match = "✓" if normalised == row["label"] else "✗"
    conf_str = f"{confidence:.3f}" if confidence is not None else "N/A"
    print(f"{match}  Predicted={normalised:<8}  GT={row['label']:<8}  Conf={conf_str}")

    return result


# ══════════════════════════════════════════════════════════════════════════════
#  ⑥ EVALUATION LOOP
# ══════════════════════════════════════════════════════════════════════════════

def run_evaluation(df: pd.DataFrame, token: str) -> list[dict]:
    """Iterate over all rows and collect results."""
    print("\n" + "="*60)
    print("  STEP 3 — Running evaluation (30 test cases)")
    print("="*60)

    results = []
    total   = len(df)

    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        res = send_request(row, token, idx, total)
        results.append(res)
        time.sleep(0.3)   # gentle throttle — remove if your backend is fast

    return results


# ══════════════════════════════════════════════════════════════════════════════
#  ⑦ COMPUTE METRICS
# ══════════════════════════════════════════════════════════════════════════════

def compute_metrics(results: list[dict]) -> pd.DataFrame:
    """
    Filter to successful predictions, compute sklearn metrics,
    print classification report, save confusion matrix PNG.
    """
    print("\n" + "="*60)
    print("  STEP 4 — Computing evaluation metrics")
    print("="*60)

    results_df = pd.DataFrame(results)

    # ── Summary counts ────────────────────────────────────────────────────────
    total      = len(results_df)
    success    = (results_df["status"] == "success").sum()
    failed     = total - success

    print(f"\n  Total samples    : {total}")
    print(f"  Successful       : {success}")
    print(f"  Failed / Skipped : {failed}")

    if success == 0:
        print("\n[ERROR] No successful predictions. Cannot compute metrics.")
        print("        Check your backend, credentials, and image paths.")
        return results_df

    # ── Use only successful rows ──────────────────────────────────────────────
    valid = results_df[results_df["status"] == "success"].copy()
    y_true = valid["ground_truth"].map(LABEL_MAP).tolist()
    y_pred = valid["predicted_label"].map(LABEL_MAP).tolist()

    # ── Core metrics ──────────────────────────────────────────────────────────
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, pos_label=1, zero_division=0)
    rec  = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
    f1   = f1_score(y_true, y_pred, pos_label=1, zero_division=0)

    print("\n  ┌─────────────────────────────────────┐")
    print(f"  │  Accuracy          :  {acc:.4f}        │")
    print(f"  │  Precision         :  {prec:.4f}        │")
    print(f"  │  Recall            :  {rec:.4f}        │")
    print(f"  │  F1 Score          :  {f1:.4f}        │")
    print("  └─────────────────────────────────────┘")

    # ── Full classification report ────────────────────────────────────────────
    print("\n  Classification Report:")
    print(
        classification_report(
            y_true, y_pred,
            target_names=["Normal", "Disease"],
            zero_division=0
        )
    )

    # ── Confusion matrix ──────────────────────────────────────────────────────
    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Normal", "Disease"],
        yticklabels=["Normal", "Disease"],
        linewidths=0.5,
        ax=ax
    )
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)
    ax.set_title(
        f"Fusion Model — Confusion Matrix\n"
        f"Acc={acc:.3f}  F1={f1:.3f}  (n={success})",
        fontsize=13, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG, dpi=150)
    plt.close()
    print(f"\n  ✓  Confusion matrix saved → {OUTPUT_IMG}")

    return results_df


# ══════════════════════════════════════════════════════════════════════════════
#  ⑧ SAVE RESULTS CSV
# ══════════════════════════════════════════════════════════════════════════════

def save_results(results_df: pd.DataFrame) -> None:
    """Save per-sample prediction results to CSV."""
    # Re-order columns for readability
    cols = [
        "image_path", "ground_truth", "predicted_label",
        "confidence", "status", "error"
    ]
    cols = [c for c in cols if c in results_df.columns]
    results_df[cols].to_csv(OUTPUT_CSV, index=False)
    print(f"  ✓  Detailed results saved → {OUTPUT_CSV}")


# ══════════════════════════════════════════════════════════════════════════════
#  ⑨ FINAL SUMMARY PRINT
# ══════════════════════════════════════════════════════════════════════════════

def print_final_summary(results_df: pd.DataFrame) -> None:
    print("\n" + "="*60)
    print("  EVALUATION COMPLETE — FINAL SUMMARY")
    print("="*60)

    total   = len(results_df)
    success = (results_df["status"] == "success").sum()
    failed  = total - success

    print(f"\n  Total samples         : {total}")
    print(f"  Successful requests   : {success}")
    print(f"  Failed requests       : {failed}")

    valid = results_df[results_df["status"] == "success"]
    if len(valid) > 0:
        y_true = valid["ground_truth"].map(LABEL_MAP)
        y_pred = valid["predicted_label"].map(LABEL_MAP)

        print(f"\n  Accuracy              : {accuracy_score(y_true, y_pred):.4f}")
        print(f"  Precision (Disease)   : {precision_score(y_true, y_pred, pos_label=1, zero_division=0):.4f}")
        print(f"  Recall    (Disease)   : {recall_score(y_true, y_pred, pos_label=1, zero_division=0):.4f}")
        print(f"  F1 Score  (Disease)   : {f1_score(y_true, y_pred, pos_label=1, zero_division=0):.4f}")

    print(f"\n  Output files:")
    print(f"    → {OUTPUT_CSV}")
    print(f"    → {OUTPUT_IMG}")
    print("\n" + "="*60 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
#  ⑩ MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("  Multimodal Lung Diagnosis — Automated Evaluation")
    print("  Backend :", BASE_URL)
    print("  Dataset :", CSV_PATH)
    print("  Images  :", IMG_DIR)
    print("="*60)

    token      = authenticate()
    df         = load_dataset()
    results    = run_evaluation(df, token)
    results_df = compute_metrics(results)
    save_results(results_df)
    print_final_summary(results_df)


if __name__ == "__main__":
    main()
