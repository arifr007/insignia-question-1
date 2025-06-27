from app.models.postgres import SessionLocal, FinanceExpense
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')


class AdvancedRCAService:
    def __init__(self):
        self.session = SessionLocal()
        self.label_encoders = {}

    def get_available_months(self):
        result = self.session.query(
            FinanceExpense.general_ledger_fiscal_year,
            FinanceExpense.posting_period
        ).distinct().all()

        return sorted(
            f"{r[0]}-{r[1]:02d}" for r in result if r[0] and r[1]
        )

    def get_historical_data(self):
        result = self.session.query(FinanceExpense).all()
        return pd.DataFrame([{
            "cost_center_id": r.cost_center_id,
            "cost_center_name": r.cost_center_name,
            "functional_area": r.functional_area,
            "functional_area_name": r.functional_area_name,
            "amount": float(r.company_code_currency_value or 0) * (-1 if r.debit_credit_ind == 'H' else 1),
            "month_year": f"{r.general_ledger_fiscal_year}-{r.posting_period:02d}" if r.general_ledger_fiscal_year and r.posting_period else "",
            "directorate": r.directorate or "",
            "general_ledger_account": r.general_ledger_account,
            "profit_center_id": r.profit_center_id,
            "level_1": r.level_1 or "",
            "level_7": r.level_7 or "",
            "account_type": r.account_type or "",
            "supplier": r.supplier or ""
        } for r in result])

    def ml_root_cause_analysis(self, from_month, to_month):
        df = self.get_historical_data()
        if df.empty or len(df) < 20:
            return {"error": "Insufficient data for ML analysis"}

        categorical_features = [
            'cost_center_id', 'functional_area', 'directorate',
            'general_ledger_account', 'profit_center_id',
            'level_1', 'level_7', 'account_type', 'supplier'
        ]

        for feature in categorical_features:
            df[feature] = df[feature].fillna('Unknown').astype(str)
            le = LabelEncoder()
            df[feature + '_encoded'] = le.fit_transform(df[feature])
            self.label_encoders[feature] = le

        encoded_features = [f + '_encoded' for f in categorical_features]
        group_cols = ['month_year'] + encoded_features

        agg_df = df.groupby(group_cols).agg({
            'amount': 'sum'
        }).reset_index()
        agg_df.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in agg_df.columns.values]

        X = agg_df[encoded_features]
        y = agg_df['amount']

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        feature_importance = pd.DataFrame({
            'feature': [f.replace('_encoded', '') for f in X.columns],
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        comp_data = df[df['month_year'].isin([from_month, to_month])]
        comp_group = comp_data.groupby(['month_year'] + encoded_features).agg({'amount': 'sum'}).reset_index()
        comp_group['predicted'] = model.predict(comp_group[encoded_features])
        comp_group['residual'] = comp_group['amount'] - comp_group['predicted']

        return {
            "ml_method": "random_forest",
            "feature_importance": feature_importance.head(5).to_dict("records"),
            "model_performance": {"mae": mean_absolute_error(y, model.predict(X))},
            "top_residuals": comp_group.nlargest(5, 'residual').to_dict("records"),
            "key_insights": self._generate_ml_insights(feature_importance)
        }

    def _generate_ml_insights(self, feature_importance):
        if feature_importance.empty:
            return []
        insights = [
            f"Top driver: {feature_importance.iloc[0]['feature']} ({feature_importance.iloc[0]['importance']:.3f})"
        ]
        if len(feature_importance) > 1:
            insights.append(
                f"Second: {feature_importance.iloc[1]['feature']} ({feature_importance.iloc[1]['importance']:.3f})"
            )
        if feature_importance.head(3)['importance'].sum() > 0.8:
            insights.append("Few features dominate the model")
        else:
            insights.append("Multiple features contribute to changes")
        return insights

    def close_session(self):
        if self.session:
            self.session.close()


def perform_comprehensive_rca(from_month, to_month):
    rca = AdvancedRCAService()
    try:
        return rca.ml_root_cause_analysis(from_month, to_month)
    finally:
        rca.close_session()

def perform_dynamic_rca():
    rca = AdvancedRCAService()
    try:
        available_months = rca.get_available_months()
        if len(available_months) < 2:
            return {"error": "Not enough months"}

        results = []
        for i in range(len(available_months) - 1):
            from_month = available_months[i]
            to_month = available_months[i + 1]
            analysis = rca.ml_root_cause_analysis(from_month, to_month)
            analysis["period"] = f"{from_month} to {to_month}"
            results.append(analysis)

        return {
            "analysis_type": "dynamic_ml_rca",
            "results": results
        }
    finally:
        rca.close_session()
