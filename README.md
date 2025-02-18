# EchoSnap - Real-Time Misinformation Detection

EchoSnap is a powerful tool designed to help broadcasters and content creators detect misinformation in real-time. It analyzes live broadcast text, YouTube videos, and website links using multiple fact-checking sources, including Google Fact Check, Wikipedia, NewsData.io, and ClaimBuster. With sentiment analysis and a user-friendly interface, EchoSnap ensures that your content is accurate and trustworthy.

---

## Features

- **Real-Time Misinformation Detection**: Analyze live broadcast text, YouTube videos, and website links.
- **Multiple Fact-Checking Sources**: Integrates Google Fact Check, Wikipedia, NewsData.io, and ClaimBuster.
- **Sentiment Analysis**: Provides sentiment scores (Positive, Negative, Neutral) for each statement.
- **History Tracking**: Saves past results for easy reference.
- **User-Friendly Interface**: Clean and intuitive design with real-time feedback.

---

## How It Works

1. **Input Text**: Paste live broadcast text or transcription.
2. **YouTube Link**: Enter a YouTube video link to extract and analyze the transcript or description.
3. **Website Link**: Paste a website link to extract and analyze its content.
4. **Choose Fact-Checking Source**: Select from Google Fact Check, Wikipedia, NewsData.io, or ClaimBuster.
5. **Get Results**: View fact-checking results, sentiment analysis, and a visual distribution of misinformation.

---

## Technologies Used

- **Frontend**: Streamlit (Python) / React.js
- **Backend**: Python (TextBlob, Hugging Face Transformers)
- **APIs**: Google Fact Check, Wikipedia, NewsData.io, ClaimBuster
- **Database**: Firebase Firestore (for history tracking)
- **Visualization**: Plotly, Chart.js

---

## Installation

### For Streamlit (Python)
1. Clone the repository:
   ```bash
   git clone https://github.com/anusharao-7/EchoSnap.git
