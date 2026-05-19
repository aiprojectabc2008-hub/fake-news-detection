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

# 2. Self-Contained, Balanced Training Dataset (No External Web Links Needed!)
@st.cache_resource
def train_model():
    # A diverse dictionary of factual journalistic reports vs classic fake news formats
    training_data = {
        'text': [
            # --- REAL NEWS SAMPLES (Objective, neutral, formal language) ---
            "The Federal Reserve announced a quarter-percentage-point interest rate hike this morning following months of intense debate among central bank governors regarding stubborn inflation.",
            "The prime minister signed the historic climate and green energy bill into law today after several weeks of parliamentary debate and amendments.",
            "Local municipal leaders have raised over $50,000 via community grants to restore and save the historic downtown public library from permanent closure.",
            "The labor department metrics released earlier this week show national unemployment rates have flattened out, though manufacturing indexes saw a minor drop.",
            "Public health officials issued a standard advisory confirming that annual influenza vaccine distributions will begin next week across local clinics.",
            "The supreme court voted to uphold the regulatory standards on interstate commerce, affecting environmental policies across three neighboring states.",
            "Shares of major technology companies fluctuated sharply following the closing bell after several firms reported lower-than-expected quarterly hardware revenue.",
            "The space agency successfully launched its latest meteorological satellite into orbit today, aiming to improve regional storm tracking capabilities.",
            
            # --- FAKE NEWS SAMPLES (Sensationalism, conspiracy keywords, exclamation marks) ---
            "BREAKING: WikiLeaks hacks have officially confirmed shocking secret underground networks operating under local pizza shops led by top political elites!",
            "ALERT: The government is releasing invisible trackable nano-bots via regular tap water networks to monitor citizens without their knowledge or consent!",
            "SHOCKING SECRET: Drinking five gallons of fresh organic lemon juice daily completely cures all terminal illnesses and major diseases instantly!",
            "CONFIRMED: The earth is actually completely hollow and a secret elite class lives inside controlling the global weather patterns using giant lasers!",
            "URGENT WARNING: The latest health clinics are hiding microchips inside common medicine to track your physical location and movements!",
            "Leaked top-secret military files prove that ancient alien civilizations built a massive command base directly beneath the dark side of the moon.",
            "MUST SEE: A rogue anonymous whistleblower just uploaded video evidence showing elite bankers staging major global economic events in secret backrooms.",
            "The mainstream media is completely hiding the truth about a newly discovered miracle vegetable that reverses aging overnight because of big pharma profit!"
        ],
        'label': [
            'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL',
            'FAKE', 'FAKE', 'FAKE', 'FAKE', 'FAKE', 'FAKE', 'FAKE', 'FAKE'
        ]
    }
    
    df = pd.DataFrame(training_data)
    
    # TF-IDF converts text patterns to mathematical weights
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_df=1.0, ngram_range=(1,2))),
        ('classifier', PassiveAggressiveClassifier(max_iter=100, random_state=42))
    ])
    pipeline.fit(df['text'], df['label'])
    return pipeline

# Train the AI
with st.spinner("🤖 Initializing AI Text and Link Classifier..."):
    model = train_model()

# 3. Interactive User Interface Layout
st.title("📰 AI News Text & Link Analyzer")
st.write("Our AI checks text patterns for integrity. Paste a news paragraph **OR** an active news link (URL).")

user_input = st.text_area("Paste News Text or Article URL here:", height=180, placeholder="https://example.com/story  OR  Paste paragraph...")

if st.button("Verify Content", type="primary"):
    text_to_analyze = user_input.strip()
    
    if not text_to_analyze:
        st.warning("⚠️ Please enter a text paragraph or web link first.")
    else:
        # Check if the input is a web link
        if text_to_analyze.startswith("http://") or text_to_analyze.startswith("https://"):
            with st.spinner("🌐 Accessing link and extracting article content..."):
                scraped_text, error = scrape_text_from_url(text_to_analyze)
                
            if error:
                st.error(f"❌ Web Scraper Blocked. Reason: {error}")
                st.info("Note: Many premium news sites block automated bots. Try copying and pasting the text manually!")
                text_to_analyze = None
            else:
                text_to_analyze = scraped_text
                st.info(f"✨ Successfully pulled text content from link ({len(text_to_analyze.split())} words found).")

        # Run AI prediction if text is ready
        if text_to_analyze:
            if len(text_to_analyze.split()) < 5:
                st.warning("⚠️ Please provide a longer statement or paragraph (at least 5 words) for an accurate reading.")
            else:
                prediction = model.predict([text_to_analyze])[0]
                
                st.markdown("---")
                if prediction == "REAL":
                    st.success("### ✅ Result: Matches REAL News Patterns")
                    st.write("The vocabulary structure, neutral framing, and context mirror standard objective journalism.")
                else:
                    st.error("### 🚨 Result: Matches FAKE News Patterns")
                    st.write("Warning: This content uses aggressive language clusters, emotional triggers, or specific phrasing linked to misinformation hoaxes.")

   


   

              
          
                 
