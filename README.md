# 🦅 BudgetHawk — Laurier Financial OS
### Created by Daniel Ramirez Bumaguin and Simran Badwal

An AI-powered, single-page financial dashboard built for Wilfrid Laurier University students to calculate, project, and visually model their complete financial runway — from tuition costs through to long-term wealth building.

> ⚠️ **Disclaimer:** This tool is for **educational and illustrative purposes only** and does **not** constitute financial, investment, tax, or legal advice. Past ETF returns are historical and do not guarantee future performance. Consult a licensed financial advisor before making any investment decisions.

---

## ✨ Features

### 📊 Expense Command Center (Budget Tab)
- **Guided Onboarding Wizard** — step-by-step setup for campus, residency, degree, living situation, and transportation
- **Dynamic Timeline** — toggle between Academic Year and Academic Term views
- **Real Laurier Data** — pulls live tuition, residence, meal plan, incidental fees, and gas prices from an institutional dataset
- **Custom Expense Ledger** — add one-time or recurring custom costs with full line-item breakdowns
- **Income Tracking** — weekly, bi-weekly, or monthly income offsets against burn rate
- **Stability Score** — real-time financial health metric (Critical → Strong) based on savings runway
- **Trajectory Chart** — per-term balance graph showing savings depletion over time

### 🤖 Gemini AI Copilot
- **AI Salary Estimation** — enter your degree + target job title and get a Gemini-powered median starting salary estimate with confidence rating

### 📈 Financial Trajectory (Investment Calculator)
- **Post-Graduation Wealth Simulator** — models net worth growth from graduation to retirement
- **2025 Canadian Tax Engine** — full Federal + Ontario provincial tax brackets, CPP2, and EI deductions with real-time after-tax salary display
- **Year-by-Year Investment Ledger** — detailed table with Gross Salary, After-Tax Salary, Monthly/Annual Contributions, Investment Gains, and Net Worth per year
- **Inflation-Adjusted Target Tracking** — highlights the exact year you hit your target (adjusted for inflation) with a milestone banner and "Rest of Career" divider
- **Negative Net Worth Support** — ledger and chart accurately reflect debt during payoff years
- **Start Working Year** — auto-synced from tuition timeline (graduation year) with manual override
- **Salary Adjustments** — schedule percentage raises or new absolute salaries at specific years to model career progression (saved to JSON)
- **ETF Quick-Picker** — auto-fill expected returns from Canadian all-equity ETF CAGR data:
  | ETF  | Inception | CAGR   |
  |------|-----------|--------|
  | XEQT | Aug 2019  | 12.9%  |
  | VEQT | Jan 2019  | 13.5%  |
  | ZEQT | Jan 2022  | 12.5%  |
  | TEQT | Apr 2025  | 12.0%  |
- **ETF Recommendation Cards** — VEQT, XEQT, ZEQT, TEQT with MER, geographic allocations, and risk profiling based on investment horizon
- **Debt Import** — pull education burn total from the Budget tab as starting debt
- **Compound Interest Controls** — adjustable savings rate, return rate, inflation rate, compounding frequency (annual/quarterly/monthly)

### 💾 Save & Restore
- **JSON Export/Import** — full dashboard state including all calculator inputs, salary adjustments, and trajectory data
- **Session Persistence** — import a save file to skip onboarding and jump straight into the calculator with all values restored

### 📄 Flight Plan Export
- **PDF Financial Statements** — generate A4 reports with full term-by-term breakdowns

---

## 🏗️ Tech Stack

| Layer       | Technology                             |
|-------------|----------------------------------------|
| Backend     | Python 3, Flask 3.1                    |
| Frontend    | HTML5, JavaScript, TailwindCSS         |
| AI          | Google Gemini 2.5 Flash (Vision + Text)|
| Charts      | Chart.js                               |
| Data        | Pandas, OpenPyXL (Excel data source)   |
| Templating  | Jinja2                                 |

---

## 📁 Project Structure

```
lcs2026-main/
├── app.py              # Flask entry point (port 8000)
├── routes.py           # API routes (/api/calculate, /api/upload, /api/estimate-salary)
├── data_store.py       # Data layer — tuition, residence, gas, incidental fee lookups
├── ai_parser.py        # Gemini API integration (invoice parsing + salary estimation)
├── requirements.txt    # Python dependencies
├── .env.example        # API key template
├── data/
│   └── Laurier Financial OS Data.xlsx   # Institutional dataset
└── templates/
    └── dashboard.html  # Single-page app (UI + all client-side logic)
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd lcs2026-main
```

### 2. Create & activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv env
env\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_key_here
   ```

> The `.env` file is git-ignored and stays local.

---

## ▶️ Running the Dashboard

```bash
python app.py
```

Navigate to **http://127.0.0.1:8000** in your browser.

---

## 🧮 Financial Engine Details

### Tax Calculation (2025)
The trajectory calculator implements the full 2025 Canadian Federal + Ontario Provincial tax bracket system:
- **Federal**: 15% → 20.5% → 26% → 29% → 33% across 5 brackets
- **Ontario**: 5.05% → 9.15% → 11.16% → 12.16% → 13.16% across 5 brackets
- **CPP2**: Employee contribution at 5.95% (max pensionable earnings $71,300)
- **EI**: 1.64% premium (max insurable earnings $65,700)

### Salary Growth Model
- Base salary grows with inflation annually
- Salary adjustments override or compound on the base:
  - **% Raise**: compounds on the current adjusted gross
  - **New Salary**: sets an absolute gross for that year — inflation compounds from that year onward (not from year 0)

### Investment Simulation
- Compound interest with configurable frequency (monthly/quarterly/annual)
- Debt payoff mode: contributions reduce debt before investing
- Inflation-adjusted target detection per year
- Chart runs from Start Working Year to Retirement Age

---

## 👥 Team

Built for **LCS 2026 Hack to the Future!**
