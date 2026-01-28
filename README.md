# Saudi Financial Database Chat

A Streamlit app for natural language querying of Saudi XBRL financial data using PandasAI and OpenRouter/Gemini.

## Features

- Query Saudi listed companies' financial data using natural language
- Multiple datasets: Analytics View, Filings, Financial Facts, Financial Ratios
- Interactive charts and data visualization
- Powered by PandasAI + Gemini 3 Flash

## Deployment to Streamlit Cloud

### Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it something like `saudi-financial-chat`
3. Make it public (required for Streamlit Cloud free tier)

### Step 2: Upload Files

Upload all files from this folder to your GitHub repository:
- `app.py` - Main application
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `data/` folder with all parquet files

### Step 3: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch
5. Set main file path to `app.py`
6. Click "Deploy"

### Step 4: Add Secrets (Important!)

After deployment, add your OpenRouter API key:

1. In Streamlit Cloud, go to your app settings
2. Click "Secrets" in the left sidebar
3. Add the following:

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-actual-api-key"
```

4. Click "Save"

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Sources

- Saudi Tadawul XBRL Financial Reports
- Pre-processed parquet files for fast loading
