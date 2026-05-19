from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
import numpy as np

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ML MODEL INITIALIZATION ---
# Using sublinear tf and n-grams (1,3) to capture contextual phrases, not just single words
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1, 3), sublinear_tf=True)
model = PassiveAggressiveClassifier(max_iter=50)

# Dummy baseline initialization data (Simulating initial training state)
init_texts = [
    "The government announced a new tax break for small businesses starting next month.",
    "Breaking news: Aliens have landed in Washington DC and taken over the capital!",
    "Scientists discover a new species of deep-sea jellyfish in the Pacific Ocean.",
    "Drinking 5 gallons of lemon juice overnight completely cures all forms of diseases."
]
init_labels = [1, 0, 1, 0] # 1 = Real, 0 = Fake

# Initial fit
X_init = vectorizer.fit_transform(init_texts)
model.partial_fit(X_init, init_labels, classes=[0, 1])

# This array acts as our temporary data buffer before automated retraining trigger
data_buffer = []

# --- SCHEMAS ---
class NewsInput(BaseModel):
    text: str

class FeedbackInput(BaseModel):
    text: str
    label: int # 1 for Real, 0 for Fake

# --- CORE FUNCTIONS ---
def trigger_incremental_retraining():
    """
    Siphons buffered real-life examples and updates the model 
    without rewriting or restarting the server.
    """
    global data_buffer, model
    if len(data_buffer) < 5: # Small threshold for demo; scale up to 500+ for your 10,000 goal
        return
    
    print(f"🔄 Retraining triggered! Processing {len(data_buffer)} new real-life examples...")
    
    texts = [item['text'] for item in data_buffer]
    labels = [item['label'] for item in data_buffer]
    
    # Transform new data using existing vocabulary definitions
    X_new = vectorizer.transform(texts)
    
    # Incrementally update model weights
    model.partial_fit(X_new, labels)
    
    # Clear buffer after successful training integration
    data_buffer.clear()
    print("✅ Model successfully updated itself!")

# --- ENDPOINTS ---
@app.post("/predict")
async def predict_news(data: NewsInput):
    # Convert text to structural/contextual matrix
    X = vectorizer.transform([data.text])
    prediction = model.predict(X)[0]
    
    verdict = "REAL" if prediction == 1 else "FAKE"
    return {"verdict": verdict}

@app.post("/feedback")
async def collect_feedback(data: FeedbackInput, background_tasks: BackgroundTasks):
    """
    Simulates real-world data gathering. When a trusted source/fact checker 
    confirms the true label, it logs it to the self-training buffer.
    """
    global data_buffer
    data_buffer.append({"text": data.text, "label": data.label})
    
    # Run the check/retrain logic as a background process so the user experiences zero lag
    background_tasks.add_task(trigger_incremental_retraining)
    
    return {"status": "Logged successfully", "buffer_count": len(data_buffer)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
