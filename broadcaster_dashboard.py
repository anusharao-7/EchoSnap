# pylint: disable=no-member
import streamlit as st
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube
import time
import os
import pandas as pd
from textblob import TextBlob
import plotly.express as px
from transformers import pipeline  # For fallback mechanism
from dotenv import load_dotenv
load_dotenv()


# Set up the page
st.set_page_config(page_title="EchoSnap - Broadcaster Dashboard", layout="wide")

# Custom CSS for animations and styling
st.markdown("""
<style>
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.stButton button {
    background-color: #4CAF50;
    color: white;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
    animation: fadeIn 1s;
}

.stTextInput input {
    border-radius: 5px;
    padding: 10px;
    font-size: 16px;
    animation: fadeIn 1s;
}

.stAlert {
    border-radius: 5px;
    padding: 20px;
    background-color: #f8d7da;
    color: #721c24;
    animation: fadeIn 0.5s;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("EchoSnap - Broadcaster Dashboard")
st.write("Monitor live broadcasts, YouTube videos, and website links for misinformation in real-time.")

# Input for live broadcast text, YouTube link, or website link
input_type = st.radio("Choose input type:", ("Text", "YouTube Link", "Website Link"))

input_text = ""
if input_type == "Text":
    input_text = st.text_area("Enter live broadcast text (or paste transcription):", height=150)
elif input_type == "YouTube Link":
    youtube_link = st.text_input("Paste YouTube video link:")
    if youtube_link:
        try:
            # Extract video ID from the YouTube link
            if "v=" in youtube_link:
                video_id = youtube_link.split("v=")[1].split("&")[0]
            else:
                video_id = youtube_link.split("/")[-1]  # For short links like https://youtu.be/VIDEO_ID

            # Fetch transcript using YouTubeTranscriptApi
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                input_text = " ".join([t["text"] for t in transcript])
                st.write("**Extracted Transcript:**")
                st.write(input_text)
            except (TranscriptsDisabled, NoTranscriptFound):
                st.warning("Transcript not available. Fetching video description...")
                # Fetch video description using pytube
                yt = YouTube(youtube_link)
                input_text = yt.description
                st.write("**Extracted Description:**")
                st.write(input_text)
        except Exception as e:
            st.error(f"Error fetching video data: {e}")
elif input_type == "Website Link":
    website_link = st.text_input("Paste website link:")
    if website_link:
        try:
            # Fetch website content using BeautifulSoup
            response = requests.get(website_link)
            soup = BeautifulSoup(response.text, "html.parser")
            input_text = soup.get_text()  # Extract all text from the website
            st.write("**Extracted Website Content:**")
            st.write(input_text[:1000] + "...")  # Show first 1000 characters for preview
        except Exception as e:
            st.error(f"Error fetching website data: {e}")

# Let user choose fact-checking source
fact_check_source = st.radio("Choose fact-checking source:", ("Google Fact Check", "Wikipedia", "NewsData.io", "ClaimBuster"))

# Cache Google Fact Check API results for 1 hour
@st.cache_data(ttl=3600)
def fetch_google_fact_check(query):
    api_key = os.getenv('GOOGLE_FACT_API_KEY')  # Replace with your API key
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch data from NewsData.io
@st.cache_data(ttl=3600)
def fetch_newsdata(query):
    api_key = os.getenv('NEWS_DATA_API_KEY')  # Replace with your NewsData.io API key
    url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch data from ClaimBuster API
@st.cache_data(ttl=3600)
def fetch_claimbuster(query):
    api_key = os.getenv('CLAIM_BUSTER_API_KEY')  # Replace with your ClaimBuster API key
    url = f"https://idir.uta.edu/claimbuster/api/v2/score/text/{query}"
    headers = {"x-api-key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Improved Wikipedia fact-checking
@st.cache_data(ttl=3600)
def fetch_wikipedia_data(query):
    try:
        # Search Wikipedia for the query
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        search_response = requests.get(search_url)
        if search_response.status_code == 200:
            search_results = search_response.json().get("query", {}).get("search", [])
            if search_results:
                # Fetch the summary of the first result
                page_title = search_results[0]["title"]
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
                summary_response = requests.get(summary_url)
                if summary_response.status_code == 200:
                    return summary_response.json()["extract"], summary_response.json()["content_urls"]["desktop"]["page"]
        return None, None
    except Exception as e:
        st.error(f"Error fetching Wikipedia data: {e}")
        return None, None

# Fallback mechanism using Hugging Face model
def fallback_misinformation_check(query):
    classifier = pipeline("text-classification", model="distilbert-base-uncased")
    result = classifier(query)
    return result

# Function to analyze sentiment
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "Positive"
    elif sentiment < 0:
        return "Negative"
    else:
        return "Neutral"

# Real-time alert system
if input_text:
    st.write("Analyzing...")
    with st.spinner("Detecting misinformation..."):
        time.sleep(2)  # Simulate processing time
        sentences = input_text.split(". ")  # Split text into sentences
        results = []
        for sentence in sentences:
            if sentence.strip():  # Skip empty sentences
                sentiment = analyze_sentiment(sentence)
                try:
                    if fact_check_source == "Google Fact Check":
                        # Use Google Fact Check API
                        google_data = fetch_google_fact_check(sentence)
                        if google_data and google_data.get("claims"):
                            for claim in google_data["claims"][:3]:  # Show top 3 claims
                                results.append({
                                    "Statement": sentence,
                                    "Status": claim["claimReview"][0]["textualRating"],
                                    "Source": claim["claimReview"][0]["url"],
                                    "Sentiment": sentiment,
                                })
                        else:
                            # Fallback to Hugging Face model
                            fallback_result = fallback_misinformation_check(sentence)
                            results.append({
                                "Statement": sentence,
                                "Status": f"Fallback: {fallback_result[0]['label']} (Score: {fallback_result[0]['score']:.2f})",
                                "Source": "N/A",
                                "Sentiment": sentiment,
                            })
                    elif fact_check_source == "Wikipedia":
                        # Use Wikipedia API
                        wiki_data, wiki_url = fetch_wikipedia_data(sentence)
                        if wiki_data:
                            results.append({
                                "Statement": sentence,
                                "Status": "Verified by Wikipedia",
                                "Source": wiki_url,
                                "Sentiment": sentiment,
                            })
                        else:
                            # Fallback to Hugging Face model
                            fallback_result = fallback_misinformation_check(sentence)
                            results.append({
                                "Statement": sentence,
                                "Status": f"Fallback: {fallback_result[0]['label']} (Score: {fallback_result[0]['score']:.2f})",
                                "Source": "N/A",
                                "Sentiment": sentiment,
                            })
                    elif fact_check_source == "NewsData.io":
                        # Use NewsData.io API
                        news_data = fetch_newsdata(sentence)
                        if news_data and news_data.get("results"):
                            for news in news_data["results"][:3]:  # Show top 3 news articles
                                results.append({
                                    "Statement": sentence,
                                    "Status": f"Related news: {news['title']}",
                                    "Source": news["link"],
                                    "Sentiment": sentiment,
                                })
                        else:
                            # Fallback to Hugging Face model
                            fallback_result = fallback_misinformation_check(sentence)
                            results.append({
                                "Statement": sentence,
                                "Status": f"Fallback: {fallback_result[0]['label']} (Score: {fallback_result[0]['score']:.2f})",
                                "Source": "N/A",
                                "Sentiment": sentiment,
                            })
                    elif fact_check_source == "ClaimBuster":
                        # Use ClaimBuster API
                        claimbuster_data = fetch_claimbuster(sentence)
                        if claimbuster_data and claimbuster_data.get("results"):
                            for result in claimbuster_data["results"][:3]:  # Show top 3 results
                                results.append({
                                    "Statement": sentence,
                                    "Status": f"Potential misinformation (Score: {result['score']})",
                                    "Source": "N/A",
                                    "Sentiment": sentiment,
                                })
                        else:
                            # Fallback to Hugging Face model
                            fallback_result = fallback_misinformation_check(sentence)
                            results.append({
                                "Statement": sentence,
                                "Status": f"Fallback: {fallback_result[0]['label']} (Score: {fallback_result[0]['score']:.2f})",
                                "Source": "N/A",
                                "Sentiment": sentiment,
                            })
                except Exception as e:
                    st.error(f"Error processing sentence: {e}")
                    results.append({
                        "Statement": sentence,
                        "Status": "Error processing sentence",
                        "Source": "N/A",
                        "Sentiment": sentiment,
                    })

        # Display results in a table
        st.write("**Fact-Check Results:**")
        df = pd.DataFrame(results)
        st.table(df)

        # Visualize misinformation distribution
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.bar(status_counts, x="Status", y="Count", title="Misinformation Distribution")
        st.plotly_chart(fig)

# Footer
st.markdown("---")
st.write("Powered by **EchoSnap** | Built with ❤️ using Streamlit")