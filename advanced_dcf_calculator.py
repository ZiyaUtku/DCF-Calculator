import yfinance as yf
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, Tuple
from matplotlib.patches import Rectangle

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


def validate_positive_number(value: str, name: str) -> float:
    """Validate and convert user input to positive float."""
    try:
        num = float(value)
        if num < 0:
            raise ValueError(f"{name} must be non-negative")
        return num
    except ValueError as e:
        print(f"Error: Invalid input for {name}. {str(e)}")
        sys.exit(1)


def validate_positive_integer(value: str, name: str) -> int:
    """Validate and convert user input to positive integer."""
    try:
        num = int(value)
        if num <= 0:
            raise ValueError(f"{name} must be greater than 0")
        return num
    except ValueError as e:
        print(f"Error: Invalid input for {name}. {str(e)}")
        sys.exit(1)


def get_user_inputs() -> Dict:
    """Prompt user for DCF calculation inputs."""
    print("\n" + "="*60)
    print("DCF CALCULATOR - User Inputs")
    print("="*60 + "\n")
    
    ticker = input("Stock Ticker (e.g., MSFT, NESN.SW, 7203.T): ").strip().upper()
    if not ticker:
        print("Error: Ticker cannot be empty")
        sys.exit(1)
    
    risk_free_rate = validate_positive_number(
        input("Country Risk-Free Rate (%) [e.g., 4.2]: ").strip(),
        "Risk-Free Rate"
    )
    
    equity_risk_premium = validate_positive_number(
        input("Country Equity Risk Premium (%) [e.g., 5.0]: ").strip(),
        "Equity Risk Premium"
    )
    
    forecast_years = validate_positive_integer(
        input("Forecast Period (Years) [e.g., 5]: ").strip(),
        "Forecast Period"
    )
    
    perpetual_growth = validate_positive_number(
        input("Perpetual Growth Rate (%) [e.g., 2.5]: ").strip(),
        "Perpetual Growth Rate"
    )
    
    # Optional: short-term FCFF growth rate
    use_custom_growth = input("\nUse custom short-term FCFF growth rate? (y/n, default: n): ").strip().lower()
    
    short_term_growth = None
    if use_custom_growth == 'y':
        short_term_growth = validate_positive_number(
            input("Short-term FCFF Growth Rate (%) [e.g., 8.0]: ").strip(),
            "Short-term Growth Rate"
        )
    
    return {
        'ticker': ticker,
        'risk_free_rate': risk_free_rate / 100,
        'equity_risk_premium': equity_risk_premium / 100,
        'forecast_years': forecast_years,
        'perpetual_growth': perpetual_growth / 100,
        'short_term_growth': short_term_growth / 100 if short_term_growth else None
    }


def fetch_company_data(ticker: str) -> Optional[Dict]:
    """Fetch company financial data from yfinance."""
    print(f"\nFetching data for {ticker}...")
    
    try:
        ticker_obj = yf.Ticker(ticker)
        
        # Fetch info
        info = ticker_obj.info
        beta = info.get('beta', None)
        market_cap = info.get('marketCap', None)
        shares_outstanding = info.get('sharesOutstanding', None)
        current_price = info.get('currentPrice', None)
        company_name = info.get('longName', ticker)
        
        # Fetch financials
        financials = ticker_obj.financials
        if financials is None or financials.empty:
            print(f"Error: Could not fetch financials for {ticker}")
            return None
        
        most_recent_fiscal = financials.columns[0]
        
        ebit = financials.loc['Operating Income', most_recent_fiscal] if 'Operating Income' in financials.index else None
        tax_expense = financials.loc['Tax Provision', most_recent_fiscal] if 'Tax Provision' in financials.index else None
        depreciation = financials.loc['Depreciation And Amortization', most_recent_fiscal] if 'Depreciation And Amortization' in financials.index else None
        interest_expense = financials.loc['Interest Expense', most_recent_fiscal] if 'Interest Expense' in financials.index else None
        
        # Fetch balance sheet
        balance_sheet = ticker_obj.balance_sheet
        if balance_sheet is None or balance_sheet.empty:
            print(f"Error: Could not fetch balance sheet for {ticker}")
            return None
        
        most_recent_balance = balance_sheet.columns[0]
        
        long_term_debt = balance_sheet.loc['Long Term Debt', most_recent_balance] if 'Long Term Debt' in balance_sheet.index else 0
        short_term_debt = balance_sheet.loc['Short Term Borrowings', most_recent_balance] if 'Short Term Borrowings' in balance_sheet.index else 0
        total_debt = (long_term_debt if long_term_debt else 0) + (short_term_debt if short_term_debt else 0)
        cash = balance_sheet.loc['Cash And Cash Equivalents', most_recent_balance] if 'Cash And Cash Equivalents' in balance_sheet.index else 0
        
        # Fetch cash flow
        cashflow = ticker_obj.cashflow
        if cashflow is None or cashflow.empty:
            print(f"Error: Could not fetch cash flow for {ticker}")
            return None
        
        most_recent_cf = cashflow.columns[0]
        
        capex = cashflow.loc['Capital Expenditure', most_recent_cf] if 'Capital Expenditure' in cashflow.index else 0
        capex = abs(capex) if capex else 0
        
        change_in_wc = 0  # Simplified
        
        if beta is None:
            print(f"Warning: Beta not available for {ticker}")
            beta = 1.0
        
        if market_cap is None or shares_outstanding is None:
            print(f"Error: Market cap or shares outstanding not available for {ticker}")
            return None
        
        if ebit is None:
            print(f"Error: EBIT (Operating Income) not available for {ticker}")
            return None
        
        print("Data fetched successfully!\n")
        
        return {
            'company_name': company_name,
            'beta': beta,
            'market_cap': market_cap,
            'shares_outstanding': shares_outstanding,
            'current_price': current_price,
            'ebit': ebit,
            'tax_expense': tax_expense,
            'depreciation': depreciation,
            'interest_expense': interest_expense,
            'total_debt': total_debt,
            'cash': cash,
            'capex': capex,
            'change_in_wc': change_in_wc
        }
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None


def calculate_tax_rate(ebit: float, tax_expense: Optional[float]) -> float:
    """Calculate effective tax rate."""
    if tax_expense is None or ebit <= 0:
        return 0.21
    
    tax_rate = tax_expense / ebit
    return max(0, min(tax_rate, 0.5))


def calculate_cost_of_debt(total_debt: float, interest_expense: Optional[float], tax_rate: float) -> float:
    """Calculate after-tax cost of debt."""
    if total_debt == 0:
        return 0
    
    if interest_expense is None or interest_expense == 0:
        pretax_cost = 0.04
    else:
        pretax_cost = interest_expense / total_debt
    
    after_tax_cost = pretax_cost * (1 - tax_rate)
    return after_tax_cost


def calculate_cost_of_equity(risk_free_rate: float, beta: float, equity_risk_premium: float) -> float:
    """Calculate cost of equity using CAPM."""
    cost_of_equity = risk_free_rate + (beta * equity_risk_premium)
    return cost_of_equity


def calculate_wacc(cost_of_equity: float, cost_of_debt: float, market_cap: float, total_debt: float) -> float:
    """Calculate Weighted Average Cost of Capital."""
    total_value = market_cap + total_debt
    
    if total_value == 0:
        return cost_of_equity
    
    weight_equity = market_cap / total_value
    weight_debt = total_debt / total_value
    
    wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt)
    return wacc


def calculate_fcff(ebit: float, tax_rate: float, depreciation: Optional[float], 
                   capex: float, change_in_wc: float) -> float:
    """Calculate Free Cash Flow to Firm (FCFF)."""
    nopat = ebit * (1 - tax_rate)
    depreciation = depreciation if depreciation else 0
    fcff = nopat + depreciation - capex - change_in_wc
    return fcff


def forecast_fcff(base_fcff: float, forecast_years: int, short_term_growth: Optional[float] = None) -> list:
    """Forecast FCFF for the forecast period."""
    if short_term_growth is None:
        short_term_growth = 0.05
    
    forecasted = []
    for year in range(1, forecast_years + 1):
        fcff = base_fcff * ((1 + short_term_growth) ** year)
        forecasted.append(fcff)
    
    return forecasted


def calculate_terminal_value(fcff_final: float, perpetual_growth: float, wacc: float) -> float:
    """Calculate terminal value using perpetuity growth model."""
    if wacc <= perpetual_growth:
        print("Error: WACC must be greater than perpetual growth rate")
        return 0
    
    terminal_value = (fcff_final * (1 + perpetual_growth)) / (wacc - perpetual_growth)
    return terminal_value


def calculate_enterprise_value(forecasted_fcff: list, terminal_value: float, wacc: float) -> Tuple[float, list, float]:
    """Calculate enterprise value by discounting cash flows."""
    pv_fcff_list = []
    pv_fcff_total = 0
    
    for year, fcff in enumerate(forecasted_fcff, 1):
        pv = fcff / ((1 + wacc) ** year)
        pv_fcff_list.append(pv)
        pv_fcff_total += pv
    
    pv_terminal = terminal_value / ((1 + wacc) ** len(forecasted_fcff))
    enterprise_value = pv_fcff_total + pv_terminal
    
    return enterprise_value, pv_fcff_list, pv_terminal


def calculate_equity_value(enterprise_value: float, total_debt: float, cash: float) -> float:
    """Calculate equity value from enterprise value."""
    equity_value = enterprise_value - total_debt + cash
    return equity_value


def calculate_intrinsic_value_per_share(equity_value: float, shares_outstanding: float) -> float:
    """Calculate intrinsic value per share."""
    if shares_outstanding == 0:
        return 0
    
    intrinsic_value = equity_value / shares_outstanding
    return intrinsic_value


def format_currency(value: float) -> str:
    """Format value as currency."""
    if abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:,.2f}"


def create_visualizations(ticker: str, inputs: Dict, company_data: Dict,
                         cost_of_equity: float, cost_of_debt: float, wacc: float,
                         base_fcff: float, forecasted_fcff: list, terminal_value: float,
                         enterprise_value: float, equity_value: float, intrinsic_value: float,
                         pv_fcff_list: list, pv_terminal: float):
    """Create comprehensive DCF visualizations."""
    
    fig = plt.figure(figsize=(20, 12))
    company_name = company_data.get('company_name', ticker)
    
    # 1. Sensitivity Analysis Heatmap (WACC vs Perpetual Growth)
    ax1 = plt.subplot(2, 3, 1)
    
    wacc_range = np.linspace(wacc * 0.8, wacc * 1.2, 7)
    growth_range = np.linspace(inputs['perpetual_growth'] * 0.5, 
                               min(inputs['perpetual_growth'] * 1.5, wacc * 0.9), 7)
    
    sensitivity_matrix = np.zeros((len(wacc_range), len(growth_range)))
    
    for i, w in enumerate(wacc_range):
        for j, g in enumerate(growth_range):
            if w > g:
                # Recalculate with new assumptions
                tv_sens = (forecasted_fcff[-1] * (1 + g)) / (w - g)
                pv_tv_sens = tv_sens / ((1 + w) ** len(forecasted_fcff))
                pv_fcff_sens = sum([fcff / ((1 + w) ** (idx + 1)) for idx, fcff in enumerate(forecasted_fcff)])
                ev_sens = pv_fcff_sens + pv_tv_sens
                eq_val_sens = ev_sens - company_data['total_debt'] + company_data['cash']
                sensitivity_matrix[i, j] = eq_val_sens / company_data['shares_outstanding']
            else:
                sensitivity_matrix[i, j] = np.nan
    
    sns.heatmap(sensitivity_matrix, 
                xticklabels=[f"{g*100:.1f}%" for g in growth_range],
                yticklabels=[f"{w*100:.1f}%" for w in wacc_range],
                annot=True, fmt='.1f', cmap='RdYlGn', ax=ax1, cbar_kws={'label': 'Share Price ($)'})
    ax1.set_title('Sensitivity Analysis: Intrinsic Value\nWACC vs Perpetual Growth Rate', fontweight='bold')
    ax1.set_xlabel('Perpetual Growth Rate', fontweight='bold')
    ax1.set_ylabel('WACC', fontweight='bold')
    
    # Mark current assumptions
    current_wacc_idx = np.argmin(np.abs(wacc_range - wacc))
    current_growth_idx = np.argmin(np.abs(growth_range - inputs['perpetual_growth']))
    ax1.add_patch(Rectangle((current_growth_idx, current_wacc_idx), 1, 1, 
                            fill=False, edgecolor='blue', lw=3))
    
    # 2. Waterfall Chart: EV to Equity Value Bridge
    ax2 = plt.subplot(2, 3, 2)
    
    categories = ['Enterprise\nValue', 'Less: Debt', 'Plus: Cash', 'Equity\nValue']
    values = [enterprise_value, -company_data['total_debt'], company_data['cash'], equity_value]
    
    cumulative = [enterprise_value]
    cumulative.append(cumulative[-1] - company_data['total_debt'])
    cumulative.append(cumulative[-1] + company_data['cash'])
    
    colors = ['#2E86AB', '#A23B72', '#06A77D', '#F18F01']
    
    # Plot bars
    ax2.bar(0, enterprise_value, color=colors[0], alpha=0.8, edgecolor='black')
    ax2.bar(1, -company_data['total_debt'], bottom=cumulative[0], color=colors[1], alpha=0.8, edgecolor='black')
    ax2.bar(2, company_data['cash'], bottom=cumulative[1], color=colors[2], alpha=0.8, edgecolor='black')
    ax2.bar(3, equity_value, color=colors[3], alpha=0.8, edgecolor='black')
    
    for i in range(len(cumulative) - 1):
        ax2.plot([i + 0.4, i + 0.6], [cumulative[i], cumulative[i]], 
                'k--', linewidth=1, alpha=0.5)
    
    ax2.text(0, enterprise_value/2, format_currency(enterprise_value), 
            ha='center', va='center', fontweight='bold', fontsize=9)
    ax2.text(1, cumulative[0] - company_data['total_debt']/2, format_currency(-company_data['total_debt']), 
            ha='center', va='center', fontweight='bold', fontsize=9)
    ax2.text(2, cumulative[1] + company_data['cash']/2, format_currency(company_data['cash']), 
            ha='center', va='center', fontweight='bold', fontsize=9)
    ax2.text(3, equity_value/2, format_currency(equity_value), 
            ha='center', va='center', fontweight='bold', fontsize=9)
    
    ax2.set_xticks(range(len(categories)))
    ax2.set_xticklabels(categories, fontweight='bold')
    ax2.set_ylabel('Value ($)', fontweight='bold')
    ax2.set_title('Waterfall Chart: Enterprise to Equity Value', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. DCF Components Breakdown
    ax3 = plt.subplot(2, 3, 3)
    
    years = [f"Year {i+1}" for i in range(len(pv_fcff_list))] + ['Terminal\nValue']
    pv_values = pv_fcff_list + [pv_terminal]
    
    bars = ax3.bar(years, pv_values, color=['#4A90E2' for _ in pv_fcff_list] + ['#E24A4A'], 
                   alpha=0.8, edgecolor='black')
    
    for bar, val in zip(bars, pv_values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{format_currency(val)}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    ax3.set_ylabel('Present Value ($)', fontweight='bold')
    ax3.set_title('DCF Components: PV of Cash Flows', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 4. Price Comparison
    ax4 = plt.subplot(2, 3, 4)
    
    if company_data['current_price']:
        prices = [company_data['current_price'], intrinsic_value]
        labels = ['Current\nMarket Price', 'DCF Intrinsic\nValue']
        colors_price = ['#FF6B6B' if intrinsic_value > company_data['current_price'] else '#4ECDC4',
                       '#4ECDC4' if intrinsic_value > company_data['current_price'] else '#FF6B6B']
        
        bars = ax4.bar(labels, prices, color=colors_price, alpha=0.8, edgecolor='black', width=0.6)
        
        for bar, price in zip(bars, prices):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'${price:.2f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        upside = ((intrinsic_value - company_data['current_price']) / company_data['current_price']) * 100
        ax4.text(0.5, max(prices) * 0.5, f"Upside: {upside:+.1f}%", 
                ha='center', fontsize=14, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax4.set_ylabel('Price per Share ($)', fontweight='bold')
        ax4.set_title('Stock Price Comparison', fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
    
    # 5. WACC Breakdown
    ax5 = plt.subplot(2, 3, 5)
    
    total_value = company_data['market_cap'] + company_data['total_debt']
    weight_equity = company_data['market_cap'] / total_value
    weight_debt = company_data['total_debt'] / total_value
    
    wacc_components = [weight_equity * cost_of_equity, weight_debt * cost_of_debt]
    labels_wacc = [f'Cost of Equity\n({weight_equity*100:.1f}% weight)', 
                   f'Cost of Debt\n({weight_debt*100:.1f}% weight)']
    colors_wacc = ['#3498DB', '#E74C3C']
    
    wedges, texts, autotexts = ax5.pie(wacc_components, labels=labels_wacc, autopct='%1.2f%%',
                                        colors=colors_wacc, startangle=90, textprops={'fontweight': 'bold'})
    
    ax5.set_title(f'WACC Breakdown\nTotal WACC: {wacc*100:.2f}%', fontweight='bold')
    
    # 6. Cash Flow Forecast
    ax6 = plt.subplot(2, 3, 6)
    
    years_fcff = list(range(1, len(forecasted_fcff) + 1))
    ax6.plot(years_fcff, forecasted_fcff, marker='o', linewidth=2, markersize=8, 
            color='#2ECC71', label='Forecasted FCFF')
    ax6.axhline(y=base_fcff, color='#E67E22', linestyle='--', linewidth=2, label='Base Year FCFF')
    
    for x, y in zip(years_fcff, forecasted_fcff):
        ax6.text(x, y, format_currency(y), ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    ax6.set_xlabel('Forecast Year', fontweight='bold')
    ax6.set_ylabel('FCFF ($)', fontweight='bold')
    ax6.set_title('Free Cash Flow Forecast', fontweight='bold')
    ax6.legend(loc='best')
    ax6.grid(True, alpha=0.3)
    
    plt.suptitle(f'DCF Valuation Analysis: {company_name} ({ticker})', 
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    filename = f'{ticker}_DCF_Analysis.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualizations saved as: {filename}")
    
    plt.show()


def print_summary(ticker: str, inputs: Dict, company_data: Dict, 
                  cost_of_equity: float, cost_of_debt: float, wacc: float,
                  base_fcff: float, forecasted_fcff: list, terminal_value: float,
                  enterprise_value: float, equity_value: float, intrinsic_value: float,
                  tax_rate: float):
    """Print comprehensive DCF analysis summary."""
    print("\n" + "="*60)
    print("DCF VALUATION SUMMARY")
    print("="*60)
    
    print(f"\n--- Ticker: {ticker} ({company_data.get('company_name', 'N/A')}) ---")
    print(f"Current Stock Price: ${company_data['current_price']:.2f}" if company_data['current_price'] else "N/A")
    
    print(f"\n--- Input Parameters ---")
    print(f"Risk-Free Rate: {inputs['risk_free_rate']*100:.2f}%")
    print(f"Equity Risk Premium: {inputs['equity_risk_premium']*100:.2f}%")
    print(f"Forecast Period: {inputs['forecast_years']} years")
    print(f"Perpetual Growth Rate: {inputs['perpetual_growth']*100:.2f}%")
    
    print(f"\n--- Company Metrics ---")
    print(f"Beta: {company_data['beta']:.2f}")
    print(f"Market Cap: {format_currency(company_data['market_cap'])}")
    print(f"Total Debt: {format_currency(company_data['total_debt'])}")
    print(f"Cash: {format_currency(company_data['cash'])}")
    print(f"Tax Rate: {tax_rate*100:.2f}%")
    
    print(f"\n--- WACC Calculation ---")
    print(f"Cost of Equity (CAPM): {cost_of_equity*100:.2f}%")
    print(f"Cost of Debt (after-tax): {cost_of_debt*100:.2f}%")
    print(f"WACC: {wacc*100:.2f}%")
    
    print(f"\n--- Free Cash Flow Analysis ---")
    print(f"EBIT: {format_currency(company_data['ebit'])}")
    print(f"Base Year FCFF: {format_currency(base_fcff)}")
    print(f"Forecasted FCFF (Year 1-{inputs['forecast_years']}):")
    for i, fcff in enumerate(forecasted_fcff, 1):
        print(f"  Year {i}: {format_currency(fcff)}")
    
    print(f"\n--- Valuation ---")
    print(f"Terminal Value: {format_currency(terminal_value)}")
    print(f"Enterprise Value: {format_currency(enterprise_value)}")
    print(f"Less: Total Debt: {format_currency(company_data['total_debt'])}")
    print(f"Plus: Cash: {format_currency(company_data['cash'])}")
    print(f"Equity Value: {format_currency(equity_value)}")
    print(f"\nShares Outstanding: {company_data['shares_outstanding']:,.0f}")
    print(f"\n*** INTRINSIC VALUE PER SHARE: ${intrinsic_value:.2f} ***")
    
    if company_data['current_price']:
        upside_downside = ((intrinsic_value - company_data['current_price']) / company_data['current_price']) * 100
        print(f"\nCurrent Price: ${company_data['current_price']:.2f}")
        print(f"Upside/Downside: {upside_downside:+.2f}%")
        
        if upside_downside > 20:
            print(f"→ Stock appears UNDERVALUED by {upside_downside:.1f}%")
        elif upside_downside < -20:
            print(f"→ Stock appears OVERVALUED by {abs(upside_downside):.1f}%")
        else:
            print(f"→ Stock appears FAIRLY VALUED")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("DISCOUNTED CASH FLOW (DCF) CALCULATOR WITH VISUALIZATIONS")
    print("="*60)
    
    # Get user inputs
    inputs = get_user_inputs()
    
    # Fetch company data
    company_data = fetch_company_data(inputs['ticker'])
    if company_data is None:
        print("Failed to retrieve company data. Exiting.")
        sys.exit(1)
    
    # Calculate tax rate
    tax_rate = calculate_tax_rate(company_data['ebit'], company_data['tax_expense'])
    
    # Calculate WACC components
    cost_of_equity = calculate_cost_of_equity(
        inputs['risk_free_rate'],
        company_data['beta'],
        inputs['equity_risk_premium']
    )
    
    cost_of_debt = calculate_cost_of_debt(
        company_data['total_debt'],
        company_data['interest_expense'],
        tax_rate
    )
    
    wacc = calculate_wacc(
        cost_of_equity,
        cost_of_debt,
        company_data['market_cap'],
        company_data['total_debt']
    )
    
    # Calculate base FCFF
    base_fcff = calculate_fcff(
        company_data['ebit'],
        tax_rate,
        company_data['depreciation'],
        company_data['capex'],
        company_data['change_in_wc']
    )
    
    # Forecast FCFF
    forecasted_fcff = forecast_fcff(
        base_fcff,
        inputs['forecast_years'],
        inputs['short_term_growth']
    )
    
    # Calculate terminal value
    terminal_value = calculate_terminal_value(
        forecasted_fcff[-1],
        inputs['perpetual_growth'],
        wacc
    )
    
    # Calculate enterprise value
    enterprise_value, pv_fcff_list, pv_terminal = calculate_enterprise_value(
        forecasted_fcff,
        terminal_value,
        wacc
    )
    
    # Calculate equity value
    equity_value = calculate_equity_value(
        enterprise_value,
        company_data['total_debt'],
        company_data['cash']
    )
    
    # Calculate intrinsic value per share
    intrinsic_value = calculate_intrinsic_value_per_share(
        equity_value,
        company_data['shares_outstanding']
    )
    
    # Print summary
    print_summary(
        inputs['ticker'],
        inputs,
        company_data,
        cost_of_equity,
        cost_of_debt,
        wacc,
        base_fcff,
        forecasted_fcff,
        terminal_value,
        enterprise_value,
        equity_value,
        intrinsic_value,
        tax_rate
    )
    
    # Create visualizations
    print("\nGenerating visualizations...")
    create_visualizations(
        inputs['ticker'],
        inputs,
        company_data,
        cost_of_equity,
        cost_of_debt,
        wacc,
        base_fcff,
        forecasted_fcff,
        terminal_value,
        enterprise_value,
        equity_value,
        intrinsic_value,
        pv_fcff_list,
        pv_terminal
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCalculation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
