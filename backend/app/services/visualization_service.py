from app.models.postgres import SessionLocal, FinanceExpense
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
import base64
from io import BytesIO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualizationService:
    def __init__(self):
        self.session = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'session'):
            try:
                self.session.close()
            except:
                pass
    
    def get_data_for_visualization(self, date_range=None):
        """Get data formatted for visualization"""
        try:
            query = self.session.query(FinanceExpense)
            result = query.all()
            
            if not result:
                return pd.DataFrame()
                
            return pd.DataFrame([{
                "cost_center_id": r.cost_center_id,
                "cost_center_name": r.cost_center_name,
                "functional_area": r.functional_area,
                "functional_area_name": r.functional_area_name,
                "amount": float(r.company_code_currency_value or 0) * (-1 if r.debit_credit_ind == 'H' else 1),
                "month_year": f"{r.general_ledger_fiscal_year}-{r.posting_period:02d}" if r.general_ledger_fiscal_year and r.posting_period else "",
                "directorate": r.directorate or "",
                "remapping_directorate": r.remapping_directorate or "",
                "general_ledger_account": r.general_ledger_account,
                "general_ledger_account_name": r.general_ledger_account_name,
                "profit_center_name": r.profit_center_name,
                "supplier": r.supplier or "",
                "transaction": r.transaction or "",
                "level_1": r.level_1 or "",
                "level_7": r.level_7 or "",
                "entity": r.entity or "",
                "debit_credit_ind": r.debit_credit_ind or ""
            } for r in result])
        except Exception as e:
            print(f"Error in get_data_for_visualization: {str(e)}")
            return pd.DataFrame()
        
        result = query.all()
        df = pd.DataFrame([{
            "cost_center_id": r.cost_center_id,
            "cost_center_name": r.cost_center_name,
            "functional_area": r.functional_area,
            "functional_area_name": r.functional_area_name,
            "amount": float(r.company_code_currency_value or 0) * (-1 if r.debit_credit_ind == 'H' else 1),
            "month_year": f"{r.general_ledger_fiscal_year}-{r.posting_period:02d}" if r.general_ledger_fiscal_year and r.posting_period else "",
            "directorate": r.directorate or "",
            "remapping_directorate": r.remapping_directorate or "",
            "general_ledger_account": r.general_ledger_account,
            "general_ledger_account_name": r.general_ledger_account_name,
            "profit_center_name": r.profit_center_name,
            "supplier": r.supplier or "",
            "transaction": r.transaction or "",
            "level_1": r.level_1 or "",
            "level_7": r.level_7 or "",
            "entity": r.entity or "",
            "debit_credit_ind": r.debit_credit_ind or ""
        } for r in result])
        
        return df
    
    def generate_trend_chart_data(self):
        """Generate data for trend visualization"""
        df = self.get_data_for_visualization()
        
        if df.empty:
            return {"error": "No data available"}
        
        # Monthly trend
        monthly_trend = df.groupby('month_year')['amount'].sum().reset_index()
        monthly_trend = monthly_trend.sort_values('month_year')
        
        # Create Plotly chart data (JSON format for frontend)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_trend['month_year'],
            y=monthly_trend['amount'],
            mode='lines+markers',
            name='Monthly Expenses',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Monthly Expense Trend',
            xaxis_title='Month',
            yaxis_title='Amount',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return {
            "chart_type": "line_chart",
            "chart_data": json.loads(fig.to_json()),
            "raw_data": monthly_trend.to_dict('records'),
            "summary": {
                "total_months": len(monthly_trend),
                "average_monthly": monthly_trend['amount'].mean(),
                "min_month": monthly_trend.loc[monthly_trend['amount'].idxmin()].to_dict(),
                "max_month": monthly_trend.loc[monthly_trend['amount'].idxmax()].to_dict()
            }
        }
    
    def generate_category_breakdown_chart(self):
        """Generate functional area breakdown pie chart data"""
        df = self.get_data_for_visualization()
        
        if df.empty:
            return {"error": "No data available"}
        
        area_totals = df.groupby('functional_area_name')['amount'].sum().reset_index()
        area_totals = area_totals.sort_values('amount', ascending=False)
        
        # Get top 10 areas and combine the rest into "Others"
        if len(area_totals) > 10:
            top_10 = area_totals.head(10).copy()
            others_total = area_totals.iloc[10:]['amount'].sum()
            others_count = len(area_totals) - 10
            
            # Add "Others" category
            others_row = pd.DataFrame({
                'functional_area_name': [f'Others ({others_count} areas)'],
                'amount': [others_total]
            })
            area_totals_display = pd.concat([top_10, others_row], ignore_index=True)
        else:
            area_totals_display = area_totals.copy()
        
        # Calculate percentages for better summary info
        total_amount = area_totals_display['amount'].sum()
        area_totals_display['percentage'] = (area_totals_display['amount'] / total_amount * 100).round(2)
        
        fig = go.Figure(data=[go.Pie(
            labels=area_totals_display['functional_area_name'],
            values=area_totals_display['amount'],
            hole=.3,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Amount: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Expense Distribution by Functional Area (Top 10)',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        
        # Prepare summary with original data for accurate totals
        largest_area = {
            "name": area_totals.iloc[0]['functional_area_name'],
            "amount": float(area_totals.iloc[0]['amount']),
            "percentage": float((area_totals.iloc[0]['amount'] / area_totals['amount'].sum() * 100))
        }
        
        smallest_displayed = {
            "name": area_totals_display.iloc[-2]['functional_area_name'] if len(area_totals_display) > 1 else area_totals_display.iloc[-1]['functional_area_name'],
            "amount": float(area_totals_display.iloc[-2]['amount'] if len(area_totals_display) > 1 else area_totals_display.iloc[-1]['amount']),
            "percentage": float(area_totals_display.iloc[-2]['percentage'] if len(area_totals_display) > 1 else area_totals_display.iloc[-1]['percentage'])
        }
        
        return {
            "chart_type": "pie_chart",
            "chart_data": json.loads(fig.to_json()),
            "raw_data": area_totals_display.to_dict('records'),
            "summary": {
                "total_functional_areas": len(area_totals),
                "displayed_areas": len(area_totals_display),
                "largest_area": largest_area,
                "smallest_area": smallest_displayed,
                "others_combined": others_count if len(area_totals) > 10 else 0,
                "others_amount": float(others_total) if len(area_totals) > 10 else 0
            }
        }
    
    def generate_cost_center_heatmap(self):
        """Generate cost center vs month heatmap data"""
        df = self.get_data_for_visualization()
        
        if df.empty:
            return {"error": "No data available"}
        
        # Create pivot table for heatmap with enhanced dimensions
        heatmap_data = df.pivot_table(
            index=['cost_center_id', 'cost_center_name'],
            columns='month_year',
            values='amount',
            aggfunc='sum',
            fill_value=0
        )
        
        # Get top 15 cost centers by total spending
        cost_center_totals = df.groupby(['cost_center_id', 'cost_center_name'])['amount'].sum()
        top_cost_centers = cost_center_totals.nlargest(15).index
        heatmap_data = heatmap_data.loc[top_cost_centers]
        
        # Create display labels combining ID and name
        display_labels = [f"{cc_id} - {cc_name}" for cc_id, cc_name in heatmap_data.index]
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=display_labels,
            colorscale='Blues',
            showscale=True,
            hovertemplate='Month: %{x}<br>Cost Center: %{y}<br>Amount: %{z:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Cost Center Spending Heatmap',
            xaxis_title='Month',
            yaxis_title='Cost Center',
            template='plotly_white'
        )
        
        # Convert the MultiIndex DataFrame to a more JSON-friendly format
        raw_data = {
            "values": heatmap_data.values.tolist(),
            "x_labels": heatmap_data.columns.tolist(),
            "y_labels": display_labels,
            "cost_centers": [{"id": cc_id, "name": cc_name} for cc_id, cc_name in heatmap_data.index]
        }
        
        # Get the highest spending cost center info
        total_spending = heatmap_data.sum(axis=1)
        max_spending_idx = total_spending.idxmax()
        
        return {
            "chart_type": "heatmap",
            "chart_data": json.loads(fig.to_json()),
            "raw_data": raw_data,
            "summary": {
                "cost_centers_shown": len(top_cost_centers),
                "months_covered": len(heatmap_data.columns),
                "highest_spending": {
                    "cost_center_id": max_spending_idx[0],
                    "cost_center_name": max_spending_idx[1],
                    "amount": float(total_spending.max())
                }
            }
        }
    
    def generate_anomaly_scatter_plot(self, anomaly_data):
        """Generate scatter plot for anomaly visualization"""
        logger.info(f"Generating anomaly scatter plot. Received anomaly_data keys: {list(anomaly_data.keys()) if isinstance(anomaly_data, dict) else 'None or not a dict'}")
        if not anomaly_data or 'anomalies' not in anomaly_data:
            logger.warning(f"No anomaly data provided or 'anomalies' key is missing. Data: {anomaly_data}")
            return {"error": "No anomaly data provided"}
        
        anomalies = anomaly_data['anomalies']
        if not anomalies:
            logger.warning("Anomaly list is empty, cannot visualize.")
            return {"error": "No anomalies to visualize"}
        
        logger.info(f"Visualizing {len(anomalies)} anomalies.")
        # Convert to DataFrame and limit size
        df_anomalies = pd.DataFrame(anomalies[:100])  # Limit to 100 anomalies max
        
        # Create scatter plot
        fig = go.Figure()
        
        # Add aggregated normal points (sample a subset to reduce size)
        df_all = self.get_data_for_visualization()
        if not df_all.empty:
            # Sample and aggregate by month to reduce data points dramatically
            monthly_normal = df_all.groupby('month_year')['amount'].agg(['mean', 'count']).reset_index()
            monthly_normal = monthly_normal.head(20)  # Limit to 20 months max
            
            fig.add_trace(go.Scatter(
                x=monthly_normal['month_year'].tolist(),
                y=monthly_normal['mean'].tolist(),
                mode='markers',
                name='Normal Expenses (Monthly Avg)',
                marker=dict(color='lightblue', size=8, opacity=0.7),
                hovertemplate='<b>%{x}</b><br>Avg Amount: $%{y:,.0f}<br>Count: %{customdata}<extra></extra>',
                customdata=monthly_normal['count'].tolist()
            ))
        
        # Add anomaly points with simplified hover info
        if not df_anomalies.empty:
            # Ensure we have proper data types and limit text length
            anomaly_x = df_anomalies['month_year'].astype(str).tolist()
            anomaly_y = pd.to_numeric(df_anomalies['amount'], errors='coerce').fillna(0).tolist()
            
            # Create enhanced hover text with reason (limit length)
            hover_texts = []
            for _, row in df_anomalies.iterrows():
                cost_center = str(row.get('cost_center_name', 'N/A'))[:30]  # Limit length
                amount = float(row.get('amount', 0))
                score = row.get('z_score', row.get('anomaly_score', 'N/A'))
                reason = str(row.get('reason', 'No reason provided'))[:150]  # Limit reason length
                
                hover_text = f"<b>Anomaly Details:</b><br>ID: {row.get('id', 'N/A')}<br>Amount: ${amount:,.0f}<br>Cost Center: {cost_center}"
                if score != 'N/A':
                    hover_text += f"<br>Score: {score:.3f}"
                hover_text += f"<br><b>Reason:</b> {reason}"
                
                hover_texts.append(hover_text)
            
            fig.add_trace(go.Scatter(
                x=anomaly_x,
                y=anomaly_y,
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=12, symbol='x'),
                text=hover_texts,
                hovertemplate='%{text}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Expense Anomalies Detection',
            xaxis_title='Month',
            yaxis_title='Amount (IDR)',
            template='plotly_white',
            hovermode='closest',
            height=500
        )
        
        return {
            "chart_type": "scatter_plot",
            "chart_data": json.loads(fig.to_json()),
            "anomaly_count": len(anomalies),
            "summary": {
                "total_anomalies": len(anomalies),
                "displayed_anomalies": len(df_anomalies),
                "detection_method": anomaly_data.get('method', 'unknown'),
                "avg_anomaly_amount": df_anomalies['amount'].mean() if not df_anomalies.empty else 0,
                "data_optimization": f"Reduced from {len(df_all) if not df_all.empty else 0} to {len(monthly_normal) if not df_all.empty else 0} normal points, showing {len(df_anomalies)} anomalies"
            }
        }
    
    def generate_rca_waterfall_chart(self, rca_data):
        """Generate waterfall chart for RCA analysis"""
        if not rca_data or 'top_cost_centers' not in rca_data:
            return {"error": "No RCA data provided"}
        
        top_cost_centers = rca_data['top_cost_centers']
        
        # Convert to list format for waterfall
        cost_centers = list(top_cost_centers.keys())
        changes = [top_cost_centers[cc].get('change', 0) for cc in cost_centers]
        
        if not changes:
            return {"error": "No change data available"}
        
        fig = go.Figure(go.Waterfall(
            name="Cost Center Impact",
            orientation="v",
            measure=["relative"] * len(changes),
            x=cost_centers,
            textposition="outside",
            text=[f"+{c:,.0f}" if c > 0 else f"{c:,.0f}" for c in changes],
            y=changes,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Root Cause Analysis - Cost Center Impact",
            xaxis_title="Cost Centers",
            yaxis_title="Change in Amount",
            template='plotly_white'
        )
        
        return {
            "chart_type": "waterfall",
            "chart_data": json.loads(fig.to_json()),
            "summary": {
                "cost_centers_analyzed": len(cost_centers),
                "largest_increase": max(changes) if changes else 0,
                "largest_decrease": min(changes) if changes else 0
            }
        }
    
    def generate_dashboard_summary(self):
        """Generate comprehensive dashboard data"""
        return {
            "trend_chart": self.generate_trend_chart_data(),
            "category_breakdown": self.generate_category_breakdown_chart(),
            "cost_center_heatmap": self.generate_cost_center_heatmap(),
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "chart_count": 3
            }
        }

def get_visualization_data(chart_type, **kwargs):
    """Main function to get visualization data"""
    viz_service = None
    try:
        viz_service = VisualizationService()
        
        if not chart_type:
            return {"error": "Chart type is required"}

        result = None
        if chart_type == "trend":
            result = viz_service.generate_trend_chart_data()
        elif chart_type == "category_breakdown":
            result = viz_service.generate_category_breakdown_chart()
        elif chart_type == "heatmap":
            result = viz_service.generate_cost_center_heatmap()
        elif chart_type == "anomaly_scatter":
            result = viz_service.generate_anomaly_scatter_plot(kwargs.get('anomaly_data'))
        elif chart_type == "rca_waterfall":
            result = viz_service.generate_rca_waterfall_chart(kwargs.get('rca_data'))
        elif chart_type == "dashboard":
            result = viz_service.generate_dashboard_summary()
        else:
            return {"error": f"Unknown chart type: {chart_type}"}

        if result and "error" in result:
            return result
            
        return result or {"error": "No data available"}
        
    except Exception as e:
        return {
            "error": f"Error generating visualization: {str(e)}",
            "chart_type": chart_type,
            "details": str(e)
        }
    finally:
        if viz_service and viz_service.session:
            viz_service.session.close()
