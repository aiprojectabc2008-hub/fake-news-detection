import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.pipeline import Pipeline

# 1. Page Layout Configuration
st.set_page_config(
    page_title="AI Fake News Detector",
    page_icon="📰",
    layout="centered"
)

# 2. Pull a Guaranteed, Massive Dataset of True/False News Articles
@st.cache_data
def load_real_dataset():
    # This is a highly stable public dataset containing thousands of real and fake articles
    url = "https://raw.githubusercontent.com/jillanisofttech/fake-or-real-news/master/fake_or_real_news.csv"
    df = pd.read_csv(url)
    # Filter the dataset to just the text content and the FAKE/REAL label
    df = df[['text', 'label']]
    return df

# 3. Machine Learning Model Training Pipeline
@st.cache_resource
def train_model():
    df = load_real_dataset()
    # TfidfVectorizer analyzes the actual vocabulary and word combinations
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7, ngram_range=(1,2))),
        ('classifier', PassiveAggressiveClassifier(max_iter=50, random_state=42))
    ])
    pipeline.fit(df['text'], df['label'])
    return pipeline

# Train the model and show a nice loading spinner while it reads thousands of lines
with st.spinner("🤖 Training AI on thousands of real-world articles... please wait..."):
    model = train_model()

# 4. User Interface Layout
st.title("📰 AI News Statement Verifier")
st.write("Our AI reads the context, grammar, and patterns of text to see if it matches verified journalism standards.")

user_input = st.text_area("Paste the News Statement or Article Paragraph Here:", height=200, placeholder="Type or paste text...")

if st.button("Verify Statement", type="primary"):
    if not user_input.strip():
        st.warning("⚠️ Please provide some news text to analyze.")
    elif len(user_input.split()) < 5:
        st.warning("⚠️ Please paste a full sentence or paragraph (at least 5 words) so the AI has enough context to analyze.")
    else:
        # Run prediction on the actual text content
        prediction = model.predict([user_input])[0]
        
        st.markdown("---")
        if prediction == "REAL":
            st.success("### ✅ Result: Likely REAL Statement")
            st.write("The language structure, neutral tone, and phrasing pattern heavily align with verified, objective reporting.")
        else:
            st.error("### 🚨 Result: Highly Suspicious (Likely FAKE)")
            st.write("Warning: This statement displays heavy linguistic markers commonly associated with hoaxes, biased writing, or misinformation.")
       
    

            
