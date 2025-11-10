# DCF Valuation Calculator with Advanced Visualizations

A professional-grade **Discounted Cash Flow (DCF) valuation tool** built in Python that fetches real company data from Yahoo Finance and generates comprehensive visualizations to understand intrinsic stock value.

Perfect for quantitative portfolio managers, finance analysts, and investors who want to make data-driven valuation decisions backed by rigorous DCF analysis.

---

## 🎯 Features

### Core Valuation Capabilities
- **Real-time Financial Data**: Fetches company metrics directly from Yahoo Finance (Beta, Market Cap, EBIT, Debt, Cash, CapEx)
- **WACC Calculation**: Automatically computes Weighted Average Cost of Capital using CAPM
- **Free Cash Flow Forecasting**: Projects FCFF based on historical base year with configurable growth rates
- **Terminal Value Analysis**: Uses perpetuity growth model for long-term value estimation
- **Enterprise to Equity Bridge**: Calculates the complete valuation waterfall

### Advanced Visualizations (6 Professional Charts)
1. **Sensitivity Analysis Heatmap** - Shows how valuation changes with WACC and growth assumptions
2. **Waterfall Chart** - Visualizes Enterprise Value → Equity Value bridge with capital structure impact
3. **DCF Components Breakdown** - Bar chart showing PV contribution of each forecast year vs terminal value
4. **Price Comparison** - Current market price vs intrinsic value with upside/downside percentage
5. **WACC Breakdown** - Pie chart showing cost of equity vs cost of debt contribution
6. **Cash Flow Forecast** - Line chart displaying projected FCFF growth trajectory

All visualizations are saved as a high-resolution PNG dashboard for easy sharing and analysis.

### Robust Error Handling
- Validates all user inputs (numeric ranges, positive values)
- Gracefully handles missing data from Yahoo Finance
- Provides fallback values and informative error messages
- Supports multi-exchange tickers (US, Swiss, Tokyo, etc.)

---

## 📋 Requirements

- Python 3.7+
- yfinance
- numpy
- pandas
- matplotlib
- seaborn

---

## 💻 Quick Start

### Run the Calculator
```bash
python dcf_viz.py
```

### Example Input Session
```
Stock Ticker (e.g., MSFT, NESN.SW, 7203.T): MSFT
Country Risk-Free Rate (%) [e.g., 4.2]: 4.2
Country Equity Risk Premium (%) [e.g., 5.0]: 5.5
Forecast Period (Years) [e.g., 5]: 5
Perpetual Growth Rate (%) [e.g., 2.5]: 2.5
Use custom short-term FCFF growth rate? (y/n, default: n): n
```

### Output
The script generates:
1. **Console Summary** - Detailed DCF calculations and results
2. **PNG Visualization** - `[TICKER]_DCF_Analysis.png` with 6 professional charts

---

## 📊 Input Parameters Explained

### Stock Ticker
- **Format**: Ticker symbol for any exchange supported by Yahoo Finance
- **Examples**: 
  - US: `MSFT`, `AAPL`, `GOOGL`, `TSLA`
  - Swiss: `NESN.SW` (Nestlé)
  - Tokyo: `7203.T` (Toyota)
  - UK: `SHEL.L` (Shell)

### Country Risk-Free Rate (%)
- **Definition**: Yield on 10-year government bond of the company's country
- **Examples**:
  - US: 4.2% (check [US Treasury](https://www.treasury.gov))
  - Switzerland: 0.8%
  - Emerging markets: 6-10%
- **Why it matters**: Base return with zero risk; foundation of cost of equity

### Country Equity Risk Premium (%)
- **Definition**: Historical premium that stocks have earned above risk-free rate
- **Standard values**:
  - US/Developed Markets: 5.0% - 6.0%
  - Emerging Markets: 7.0% - 9.0%
- **Resource**: [Damodaran's Equity Risk Premium Data](http://pages.stern.nyu.edu/~adamodar/)
- **Why it matters**: Captures market risk premium for equity investors

### Forecast Period (Years)
- **Definition**: Number of years to explicitly forecast free cash flows
- **Recommended**:
  - Conservative: 5 years
  - Standard: 10 years
  - Aggressive/Growth: 5-7 years (with high growth assumptions)
- **Why it matters**: Balance between predictability and long-term value

### Perpetual Growth Rate (%)
- **Definition**: Long-term growth rate used in terminal value calculation
- **Best practices**:
  - Developed markets: 2.0% - 2.5% (GDP growth + inflation)
  - Emerging markets: 3.0% - 4.0%
  - **Golden Rule**: Never exceed WACC; preferably use GDP growth rate
- **Warning**: Most common DCF mistake is overstating perpetual growth
- **Why it matters**: Terminal value typically represents 60-80% of total value

### Short-Term FCFF Growth Rate (Optional)
- **Definition**: Custom annual growth rate for forecast period (overrides default 5%)
- **Use cases**:
  - High-growth companies: 10% - 20%
  - Mature/declining companies: 2% - 4%
  - If left blank: Defaults to 5%
- **Why it matters**: Critical for capturing company-specific growth trajectory

---

## 📈 Understanding the Visualizations

### 1. Sensitivity Analysis Heatmap
**What it shows**: How intrinsic share value changes across different WACC and perpetual growth rate assumptions

**How to read**:
- **Green cells** = Higher valuations (more optimistic scenario)
- **Red cells** = Lower valuations (more pessimistic scenario)
- **Blue box** = Your base case assumptions
- **Range** = WACC ±20%, Perpetual Growth varies with WACC constraint

**What it tells you**:
- Tight clustering around base case = Robust valuation with high confidence
- Wide spread = High sensitivity; small changes in assumptions cause large valuation swings
- Dominated by one edge = Model is driven by specific assumption; validate carefully

**Pro tip**: If your upside target is 20% but sensitivity shows range of -40% to +80%, your conviction should be low—model risk is high.

### 2. Waterfall Chart: Enterprise to Equity Value Bridge
**What it shows**: How Enterprise Value transforms to Equity Value

**Formula visualized**: `Equity Value = Enterprise Value - Total Debt + Cash`

**Components**:
1. **Enterprise Value** (starting point) - Value of business to all capital providers
2. **Less: Total Debt** (red bar downward) - Obligation to creditors
3. **Plus: Cash** (green bar upward) - Available liquid assets
4. **Equity Value** (ending point) - Value available to shareholders

**What it tells you**:
- If debt bar is huge = Company is highly leveraged; equity is riskier
- If cash bar is significant = Downside protection; equity value more stable
- Negative equity value = Company is insolvent (enterprise value < debt)

**Pro tip**: For valuation, focus on enterprise value first. Waterfall shows why equity value differs from EV due to capital structure.

### 3. DCF Components Breakdown
**What it shows**: Present value contribution of each forecast year's free cash flow plus terminal value

**Key insight**: Terminal value (final bar) typically dominates—often 60-80% of total

**What it tells you**:
- If terminal value >85% = Valuation heavily depends on perpetual growth assumption (risky)
- If fairly distributed across years = Valuation more grounded in near-term cash flows (safer)
- Negative early years = Company currently unprofitable (validate growth path)

**Pro tip**: Question your perpetual growth assumption if terminal value exceeds 80%. Consider more conservative estimates.

### 4. Price Comparison
**What it shows**: Current market price vs. your DCF intrinsic value

**Output includes**: 
- Current stock price (from Yahoo Finance)
- Intrinsic value per share (from DCF)
- Upside/downside percentage

**Color coding**:
- **Green** = Stock undervalued; intrinsic > market price
- **Red** = Stock overvalued; intrinsic < market price

**Investment implications**:
- **>20% upside** = Potentially significant buying opportunity
- **10-20% upside** = Moderate buying opportunity
- **-10% to +10%** = Fairly valued
- **<-20% downside** = Potentially overvalued

**Pro tip**: Don't trade solely on DCF signals. Use as one input alongside technical analysis, sentiment, and catalysts.

### 5. WACC Breakdown
**What it shows**: Pie chart of how cost of equity and cost of debt contribute to total WACC

**Interpretation**:
- **Cost of Equity weight** = % financed by equity; reflects shareholder cost
- **Cost of Debt weight** = % financed by debt; reflects creditor cost (lower due to tax shield)

**What it tells you**:
- Equity-heavy (90%+) = Lower leverage but higher cost of capital
- Balanced capital structure (40-60% debt) = Optimal WACC for most companies
- Highly leveraged (70%+ debt) = Financial risk increases significantly

**Pro tip**: Companies with low WACC (5-7%) have competitive advantages; companies with high WACC (12%+) face steep hurdle rates.

### 6. Cash Flow Forecast
**What it shows**: Projected FCFF growth over your forecast period

**Elements**:
- **Blue line** = Forecasted free cash flows year-by-year
- **Orange dashed line** = Base year FCFF (for comparison)
- **Data labels** = Exact values at each point

**What it tells you**:
- Steep upward slope = Aggressive growth assumptions
- Flat trajectory = Mature company assumptions
- Negative values = Currently unprofitable (validate turnaround case)

**Pro tip**: Compare this trajectory to company's historical FCFF growth. If forecast assumes 15% growth but historical is 3%, justify the inflection point.

---

## 📊 Sample Output

After running the calculator, you'll see console output like:

```
============================================================
DCF VALUATION SUMMARY
============================================================

--- Ticker: MSFT (MICROSOFT CORPORATION) ---
Current Stock Price: $420.50

--- Input Parameters ---
Risk-Free Rate: 4.20%
Equity Risk Premium: 5.50%
Forecast Period: 5 years
Perpetual Growth Rate: 2.50%

--- Company Metrics ---
Beta: 0.90
Market Cap: $3,150B
Total Debt: $65B
Cash: $75B
Tax Rate: 15.3%

--- WACC Calculation ---
Cost of Equity (CAPM): 9.15%
Cost of Debt (after-tax): 2.80%
WACC: 8.62%

--- Free Cash Flow Analysis ---
EBIT: $88,500M
Base Year FCFF: $65,200M
Forecasted FCFF (Year 1-5):
  Year 1: $68,460M
  Year 2: $71,883M
  Year 3: $75,477M
  Year 4: $79,251M
  Year 5: $83,214M

--- Valuation ---
Terminal Value: $1,650B
Enterprise Value: $1,950B
Less: Total Debt: $65B
Plus: Cash: $75B
Equity Value: $1,960B

Shares Outstanding: 2,580,000,000

*** INTRINSIC VALUE PER SHARE: $759.30 ***

Current Price: $420.50
Upside/Downside: +80.50%
→ Stock appears UNDERVALUED by 80.5%

✓ Visualizations saved as: MSFT_DCF_Analysis.png

============================================================
```

---

## 🔍 Key Formulas & Calculations

### Cost of Equity (CAPM)
```
Cost of Equity = Risk-Free Rate + (Beta × Equity Risk Premium)
```

### Weighted Average Cost of Capital (WACC)
```
WACC = (E/V × Cost of Equity) + (D/V × Cost of Debt × (1 - Tax Rate))

Where:
E = Market value of equity
V = Total firm value (E + D)
D = Market value of debt
```

### Free Cash Flow to Firm (FCFF)
```
FCFF = EBIT × (1 - Tax Rate) + Depreciation - CapEx - Change in Working Capital
```

### Terminal Value (Perpetuity Growth Model)
```
Terminal Value = FCFF_Final × (1 + Perpetual Growth Rate) / (WACC - Perpetual Growth Rate)
```

### Enterprise Value (DCF)
```
EV = Σ [FCFF_Year_t / (1 + WACC)^t] + [Terminal Value / (1 + WACC)^n]

Where:
t = Year 1 to n (forecast period)
n = Final year of forecast
```

### Equity Value
```
Equity Value = Enterprise Value - Total Debt + Cash
```

### Intrinsic Value Per Share
```
Share Price = Equity Value / Shares Outstanding
```

---

## ⚠️ Important Caveats & Best Practices

### DCF Limitations
- **Garbage in, garbage out**: Model quality depends entirely on input assumptions
- **Terminal value dominance**: Often 60-80% of value; small growth rate changes cause massive swings
- **Point estimate, not a range**: The final number is ONE scenario, not a prediction
- **Past performance ≠ future results**: Historical metrics don't guarantee future FCFF growth

### How to Use Responsibly
1. **Run sensitivity analysis**: The heatmap is more valuable than any single number
2. **Cross-validate with multiples**: Compare DCF result to EV/EBITDA, P/E, P/B multiples
3. **Document assumptions**: Keep a record of inputs and reasoning for future reference
4. **Update regularly**: Rerun quarterly after earnings; assumptions change
5. **Use for ranking, not precision**: Better for "which stock is cheapest?" than "exact value is $47.32"

### Common Mistakes to Avoid
- ❌ Using perpetual growth >3% for mature companies
- ❌ Ignoring terminal value sensitivity; not testing assumptions
- ❌ Forgetting to update inputs with new financial data
- ❌ Using DCF as sole investment criterion
- ❌ Overstating near-term growth (forecast period growth should be conservative)

### Validation Checklist
- [ ] Risk-free rate reflects actual government bond yields
- [ ] Equity risk premium aligns with published research (Damodaran, Ibbotson)
- [ ] Perpetual growth ≤ WACC (otherwise model breaks)
- [ ] FCFF forecast growth is justified by company fundamentals
- [ ] Beta is reasonable for industry (compare to peers)
- [ ] Tax rate is consistent with company's recent history
- [ ] Terminal value as % of EV seems reasonable (ideally 50-75%)

---

## 📚 Resources & References

### Learning Materials
- **Damodaran's Corporate Finance**: [Valuation Lectures](http://pages.stern.nyu.edu/~adamodar/)
- **Investment Banking Fundamentals**: Focus on DCF mechanics and assumption setting
- **Financial Modeling**: Learn to build 3-statement models for accurate FCFF

### Data Sources
- **Risk-Free Rate**: [US Treasury](https://www.treasury.gov/resource-center/data-chart-center/interest-rates/)
- **Equity Risk Premium**: [Damodaran ERP Data](http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html)
- **Company Data**: [Yahoo Finance](https://finance.yahoo.com/)
- **Comparable Multiples**: [Stock Screening Sites](https://finviz.com/)

### Academic Research
- Fama, French (2004): "The Capital Asset Pricing Model: Expectations and Reality"
- Brealey, Myers, Allen: "Principles of Corporate Finance" (Chapters on DCF)
- Damodaran: "Damodaran on Valuation" (Comprehensive DCF textbook)

---

## 📝 Examples

### Example 1: Mature Tech Company (Microsoft)
```
Ticker: MSFT
Risk-Free Rate: 4.2%
ERP: 5.5%
Forecast Years: 5
Perpetual Growth: 2.5%
Short-term Growth: 5%

Expected Result: Moderate upside; low sensitivity; mature company dynamics
```

### Example 2: High-Growth Company (Tesla)
```
Ticker: TSLA
Risk-Free Rate: 4.2%
ERP: 6.0% (higher risk)
Forecast Years: 10
Perpetual Growth: 3.0%
Short-term Growth: 15% (custom growth)

Expected Result: High sensitivity; significant valuation range; terminal value critical
```

### Example 3: International Company (Nestlé)
```
Ticker: NESN.SW
Risk-Free Rate: 0.8% (Swiss 10-year)
ERP: 5.5%
Forecast Years: 5
Perpetual Growth: 2.0%
Short-term Growth: 3%

Expected Result: Low WACC; stable dividend payer; capital-efficient business
```

---

## ⭐ Support

If this tool helped you in your analysis, please:
- ⭐ Star the repository
- 🐛 Report issues and bugs
- 💡 Suggest features and improvements
- 📢 Share with other analysts and portfolio managers

---

## 👨‍💼 Author

Built for **quantitative portfolio managers and finance analysts** who want professional-grade valuation tools.

**Built with**: Python, yfinance, pandas, numpy, matplotlib, seaborn

**Last Updated**: November 2025

---

## 📬 Contact & Questions

For questions, suggestions, or collaboration opportunities:
- Open an issue on GitHub
- Reach out with valuation questions and use cases
- Share your analysis results and feedback

---

**Happy Valuation! 🚀📊**

*Disclaimer: This tool is for educational and analytical purposes. Always conduct thorough due diligence and consult financial professionals before making investment decisions.*
