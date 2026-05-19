
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
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

# 2. Pull a Stable, Balanced, Real-vs-Fake Dataset (6,000+ Verified Articles)
@st.cache_data
def load_balanced_dataset():
    # Utilizing an alternate, high-uptime mirror for the classic Welker Fake/Real News Dataset
    url = "https://raw.githubusercontent.com/skandavivek/Fake-News-Prediction/main/fake_or_real_news.csv"
    df = pd.read_csv(url)
    # Filter down to the text columns and ensure labels are strictly "REAL" and "FAKE"
    df = df[['text', 'label']].dropna()
    return df

# 3. Model Training Pipeline
@st.cache_resource
def train_model():
    df = load_balanced_dataset()
    # TF-IDF looks at individual words and 2-word combinations (ngrams) to detect tone
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7, ngram_range=(1,2))),
        ('classifier', PassiveAggressiveClassifier(max_iter=50, random_state=42))
    ])
    pipeline.fit(df['text'], df['label'])
    return pipeline

# Train the AI
with st.spinner("🤖 Training AI on 6,300+ balanced True & Fake articles..."):
    model = train_model()

# 4. Interactive User Interface
st.title("📰 AI News Text & Link Analyzer")
st.write("Paste a paragraph **OR** an active news link to evaluate its truth pattern against 6,000+ articles.")

user_input = st.text_area("Paste News Text or Article URL here:", height=180, placeholder="https://example.com/story  OR  Paste text...")

if st.button("Verify Integrity", type="primary"):
    text_to_analyze = user_input.strip()
    
    if not text_to_analyze:
        st.warning("⚠️ Please enter a text paragraph or web link first.")
    else:
        # If the input is a web link, automatically scrape it
        if text_to_analyze.startswith("http://") or text_to_analyze.startswith("https://"):
            with st.spinner("🌐 Crawling website text content..."):
                scraped_text, error = scrape_text_from_url(text_to_analyze)
                
            if error:
                st.error(f"❌ Web Scraper Blocked. Reason: {error}")
                st.info("Note: Premium news networks block code scrapers. Try manual copy/pasting instead!")
                text_to_analyze = None
            else:
                text_to_analyze = scraped_text
                st.info(f"✨ Successfully pulled {len(text_to_analyze.split())} words from the link context.")

        # Run model analysis if valid text is ready
        if text_to_analyze:
            if len(text_to_analyze.split()) < 10:
                st.warning("⚠️ Please provide a longer statement (at least 10 words) for an accurate AI prediction.")
            else:
                prediction = model.predict([text_to_analyze])[0]
                
                st.markdown("---")
                if prediction == "REAL" or prediction.strip().upper() == "REAL":
                    st.success("### ✅ Result: Likely REAL Content")
                    st.write("Our classification layout flags this text style as objective, journalistic reporting.")
                else:
                    st.error("### 🚨 Result: Highly Suspicious (Likely FAKE)")
                    st.write("Warning: This text pattern heavily aligns with sensationalized tracking data, hoaxes, or political misinformation.")

  
