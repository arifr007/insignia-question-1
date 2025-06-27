from flask import request
from app.models.postgres import SessionLocal, FinanceExpense
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction import FeatureHasher
from scipy import stats
from typing import Dict, List
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    def __init__(self):
        self.session = SessionLocal()
        self.scaler = StandardScaler()
        self.hasher = FeatureHasher(n_features=10, input_type="string")

    def __del__(self):
        self.session.close()

    def get_data_for_analysis(self) -> pd.DataFrame:
        try:
            query = self.session.query(
                FinanceExpense.id,
                FinanceExpense.cost_center_id,
                FinanceExpense.cost_center_name,
                FinanceExpense.functional_area,
                FinanceExpense.functional_area_name,
                FinanceExpense.company_code_currency_value,
                FinanceExpense.debit_credit_ind,
                FinanceExpense.general_ledger_fiscal_year,
                FinanceExpense.posting_period,
                FinanceExpense.general_ledger_account,
                FinanceExpense.directorate,
                FinanceExpense.level_1,
            )

            df = pd.read_sql(query.statement, query.session.bind)
            logger.info(f"Fetched {len(df)} records from the database.")

            df["amount"] = df["company_code_currency_value"] * np.where(
                df["debit_credit_ind"] == "H", -1, 1
            )
            df["month_year"] = np.where(
                df["general_ledger_fiscal_year"].notna() & df["posting_period"].notna(),
                df["general_ledger_fiscal_year"].astype(str)
                + "-"
                + df["posting_period"].astype(str).str.zfill(2),
                "",
            )
            df.fillna({"directorate": "", "level_1": ""}, inplace=True)

            df.drop(
                columns=["company_code_currency_value", "debit_credit_ind"],
                inplace=True,
            )
            logger.info(f"Data prepared for analysis with {len(df)} rows.")
            return df

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame()

    def _calculate_stats(self, df: pd.DataFrame) -> Dict:
        return {
            "mean": df["amount"].mean(),
            "median": df["amount"].median(),
            "std": df["amount"].std(),
            "count": len(df),
            "sum": df["amount"].sum(),
        }

    def detect_statistical_anomalies(
        self, df: pd.DataFrame, threshold: float = 2.5
    ) -> Dict:
        if df.empty:
            logger.warning("Statistical analysis: No data available.")
            return {"anomalies": [], "summary": "No data available"}

        median = df["amount"].median()
        mad = stats.median_abs_deviation(df["amount"], scale="normal")
        if mad == 0:
            mad = df["amount"].mad() or df["amount"].std() or 1

        logger.info(f"Statistical analysis: median={median}, mad={mad}")

        df["z_score"] = np.abs(0.6745 * (df["amount"] - median) / mad)
        anomalies = df[df["z_score"] > threshold].copy()

        logger.info(f"Found {len(anomalies)} statistical anomalies with threshold {threshold}.")

        records = []
        for _, row in anomalies.iterrows():
            records.append(
                {
                    "id": row["id"],
                    "cost_center_id": row["cost_center_id"],
                    "cost_center_name": row["cost_center_name"],
                    "amount": row["amount"],
                    "z_score": round(row["z_score"], 2),
                    "month_year": row["month_year"],
                    "directorate": row["directorate"],
                    "functional_area_name": row["functional_area_name"],
                    "deviation_type": "statistical_outlier",
                    "reason": f"Z-score of {row['z_score']:.2f} exceeds threshold {threshold}",
                }
            )

        return {
            "method": "z_score",
            "threshold": threshold,
            "anomaly_count": len(anomalies),
            "anomalies": records[:10],
            "overall_stats": self._calculate_stats(df),
        }

    def _prepare_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        features = df[["amount"]].copy()
        for col in ["cost_center_id", "functional_area", "directorate"]:
            hashed = self.hasher.transform([[val] for val in df[col].astype(str)])
            hashed_df = pd.DataFrame(
                hashed.toarray(), columns=[f"{col}_hash_{i}" for i in range(10)]
            )
            features = pd.concat(
                [features.reset_index(drop=True), hashed_df.reset_index(drop=True)],
                axis=1,
            )
        return features

    def detect_ml_anomalies(
        self, df: pd.DataFrame, contamination: float = 0.05
    ) -> Dict:
        if df.empty or len(df) < 20:
            logger.warning(f"ML analysis: Insufficient data for ML (rows: {len(df)}).")
            return {"anomalies": [], "summary": "Insufficient data for ML"}

        try:
            X = self._prepare_ml_features(df)
            logger.info(f"ML analysis: Feature matrix shape: {X.shape}")
            model = IsolationForest(contamination=contamination, random_state=42)
            df["is_anomaly"] = model.fit_predict(X) == -1
            anomalies = df[df["is_anomaly"]].copy()

            logger.info(f"Found {len(anomalies)} ML anomalies with contamination {contamination}.")

            records = []
            for _, row in anomalies.iterrows():
                reason = "Unusual pattern"
                if row["amount"] > 50000:
                    reason += " - high expense"
                elif row["amount"] < -10000:
                    reason += " - large refund"
                records.append(
                    {
                        "id": row["id"],
                        "cost_center_id": row["cost_center_id"],
                        "cost_center_name": row["cost_center_name"],
                        "amount": row["amount"],
                        "month_year": row["month_year"],
                        "directorate": row["directorate"],
                        "functional_area_name": row["functional_area_name"],
                        "deviation_type": "ml_isolation_forest",
                        "reason": reason,
                    }
                )

            return {
                "method": "isolation_forest",
                "contamination": contamination,
                "anomaly_count": len(anomalies),
                "anomalies": records[:10],
                "overall_stats": self._calculate_stats(df),
            }

        except Exception as e:
            logger.error(f"ML anomaly detection failed: {str(e)}")
            return {"anomalies": [], "summary": f"ML error: {str(e)}"}

    def detect_trend_anomalies(
        self, df: pd.DataFrame, threshold_pct: float = 30.0
    ) -> Dict:
        if df.empty:
            logger.warning("Trend analysis: No data available.")
            return {"anomalies": [], "summary": "No data"}

        valid = df[df["month_year"].str.match(r"\d{4}-\d{2}")]
        monthly = (
            valid.groupby("month_year")["amount"]
            .sum()
            .reset_index()
            .sort_values("month_year")
        )
        logger.info(f"Trend analysis: Analyzing {len(monthly)} months of data.")
        monthly["pct_change"] = monthly["amount"].pct_change() * 100
        anomalies = monthly[monthly["pct_change"].abs() > threshold_pct]

        logger.info(f"Found {len(anomalies)} trend anomalies with threshold {threshold_pct}%.");

        records = []
        for _, row in anomalies.iterrows():
            month_data = valid[valid["month_year"] == row["month_year"]]
            top_contributors = (
                month_data.groupby(
                    ["cost_center_id", "cost_center_name", "directorate"]
                )
                .agg({"amount": "sum", "functional_area_name": "first"})
                .nlargest(3, "amount")
                .reset_index()
            )
            records.append(
                {
                    "month_year": row["month_year"],
                    "total_amount": row["amount"],
                    "mom_change_percent": round(row["pct_change"], 2),
                    "deviation_type": "trend_anomaly",
                    "reason": f"MoM change of {row['pct_change']:.2f}%",
                    "top_contributors": top_contributors.to_dict("records"),
                    "affected_cost_centers": month_data["cost_center_id"].nunique(),
                }
            )

        return {
            "method": "trend_analysis",
            "threshold_percent": threshold_pct,
            "anomaly_months": len(anomalies),
            "anomalies": records,
            "monthly_summary": monthly.to_dict("records"),
            "overall_stats": self._calculate_stats(valid),
        }

    def comprehensive_analysis(self) -> Dict:
        try:
            df = self.get_data_for_analysis()
            if df.empty:
                logger.warning("Comprehensive analysis: No data returned from get_data_for_analysis.")
                return {
                    "statistical_anomalies": {"anomalies": [], "summary": "No data"},
                    "ml_anomalies": {"anomalies": [], "summary": "No data"},
                    "trend_anomalies": {"anomalies": [], "summary": "No data"},
                    "summary": {"recommendations": ["No data available"]},
                }

            stat = self.detect_statistical_anomalies(df)
            ml = self.detect_ml_anomalies(df)
            trend = self.detect_trend_anomalies(df)

            logger.info(f"Comprehensive analysis results: "
                        f"Statistical={stat['anomaly_count']}, "
                        f"ML={ml['anomaly_count']}, "
                        f"Trend={trend['anomaly_months']}")

            summary = []
            if stat["anomaly_count"] > 0:
                summary.append(f"Review {stat['anomaly_count']} statistical anomalies")
            if ml["anomaly_count"] > 0:
                summary.append(f"Investigate {ml['anomaly_count']} ML anomalies")
            if trend["anomaly_months"] > 0:
                summary.append(
                    f"Analyze {trend['anomaly_months']} months with unusual trend"
                )

            return {
                "statistical_anomalies": stat,
                "ml_anomalies": ml,
                "trend_anomalies": trend,
                "summary": {
                    "total_records": len(df),
                    "total_amount": df["amount"].sum(),
                    "recommendations": summary or ["No significant anomalies detected"],
                },
            }

        except Exception as e:
            logger.error(f"Comprehensive analysis error: {str(e)}")
            return {"error": str(e), "summary": "An error occurred during analysis"}


def get_anomaly_analysis(method: str = "comprehensive") -> Dict:
    try:
        logger.info(f"Starting anomaly analysis with method: {method}")
        detector = AnomalyDetector()

        if method == "comprehensive":
            return detector.comprehensive_analysis()

        df = detector.get_data_for_analysis()

        if method == "statistical":
            threshold = (
                float(request.args.get("threshold", 2.5))
                if "request" in globals()
                else 2.5
            )
            return detector.detect_statistical_anomalies(df, threshold)
        elif method == "ml":
            contamination = (
                float(request.args.get("contamination", 0.05))
                if "request" in globals()
                else 0.05
            )
            return detector.detect_ml_anomalies(df, contamination)
        elif method == "trend":
            threshold_pct = (
                float(request.args.get("threshold_pct", 30.0))
                if "request" in globals()
                else 30.0
            )
            return detector.detect_trend_anomalies(df, threshold_pct)
        else:
            logger.error(f"Unknown anomaly detection method: {method}")
            return {"error": f"Unknown method {method}", "summary": "Invalid method specified"}

    except Exception as e:
        logger.error(f"Anomaly detection failed for method {method}: {str(e)}")
        return {"error": str(e), "summary": f"Error in {method} analysis"}
