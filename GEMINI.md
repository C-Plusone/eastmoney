# Deep Data Mining System (Fund Analysis)

## Project Overview
This project is an AI-driven "Virtual Investment Analyst" designed to perform deep data mining on mutual funds. It aggregates financial data, performs web searches for news/sentiment, and uses Large Language Models (LLMs) to generate structured daily reports (Pre-market Intelligence and Post-market Reviews).

**Core Philosophy:** "Investment is an information war." The system aims to distill signal from noise to provide actionable intelligence.

## Tech Stack
*   **Language:** Python
*   **AI/LLM:** Google Gemini (`google-genai`), OpenAI (`openai`)
*   **Data Sources:**
    *   **Financial Data:** `akshare` (A-share, HK, US market data, Fund holdings)
    *   **Web Search:** `tavily-python` (News and sentiment analysis)
*   **Configuration:** `python-dotenv`

## Project Structure
```text
eastmoney/
├── config/
│   ├── settings.py       # Configuration loader (API keys, Providers)
│   └── funds.json        # Target funds configuration
├── src/
│   ├── data_sources/     # Data fetching adapters
│   │   ├── akshare_api.py   # Market & Fund data
│   │   └── web_search.py    # Tavily Search wrapper
│   ├── llm/              # LLM Integration
│   │   ├── client.py        # Client Factory (Gemini/OpenAI)
│   │   └── prompts.py       # System Prompts (Chinese)
│   └── analysis/         # Core Logic
│       ├── pre_market.py    # Morning strategy logic
│       └── post_market.py   # After-hours attribution logic
├── reports/              # Output directory for Markdown reports
├── main.py               # CLI Entry Point
├── requirements.txt      # Dependencies
├── design.md             # Original Idea
├── detailed_design.md    # Architecture & Roadmap
└── .env                  # API Keys (Secrets)
```

## Building and Running

### Prerequisites
1.  Python 3.10+
2.  API Keys for:
    *   Google Gemini (or OpenAI)
    *   Tavily Search

### Installation
```powershell
pip install -r requirements.txt
```

### Configuration
1.  Create/Edit `.env` file:
    ```env
    # LLM Provider: gemini or openai
    LLM_PROVIDER=gemini 
    
    # Google Gemini
    GEMINI_API_KEY=your_key
    GEMINI_API_ENDPOINT= # Optional custom endpoint
    
    # OpenAI (Optional)
    OPENAI_API_KEY=your_key
    OPENAI_BASE_URL= # Optional
    
    # Search
    TAVILY_API_KEY=your_key
    ```
2.  Edit `config/funds.json` to track specific funds.

### Usage Commands

**1. Pre-market Intelligence (Morning Brief):**
Analyzes macro data and overnight holdings news to predict opening sentiment.
```powershell
python main.py --mode pre
```

**2. Post-market Review (Daily Wrap-up):**
Analyzes daily performance, attribution (Alpha vs Beta), and sector flows.
```powershell
python main.py --mode post
```

## Development Conventions
*   **Modular Design:** Separated Data, LLM, and Analysis layers.
*   **Factory Pattern:** Used in `src/llm/client.py` to switch between LLM providers easily.
*   **Error Handling:** Robust fallbacks for missing data (e.g., using previous year's holdings if current year is empty).
*   **Localization:** Prompts are tuned for Chinese output (`src/llm/prompts.py`).

## Key Files Description
*   `detailed_design.md`: Contains the roadmap (Phases 1-4) and architectural vision.
*   `src/llm/client.py`: Handles the `google-genai` vs `openai` client instantiation.
*   `src/data_sources/akshare_api.py`: Wraps `akshare` functions, handles year fallback logic for holdings.
