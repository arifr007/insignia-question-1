from app.models.postgres import SessionLocal, FinanceExpense
import pandas as pd

def get_eda_summary():
    session = SessionLocal()
    try:
        result = session.query(FinanceExpense).all()
        
        # Create comprehensive dataframe with all available columns
        df = pd.DataFrame([{
            "id": r.id,
            "posting_period": r.posting_period,
            "ledger": r.ledger,
            "company_code": r.company_code,
            "region": r.region,
            "profit_center_id": r.profit_center_id,
            "profit_center_name": r.profit_center_name,
            "funds_center": r.funds_center,
            "cost_center_id": r.cost_center_id,
            "cost_center_name": r.cost_center_name,
            "general_ledger_account": r.general_ledger_account,
            "general_ledger_account_name": r.general_ledger_account_name,
            "fund": r.fund,
            "functional_area": r.functional_area,
            "functional_area_name": r.functional_area_name,
            "general_ledger_fiscal_year": r.general_ledger_fiscal_year,
            "account_type": r.account_type,
            "currency": r.company_code_currency_key,
            "debit_credit_ind": r.debit_credit_ind,
            "raw_amount": float(r.company_code_currency_value or 0),
            "amount": float(r.company_code_currency_value or 0) * (-1 if r.debit_credit_ind == 'H' else 1),
            "supplier": r.supplier if r.supplier else None,
            "reference": r.reference if r.reference else None,
            "document_header_text": r.document_header_text if r.document_header_text else None,
            "po_description": r.po_description if r.po_description else None,
            "transaction": r.transaction if r.transaction else None,
            "level_1": r.level_1 if r.level_1 else None,
            "level_7": r.level_7 if r.level_7 else None,
            "directorate": r.directorate if r.directorate else None,
            "entity": r.entity if r.entity else None,
            "remapping_directorate": r.remapping_directorate if r.remapping_directorate else None,
            "status": r.status if r.status else None,
            # Derived fields for compatibility
            "month_year": f"{r.general_ledger_fiscal_year}-{r.posting_period:02d}" if r.general_ledger_fiscal_year and r.posting_period else None
        } for r in result])

        # Enhanced summary with all dimensions
        summary = {
            "total_rows": len(df),
            "data_quality": {
                "missing_values": df.isnull().sum().to_dict(),
                "unique_counts": df.nunique().to_dict(),
                "data_completeness": {
                    "amount_records": len(df[df['amount'] > 0]),
                    "zero_amount_records": len(df[df['amount'] == 0]),
                    "negative_amount_records": len(df[df['amount'] < 0])
                }
            },
            "financial_summary": {
                "total_amount": df['amount'].sum(),
                "average_amount": df['amount'].mean(),
                "median_amount": df['amount'].median(),
                "currency_breakdown": df['currency'].value_counts().to_dict()
            },
            "organizational_breakdown": {
                "top_directorates": df[df['directorate'].notna()].groupby("directorate")["amount"].sum().nlargest(5).to_dict(),
                "top_profit_centers": df[df['profit_center_id'].notna()].groupby("profit_center_id")["amount"].sum().nlargest(5).to_dict(),
                "top_cost_centers": df[df['cost_center_id'].notna()].groupby("cost_center_id")["amount"].sum().nlargest(5).to_dict(),
                "top_functional_areas": df[df['functional_area'].notna()].groupby("functional_area")["amount"].sum().nlargest(5).to_dict()
            },
            "general_ledger_account_analysis": {
                "top_general_ledger_accounts": df[df['general_ledger_account_name'].notna()].groupby("general_ledger_account_name")["amount"].sum().nlargest(10).to_dict(),
                "general_ledger_account_types": df[df['account_type'].notna()].groupby("account_type")["amount"].sum().to_dict()
            },
            "temporal_analysis": {
                "by_fiscal_year": df.groupby("general_ledger_fiscal_year")["amount"].sum().to_dict(),
                "recent_months": df.groupby("month_year")["amount"].sum().nlargest(6).to_dict()
            },
            "transaction_analysis": {
                "top_transaction_types": df[df['transaction'].notna()].groupby("transaction")["amount"].sum().nlargest(5).to_dict(),
                "top_level_1": df[df['level_1'].notna()].groupby("level_1")["amount"].sum().nlargest(5).to_dict(),
                "debit_credit_split": df[df['debit_credit_ind'].notna()].groupby("debit_credit_ind")["amount"].sum().to_dict()
            },
            "supplier_analysis": {
                "top_suppliers": df[df['supplier'].notna() & (df['supplier'] != '')].groupby("supplier")["amount"].sum().nlargest(10).to_dict(),
                "supplier_count": len(df[df['supplier'].notna() & (df['supplier'] != '')]['supplier'].unique())
            },
            "geographic_analysis": {
                "top_regions": df[df['region'].notna()].groupby("region")["amount"].sum().nlargest(5).to_dict(),
                "top_entities": df[df['entity'].notna()].groupby("entity")["amount"].sum().nlargest(5).to_dict()
            }
        }
        
        return summary
    
    finally:
        session.close()

def get_detailed_breakdown(dimension, top_n=10):
    """Get detailed breakdown by specific dimension"""
    session = SessionLocal()
    try:
        result = session.query(FinanceExpense).all()
        
        df = pd.DataFrame([{
            "id": r.id,
            "amount": float(r.company_code_currency_value or 0) * (-1 if r.debit_credit_ind == 'H' else 1),
            "dimension_value": getattr(r, dimension, 'Unknown'),
            "cost_center_id": r.cost_center_id,
            "directorate": r.directorate or "",
            "month_year": f"{r.general_ledger_fiscal_year}-{r.posting_period:02d}" if r.general_ledger_fiscal_year and r.posting_period else ""
        } for r in result])
        
        breakdown = df.groupby("dimension_value").agg({
            "amount": ["sum", "count", "mean", "std"],
            "cost_center_id": "nunique",
            "directorate": "nunique"
        }).round(2)
        
        return {
            "dimension": dimension,
            "breakdown": breakdown.nlargest(top_n, ("amount", "sum")).to_dict(),
            "summary_stats": {
                "total_categories": len(breakdown),
                "total_amount": df['amount'].sum(),
                "showing_top": min(top_n, len(breakdown))
            }
        }
    
    finally:
        session.close()

def get_time_series_analysis(group_by="month_year"):
    """Get time series analysis"""
    session = SessionLocal()
    try:
        result = session.query(FinanceExpense).all()
        
        df = pd.DataFrame([{
            "amount": float(r.company_code_currency_value or 0) * (-1 if r.debit_credit_ind == 'H' else 1),
            "month_year": f"{r.general_ledger_fiscal_year}-{r.posting_period:02d}" if r.general_ledger_fiscal_year and r.posting_period else "",
            "fiscal_year": r.general_ledger_fiscal_year,
            "posting_period": r.posting_period,
            "directorate": r.directorate or ""
        } for r in result])
        
        # Time series by specified grouping
        if group_by == "month_year":
            # Sort by fiscal year and posting period to ensure correct chronological order
            df['sort_key'] = pd.to_datetime(df['month_year'], format='%Y-%m')
            df = df.sort_values('sort_key')
            time_series = df.groupby("month_year")["amount"].agg(["sum", "count", "mean"]).reset_index()
        elif group_by == "fiscal_year":
            time_series = df.groupby("fiscal_year")["amount"].agg(["sum", "count", "mean"]).reset_index()
            time_series = time_series.sort_values('fiscal_year')
        else:
            time_series = df.groupby("posting_period")["amount"].agg(["sum", "count", "mean"]).reset_index()
            time_series = time_series.sort_values('posting_period')
        
        # Calculate growth rates
        previous_amounts = time_series['sum'].shift(1)
        current_amounts = time_series['sum']
        time_series['growth_rate'] = ((current_amounts - previous_amounts) / previous_amounts.abs()) * 100
        
        return {
            "time_series": time_series.to_dict('records'),
            "summary": {
                "total_periods": len(time_series),
                "avg_growth_rate": time_series['growth_rate'].mean(),
                "max_amount_period": time_series.loc[time_series['sum'].idxmax()].to_dict(),
                "min_amount_period": time_series.loc[time_series['sum'].idxmin()].to_dict()
            }
        }
    
    finally:
        session.close()