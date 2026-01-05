# Deep Data Mining System: Project "Information Warfare" - Detailed Design Document

## 1. Vision & Philosophy
**Core Philosophy:** Investment is an information war. The goal is not just to aggregate data, but to *distill* signal from noise, perform deep reasoning, and provide actionable intelligence (Alpha) using AI.
**Objective:** Build an automated system that acts as a "Virtual Investment Analyst," delivering structured Pre-market Intelligence and Post-market Reviews for specific mutual funds.

---

## 2. System Architecture

The system follows a **Pipeline Architecture** with four distinct layers:

```mermaid
graph TD
    A[Data Ingestion Layer] --> B[Context & Processing Layer]
    B --> C[Intelligence Layer (AI Brain)]
    C --> D[Presentation & Delivery Layer]
    
    subgraph Data Sources
    D1[AKShare (Market Data)]
    D2[Tavily (Web Search)]
    D3[User Config (Funds/Holdings)]
    end
    
    subgraph Storage (Expansion)
    S1[Local Cache (JSON/SQLite)]
    S2[Vector DB (Chroma/FAISS) - Future]
    end
```

### 2.1 Layer Details

#### A. Data Ingestion Layer (The Senses)
Responsible for gathering raw facts.
*   **Market Data (AKShare):**
    *   Real-time quotes (A-share/HK/US).
    *   Fund Holdings (Quarterly updates).
    *   Macro Indicators (Exchange rates, A50 futures).
*   **Open Intelligence (Tavily/Search):**
    *   Targeted queries: "Semiconductor industry policy changes last 24h", "Tencent Holdings latest analyst ratings".
    *   Sentiment scraping from news headers.

#### B. Context & Processing Layer (The Memory)
Responsible for preparing data for the AI.
*   **Holdings Mapper:** dynamically maps a Fund Code -> Top 10 Stocks -> Industries.
*   **Context Builder:** Assembles the "Prompt Context". E.g., combining *Yesterday's NAV drop* + *Top 1 holding's crash* + *Sector News* into a single context window.
*   **Expansion (Memory):** In the future, this layer will retrieve *past* reports to spot trend changes (e.g., "The AI was bullish on Semi last week, why bearish now?").

#### C. Intelligence Layer (The Brain - Gemini)
Responsible for reasoning and deduction.
*   **Model Selection:**
    *   *Gemini-2.0-Flash/Pro:* For fast, daily report generation.
    *   *Gemini-Pro-MaxThinking (Future):* For "Deep Dives" or quarterly rebalancing analysis.
*   **Cognitive Tasks:**
    *   **Correlation Analysis:** "Did the fund drop because of the sector or stock-specific bad news?"
    *   **Impact Assessment:** "How does the fed rate hike probability affect *this specific* growth fund?"
    *   **Sentiment Scoring:** Rating news from -5 (Bearish) to +5 (Bullish).

#### D. Presentation Layer (The Interface)
*   **MVP:** Markdown file generation in `reports/` folder.
*   **Expansion:** Push notifications (WeChat Work/DingTalk via Webhook), Email, or a local Streamlit Dashboard.

---

## 3. Functional Modules

### 3.1 Pre-market Intelligence (08:30 AM Trigger)
**Goal:** Prepare the user for the trading day.
1.  **Macro Scan:** Check US Close (Nasdaq/Dow), A50 Futures, USD/CNY.
2.  **Holdings Scan:** Search news for Top 10 holdings of target funds (Overnight news).
3.  **Synthesis:**
    *   *Input:* Macro Data + Holdings News + Fund Style (e.g., "Growth").
    *   *AI Task:* "Predict opening pressure. If Nasdaq dropped 2% and this fund is heavy on tech, predict a low open. Highlight specific risks."
    *   *Output:* "Strategy: Watch for low opening to buy" or "Risk Alert: Significant headwind."

### 3.2 Post-market Review (15:30 PM Trigger)
**Goal:** Explain *why* things happened.
1.  **Performance Check:** Get Fund Estimated NAV vs. Actual Index.
2.  **Attribution:**
    *   Get Top 10 holdings' daily change.
    *   *AI Task:* "The fund fell 1.5%, but its main sector only fell 0.5%. Find the culprit." (e.g., One specific stock crashed).
3.  **Flow Analysis:** Northbound money flows in the fund's core sectors.

---

## 4. Expansion & Roadmap (Deep Thinking)

To truly achieve "Information Warfare" capabilities, the system must evolve beyond simple reporting.

### Phase 1: The Analyst (Current Scope)
*   **Capability:** Daily automated summaries based on rigid rules.
*   **Tech:** Python scripts + LLM API.

### Phase 2: The Researcher (Agentic Workflow)
*   **Capability:** Autonomous "Deep Dives".
    *   *Trigger:* User asks "Why is Liquor falling continuously?"
    *   *Action:* Agent breaks down the question -> Searches Policy -> Searches Inventory levels -> Searches Competitor pricing -> Synthesizes a 5-page report.
*   **Tech:** LangGraph or simple Loop-based Agent.

### Phase 3: The Historian (RAG & Memory)
*   **Capability:** Long-term trend tracking.
    *   *Feature:* "Vector Memory". Store every daily report.
    *   *Benefit:* The AI can say, "This is the 3rd time this month we've seen negative news on 'Inventory', suggesting a structural problem." (Connecting dots over time).

### Phase 4: The Sentinel (Real-time Monitoring)
*   **Capability:** Intraday alerts.
    *   *Action:* Loop every 15 mins. If a *major* keyword matches a holding (e.g., "Investigation", "Fraud", "Acquisition"), push an alert immediately.

---

## 5. Data Structures (Draft)

**Fund Config (`funds.json`):**
```json
{
  "funds": [
    {
      "code": "005827",
      "name": "E Fund Blue Chip",
      "strategy": "Value-Growth",
      "core_sectors": ["Liquor", "Internet"],
      "holdings_cache": ["00700.HK", "600519.SH"] // Updated weekly
    }
  ]
}
```

**Daily Report Output (`YYYY-MM-DD_{FundCode}.md`):**
*   **Header:** Fund Name | Date | Sentiment Score
*   **Section 1: The Morning Brief** (Macro + Risks)
*   **Section 2: The Afternoon Review** (Attribution + Flows)
*   **Section 3: AI Insights** (Hidden correlations / "The Signal")
