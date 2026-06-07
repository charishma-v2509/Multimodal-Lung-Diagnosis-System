import joblib
from sentence_transformers import SentenceTransformer

# Load SBERT encoder
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")


def load_text_model(path):
    return joblib.load(path)


def predict_text(model, impression):

    # Convert sentence to embedding
    embedding = sbert_model.encode([impression])

    prediction = model.predict(embedding)[0]

    if prediction == 0:
        label = "Normal"
        prob = 0.2
    else:
        label = "Abnormal"
        prob = 0.8

    return {
        "label": label,
        "probability": prob
    }