import streamlit as st
import requests
from bs4 import BeautifulSoup

# 1. Page Layout Configuration
st.set_page_config(
    page_title="Live Fact-Checker",
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

# Helper Function: Automated Google/Web Reference Engine
def query_live_database(claim):
    """
    Automated Web Search Engine:
    Takes any statement, strips out filler words, searches a live index,
    and returns a verified historical abstract or reference if available.
    """
    try:
        # Format the text into a clean web query
        clean_query = claim.lower().replace("?", "").replace("is the", "").replace("is an", "").strip()
        url = f"https://api.duckduckgo.com/?q={clean_query}&format=json&no_html=1"
        response = requests.get(url, timeout=8).json()
        
        # 1. Check for a direct encyclopedic description
        abstract = response.get("AbstractText", "")
        
        # 2. If empty, check for a related dictionary/historical heading definition
        if not abstract and response.get("RelatedTopics"):
            abstract = response.get("RelatedTopics")[0].get("Text", "")
            
        return abstract if abstract else None
    except Exception:
        return None

# 2. Interactive User Interface
st.title("🔍 Automated Live Fact-Checker")
st.write("This engine scans web record summaries to help you evaluate if a name, entity, or historical claim is accurate.")

user_input = st.text_area(
    "Enter a statement or paste a link to verify:", 
    height=150, 
    placeholder="e.g., Narendra Modi, Rahul Gandhi, or paste an article url..."
)

if st.button("Verify Facts Live", type="primary"):
    text_to_analyze = user_input.strip()
    
    if not text_to_analyze:
        st.warning("⚠️ Please input text or a link first.")
    else:
        # URL link handling
        if text_to_analyze.startswith("http://") or text_to_analyze.startswith("https://"):
            with st.spinner("🌐 Accessing link and scraping text context..."):
                scraped_text, error = scrape_text_from_url(text_to_analyze)
            if error:
                st.error(f"❌ Web Scraper Blocked: {error}")
                text_to_analyze = None
            else:
                text_to_analyze = scraped_text

        # Run Live Automated Fact-Check
        if text_to_analyze:
            with st.spinner("🧠 Querying live global databases for reference data..."):
                web_evidence = query_live_database(text_to_analyze)
            
            st.markdown("---")
            
            if web_evidence:
                st.success("### ✅ Live Reference Context Retrieved")
                st.write("**Official Web Records State:**")
                st.info(web_evidence)
                st.write("📝 *How to evaluate your result:* Cross-reference the official text block above with your statement. If the details conflict (e.g., mismatching names/titles), your statement is likely incorrect.")
            else:
                st.warning("### ℹ️ No Conclusive Reference Found")
                st.write("The database couldn't find a direct match for that specific wording. Try simplifying your query to the main subject or names (e.g., searching 'Prime Minister of India' or 'Rahul Gandhi' directly).")
   
      
            
             
            
       
 
    
    
              
                   
