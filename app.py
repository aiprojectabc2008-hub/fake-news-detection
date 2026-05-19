import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.pipeline import Pipeline

# 1. Page Configuration
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="centered"
)

# 2. Mock Dataset for Initial Demo
@st.cache_resource
def get_mock_data():
    return pd.DataFrame({
        'text': [
            "The president signed the historic climate bill into law today after months of debate.",
            "BREAKING: Scientists discover secret alien base hiding underneath the dark side of the moon!",
            "Local community raises over $50,000 to save the historic downtown library from closure.",
            "SHOCKING SECRET: Drinking 5 gallons of lemon juice daily completely cures all diseases instantly!!",
            "The central bank announced a 0.25% interest rate hike to combat rising core inflation.",
            "ALERT: Government releasing invisible tracking robots via regular tap water networks!"
        ],
        'label': ['REAL', 'FAKE', 'REAL', 'FAKE', 'REAL', 'FAKE']
    })

# 3. Model Training Pipeline
@st.cache_resource
def train_model():
    df = get_mock_data()
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7)),
        ('classifier', PassiveAggressiveClassifier(max_iter=50, random_state=42))
    ])
    pipeline.fit(df['text'], df['label'])
    return pipeline

model = train_model()

# 4. User Interface Layout
st.title("📰 Fake News Detection AI")
st.write("Paste a news article snippet below to check its validity using our NLP classification model.")

user_input = st.text_area("Enter News Content Here:", height=200, placeholder="Paste article paragraph...")

if st.button("Analyze News", type="primary"):
    if not user_input.strip():
        st.warning("⚠️ Please provide some news content to analyze.")
    else:
        prediction = model.predict([user_input])[0]
        
        st.markdown("---")
        if prediction == "REAL":
            st.success("### ✅ Result: Likely REAL News")
            st.write("The linguistic structure of this text heavily aligns with factual, verified news reporting.")
        else:
            st.error("### 🚨 Result: Highly Suspicious (Likely FAKE)")
            st.write("Warning: This text exhibits emotional vocabulary patterns or structures often found in misinformation.")
