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
        # Add a custom User-Agent header so news websites don't block our app request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None, f"Could not access website (Error Code: {response.status_code})"
        
        # Parse the page HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements that aren't readable news text
        for script in soup(["script", "style"]):
            script.extract()
            
        # Extract paragraph elements (standard for news articles)
        paragraphs = soup.find_all('p')
        article_text = " ".join([p.get_text() for p in paragraphs])
        
        # Clean up whitespace
        clean_text = " ".join(article_text.split())
        return clean_text, None
        
    except Exception as e:
        return None, str(e)

# 2. Pull a Massive Real-World Dataset
@st.cache_data
def load_real_dataset():
    url = "https://raw.githubusercontent.com/jillanisofttech/fake-or-real-news/master/fake_or_real_news.csv"
    df = pd.read_csv(url)
    return df[['text', 'label']]

# 3. Model Training Pipeline
@st.cache_resource
def train_model():
    df = load_real_dataset()
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7, ngram_range=(1,2))),
        ('classifier', PassiveAggressiveClassifier(max_iter=50, random_state=42))
    ])
    pipeline.fit(df['text'], df['label'])
    return pipeline

# Train the AI
with st.spinner("🤖 Adjusting AI settings to read text and links... please wait..."):
    model = train_model()

# 4. Interactive User Interface
st.title("📰 Smart News Analyzer")
st.write("Our AI checks text patterns for integrity. You can paste a full news paragraph **OR** a direct link (URL) to a news article.")

user_input = st.text_area("Paste News Text or News Article Link here:", height=180, placeholder="https://example.com/news-story  OR  Paste paragraph...")

if st.button("Verify Content", type="primary"):
    text_to_analyze = user_input.strip()
    
    if not text_to_analyze:
        st.warning("⚠️ Please provide text or a link to analyze.")
    else:
        # Check if the input looks like a web link
        if text_to_analyze.startswith("http://") or text_to_analyze.startswith("https://"):
            with st.spinner("🌐 Accessing the website and scanning the article text..."):
                scraped_text, error = scrape_text_from_url(text_to_analyze)
                
            if error:
                st.error(f"❌ Failed to read the link. Reason: {error}")
                st.info("Tip: Some premium news websites block automated reading tools. Try copying and pasting the text block manually instead!")
                text_to_analyze = None
            else:
                text_to_analyze = scraped_text
                st.info(f"✨ Successfully retrieved text content from link! ({len(text_to_analyze.split())} words found)")

        # Run the prediction if we have clean text to work with
        if text_to_analyze:
            if len(text_to_analyze.split()) < 5:
                st.warning("⚠️ The retrieved text is too short. Please provide a link or block with more sentences.")
            else:
                prediction = model.predict([text_to_analyze])[0]
                
                st.markdown("---")
                if prediction == "REAL":
                    st.success("### ✅ Result: Likely REAL Content")
                    st.write("The linguistic structure, formatting, and phrasing pattern match verified news standards.")
                else:
                    st.error("### 🚨 Result: Highly Suspicious (Likely FAKE)")
                    st.write("Warning: This content contains significant linguistic clusters tied to hoaxes or highly biased reporting.")
       
    

            
