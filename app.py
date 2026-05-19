import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.pipeline import Pipeline

# 1. Page Layout Configuration
st.set_page_config(
    page_title="AI Fact Verifier",
    page_icon="🔍",
    layout="centered"
)

# Helper Function: Web scraper for news links
def scrape_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, f"Error Code: {response.status_code}"
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        paragraphs = soup.find_all('p')
        return " ".join([p.get_text() for p in paragraphs]).strip(), None
    except Exception as e:
        return None, str(e)

# Helper Function: Fact-Checking Knowledge Engine
def cross_reference_fact(claim):
    """
    Queries a free, open-source knowledge database (DuckDuckGo Instant Answer API)
    to check if the key terms in the statement match real-world facts.
    """
    try:
        # Clean the claim for a quick search query
        query = claim.lower().replace("?", "").replace("is the", "").strip()
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        response = requests.get(url, timeout=5).json()
        
        abstract = response.get("AbstractText", "")
        related_topics = response.get("RelatedTopics", [])
        
        # Fallback search if abstract is empty
        if not abstract and related_topics:
            abstract = related_topics[0].get("Text", "")
            
        return abstract if abstract else None
    except Exception:
        return None

# 3. Tone and Writing Style Predictor (Our original ML model)
@st.cache_resource
def train_tone_model():
    training_data = {
        'text': [
            "The Federal Reserve raised interest rates to combat inflation.",
            "The prime minister signed the historic climate bill into law today.",
            "Local community raises funds to save the downtown library.",
            "BREAKING: Secret underground networks operating under pizza shops!",
            "ALERT: Government releasing invisible tracking robots via regular tap water!",
            "SHOCKING SECRET: Drinking lemon juice completely cures all terminal diseases!"
        ],
        'label': ['REAL_TONE', 'REAL_TONE', 'REAL_TONE', 'FAKE_TONE', 'FAKE_TONE', 'FAKE_TONE']
    }
    df = pd.DataFrame(training_data)
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_df=1.0, ngram_range=(1,2))),
        ('classifier', PassiveAggressiveClassifier(max_iter=50, random_state=42))
    ])
    pipeline.fit(df['text'], df['label'])
    return pipeline

model = train_tone_model()

# 4. Interactive User Interface
st.title("🔍 Smart AI Fact-Checker")
st.write("This engine checks **BOTH** the writing style tone and cross-references the statement with a real-world database to find factual errors.")

user_input = st.text_area("Paste News Text, a Fact Claim, or an Article Link here:", height=150, placeholder="e.g., Rahul Gandhi is prime minister of india")

if st.button("Verify Statement & Facts", type="primary"):
    text_to_analyze = user_input.strip()
    
    if not text_to_analyze:
        st.warning("⚠️ Please enter a text statement or a web link.")
    else:
        # Link Handler
        if text_to_analyze.startswith("http://") or text_to_analyze.startswith("https://"):
            with st.spinner("🌐 Reading webpage text..."):
                scraped_text, error = scrape_text_from_url(text_to_analyze)
            if error:
                st.error(f"❌ Failed to scrape link: {error}")
                text_to_analyze = None
            else:
                text_to_analyze =
