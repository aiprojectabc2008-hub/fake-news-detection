import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.pipeline import Pipeline

# 1. Page Layout Configuration
st.set_page_config(
    page_title="AI Fake News & Link Detector",
    page_icon="📰",
    layout="centered"
)

# Helper Function: Extract clean text from a news URL
def scrape_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None, f"Could not access website (Error Code: {response.status_code})"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
            
        paragraphs = soup.find_all('p')
        article_text = " ".join([p.get_text() for p in paragraphs])
        clean_text = " ".join(article_text.split())
        return clean_text, None
    except Exception as e:
        return None, str(e)

# 2. Secure Local Model Training (No URL dependency)
@st.cache_resource
def train_model():
    # Fetch real news text categories (politics, space, electronics, medicine)
    real_data = fetch_20newsgroups(subset='all', categories=[
        'talk.politics.misc', 'sci.space', 'sci.med', 'sci.electronics'
    ], remove=('headers', 'footers', 'quotes'))
    
    # Generate balanced fake samples using randomized/conspiracy keyword structures
    fake_texts = [
        "SECRET REVEALED: The government is using invisible frequencies to control your thoughts via cell towers!",
        "URGENT WARNING: Drinking toxic cleaner completely cures all viruses instantly! Hidden by pharmacies!",
        "BREAKING NEWS: Alien base discovered on the dark side of the moon by rogue independent astronomers.",
        "CONFIRMED: The earth is actually hollow and a secret race lives inside controlling global weather patterns."
    ] * 250  # Duplicate to balance training weights
    
    # Combine datasets
    texts = list(real_data.data) + fake_texts
    labels = ['REAL'] * len(real_data.data) + ['FAKE'] * len(fake_texts)
    
    # Build NLP Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.8, ngram_range=(1,2))),
        ('classifier', PassiveAggressiveClassifier(max_iter=50, random_state=42))
    ])
    pipeline.fit(texts, labels)
    return pipeline

# Train the AI
with st.spinner("🤖 Adjusting AI settings to read text and links... please wait..."):
    model = train_model()

# 3. Interactive User Interface
st.title("📰 Smart News Analyzer")
st.write("Our AI checks text patterns for integrity. Paste a news paragraph **OR** a link (URL) to a news article.")

user_input = st.text_area("Paste News Text or News Article Link here:", height=180, placeholder="https://example.com/news-story  OR  Paste paragraph...")

if st.button("Verify Content", type="primary"):
    text_to_analyze = user_input.strip()
    
    if not text_to_analyze:
        st.warning("⚠️ Please provide text or a link to analyze.")
    else:
        # Check if input is a link
        if text_to_analyze.startswith("http://") or text_to_analyze.startswith("https://"):
            with st.spinner("🌐 Accessing the website and scanning the article text..."):
                scraped_text, error = scrape_text_from_url(text_to_analyze)
                
            if error:
                st.error(f"❌ Failed to read the link. Reason: {error}")
                st.info("Tip: Some premium news websites block automated web scrapers. Copy and paste the text blocks manually instead!")
                text_to_analyze = None
            else:
                text_to_analyze = scraped_text
                st.info(f"✨ Retrieved {len(text_to_analyze.split())} words from the link context!")

        # Run prediction
        if text_to_analyze:
            if len(text_to_analyze.split()) < 5:
                st.warning("⚠️ Please provide a statement or paragraph containing at least 5 words.")
            else:
                prediction = model.predict([text_to_analyze])[0]
                
                st.markdown("---")
                if prediction == "REAL":
                    st.success("### ✅ Result: Likely REAL Content")
                    st.write("The language layout, neutral framing, and context structures match factual benchmarks.")
                else:
                    st.error("### 🚨 Result: Highly Suspicious (Likely FAKE)")
                    st.write("Warning: This content uses aggressive patterns found in disinformation or online hoaxes.")
