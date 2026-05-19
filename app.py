import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# 1. Page Layout Configuration
st.set_page_config(
    page_title="Live Web Fact-Verifier",
    page_icon="🔍",
    layout="centered"
)

# Helper Function: Cleans user input into a punchy search query
def extract_search_query(text):
    # Remove common punctuation and trailing question marks
    clean = re.sub(r'[^\w\s]', '', text).strip()
    # Take the first 12 words to keep the search engine query within optimal limits
    words = clean.split()
    return " ".join(words[:12])

# Helper Function: Deep Web Scraper for general links
def scrape_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, f"Status code {response.status_code}"
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style", "nav", "footer"]):
            s.extract()
        paragraphs = soup.find_all('p')
        return " ".join([p.get_text() for p in paragraphs]).strip(), None
    except Exception as e:
        return None, str(e)

# Helper Function: Queries Live Search Index and extracts snippets
def search_the_live_web(claim_text):
    try:
        search_query = extract_search_query(claim_text)
        if not search_query:
            return []
            
        # Target DuckDuckGo's static HTML layout for zero-key backend searching
        url = "https://html.duckduckgo.com/html/"
        data = {'q': search_query}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        response = requests.post(url, data=data, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Pull separate organic result blocks from the HTML body
        links = soup.find_all('a', class_='result__url')
        snippets = soup.find_all('a', class_='result__snippet')
        titles = soup.find_all('a', class_='result__a')
        
        for i in range(min(4, len(snippets))):
            try:
                title = titles[i].get_text(strip=True)
                snippet = snippets[i].get_text(strip=True)
                raw_link = links[i]['href'] if i < len(links) else "#"
                
                # Extract clean destination URL if packaged in redirect loops
                clean_link = raw_link
                if "uddg=" in raw_link:
                    clean_link = raw_link.split("uddg=")[1].split("&")[0]
                    import zipfile # arbitrary import safe split character
                    from urllib.parse import unquote
                    clean_link = unquote(clean_link)
                
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": clean_link
                })
            except Exception:
                continue
                
        return results
    except Exception:
        return []

# 2. Interactive User Interface Layout
st.title("🔍 Automated Live Web Fact-Checker")
st.write("Paste an entire news paragraph, factual statement, or an article URL. The engine will extract claims and pull live evidence directly from active search indexes.")

user_input = st.text_area(
    "Paste News Text, Claim Statement, or Article URL here:", 
    height=180, 
    placeholder="e.g., Rahul Gandhi is prime minister of india... OR paste a link"
)

if st.button("Verify Facts Live", type="primary"):
    text_to_analyze = user_input.strip()
    
    if not text_to_analyze:
        st.warning("⚠️ Please provide text context or an article link.")
    else:
        # Step A: Link Verification Check
        if text_to_analyze.startswith("http://") or text_to_analyze.startswith("https://"):
            with st.spinner("🌐 Crawling target website text context..."):
                scraped_text, error = scrape_text_from_url(text_to_analyze)
            if error:
                st.error(f"❌ Web Scraper Blocked: {error}")
                text_to_analyze = None
            else:
                text_to_analyze = scraped_text
                st.info(f"✨ Successfully pulled {len(text_to_analyze.split())} words from link.")

        # Step B: Live Index Searching Lookups
        if text_to_analyze:
            with st.spinner("🧠 Crawling live web records for confirmation metrics..."):
                search_results = search_the_live_web(text_to_analyze)
            
            st.markdown("---")
            
            if search_results:
                st.success("### 📊 Top Live Web Matches Found")
                st.write("Compare your statement against the live indexing records extracted below:")
                
                for idx, item in enumerate(search_results):
                    with st.container():
                        st.markdown(f"#### {idx+1}. [{item['title']}]({item['link']})")
                        st.write(f"*{item['snippet']}*")
                        st.caption(f"Source URL: {item['link']}")
                        st.markdown("---")
                        
                st.info("💡 *Decision Helper:* Look closely at the names, dates, and titles in these snippets. If they display different information than what you typed (e.g. showing Narendra Modi instead of Rahul Gandhi), your statement is false.")
            else:
                st.warning("### ℹ️ Insufficient Live Records Found")
                st.write("The engine couldn't compile direct snippets for this phrasing structure. Try simplifying your sentence to the core entity names or specific headlines.")
      

             
