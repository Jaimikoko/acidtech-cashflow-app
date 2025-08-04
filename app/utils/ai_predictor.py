from datetime import datetime, date, timedelta
from app.models.transaction import Transaction
from app import db
import json

class CashFlowPredictor:
    def __init__(self):
        self.prediction_days = 90
    
    def get_cash_flow_prediction(self):
        """Generate cash flow predictions based on historical data and pending transactions"""
        
        # Get pending transactions
        pending_receivables = Transaction.query.filter_by(type='receivable', status='pending').all()
        pending_payables = Transaction.query.filter_by(type='payable', status='pending').all()
        
        # Generate predictions for next 90 days
        predictions = []
        today = date.today()
        
        for i in range(self.prediction_days):
            prediction_date = today + timedelta(days=i)
            
            # Calculate expected cash inflow (receivables due on this date)
            inflow = sum(
                float(t.amount) for t in pending_receivables 
                if t.due_date == prediction_date
            )
            
            # Calculate expected cash outflow (payables due on this date)
            outflow = sum(
                float(t.amount) for t in pending_payables 
                if t.due_date == prediction_date
            )
            
            # Calculate net flow
            net_flow = inflow - outflow
            
            # Add some intelligence based on historical patterns
            historical_factor = self._get_historical_factor(prediction_date)
            adjusted_inflow = inflow * historical_factor
            
            predictions.append({
                'date': prediction_date.strftime('%Y-%m-%d'),
                'inflow': round(adjusted_inflow, 2),
                'outflow': round(outflow, 2),
                'net_flow': round(adjusted_inflow - outflow, 2),
                'confidence': self._calculate_confidence(inflow, outflow)
            })
        
        return predictions
    
    def _get_historical_factor(self, prediction_date):
        """Calculate adjustment factor based on historical payment patterns"""
        # Simple logic: assume 85% collection rate for receivables
        # This could be enhanced with machine learning
        return 0.85
    
    def _calculate_confidence(self, inflow, outflow):
        """Calculate confidence level for predictions"""
        # Higher confidence when there are actual transactions
        if inflow == 0 and outflow == 0:
            return 0.3  # Low confidence for days with no scheduled transactions
        elif inflow > 0 or outflow > 0:
            return 0.75  # Medium-high confidence for days with scheduled transactions
        else:
            return 0.5  # Medium confidence
    
    def get_risk_analysis(self):
        """Analyze cash flow risks"""
        today = date.today()
        thirty_days = today + timedelta(days=30)
        
        # Get overdue transactions
        overdue_receivables = Transaction.query.filter(
            Transaction.type == 'receivable',
            Transaction.status == 'pending',
            Transaction.due_date < today
        ).all()
        
        overdue_payables = Transaction.query.filter(
            Transaction.type == 'payable',
            Transaction.status == 'pending',
            Transaction.due_date < today
        ).all()
        
        # Calculate amounts
        overdue_receivables_amount = sum(float(t.amount) for t in overdue_receivables)
        overdue_payables_amount = sum(float(t.amount) for t in overdue_payables)
        
        # Upcoming receivables and payables (next 30 days)
        upcoming_receivables = Transaction.query.filter(
            Transaction.type == 'receivable',
            Transaction.status == 'pending',
            Transaction.due_date >= today,
            Transaction.due_date <= thirty_days
        ).all()
        
        upcoming_payables = Transaction.query.filter(
            Transaction.type == 'payable',
            Transaction.status == 'pending',
            Transaction.due_date >= today,
            Transaction.due_date <= thirty_days
        ).all()
        
        upcoming_receivables_amount = sum(float(t.amount) for t in upcoming_receivables)
        upcoming_payables_amount = sum(float(t.amount) for t in upcoming_payables)
        
        # Calculate risk score (0-100, higher = more risk)
        risk_score = 0
        
        # Overdue receivables increase risk
        if overdue_receivables_amount > 0:
            risk_score += min(30, overdue_receivables_amount / 1000)
        
        # Negative cash flow in next 30 days increases risk
        net_thirty_days = upcoming_receivables_amount - upcoming_payables_amount
        if net_thirty_days < 0:
            risk_score += min(40, abs(net_thirty_days) / 1000)
        
        # High ratio of payables to receivables increases risk
        if upcoming_receivables_amount > 0:
            ratio = upcoming_payables_amount / upcoming_receivables_amount
            if ratio > 1:
                risk_score += min(30, (ratio - 1) * 20)
        
        risk_score = min(100, risk_score)
        
        return {
            'risk_score': round(risk_score, 1),
            'risk_level': self._get_risk_level(risk_score),
            'overdue_receivables': {
                'count': len(overdue_receivables),
                'amount': round(overdue_receivables_amount, 2)
            },
            'overdue_payables': {
                'count': len(overdue_payables),
                'amount': round(overdue_payables_amount, 2)
            },
            'upcoming_30_days': {
                'receivables_amount': round(upcoming_receivables_amount, 2),
                'payables_amount': round(upcoming_payables_amount, 2),
                'net_flow': round(net_thirty_days, 2)
            },
            'recommendations': self._get_recommendations(risk_score, overdue_receivables, overdue_payables)
        }
    
    def _get_risk_level(self, risk_score):
        """Convert risk score to risk level"""
        if risk_score < 25:
            return 'Low'
        elif risk_score < 50:
            return 'Medium'
        elif risk_score < 75:
            return 'High'
        else:
            return 'Critical'
    
    def _get_recommendations(self, risk_score, overdue_receivables, overdue_payables):
        """Generate recommendations based on risk analysis"""
        recommendations = []
        
        if len(overdue_receivables) > 0:
            recommendations.append(f"Follow up on {len(overdue_receivables)} overdue receivables")
        
        if len(overdue_payables) > 0:
            recommendations.append(f"Pay {len(overdue_payables)} overdue bills to avoid penalties")
        
        if risk_score > 50:
            recommendations.append("Consider negotiating payment terms with customers")
            recommendations.append("Review credit policies for new customers")
        
        if risk_score > 75:
            recommendations.append("Urgent: Review cash position and consider financing options")
            recommendations.append("Prioritize collection of largest outstanding receivables")
        
        return recommendations
    
    def get_vendor_customer_insights(self):
        """Analyze vendor and customer payment patterns"""
        
        # Get top customers by revenue
        top_customers = db.session.query(
            Transaction.vendor_customer,
            db.func.sum(Transaction.amount).label('total_amount'),
            db.func.count(Transaction.id).label('transaction_count'),
            db.func.avg(Transaction.amount).label('avg_amount')
        ).filter(
            Transaction.type == 'receivable'
        ).group_by(Transaction.vendor_customer).order_by(
            db.func.sum(Transaction.amount).desc()
        ).limit(5).all()
        
        # Get top vendors by spending
        top_vendors = db.session.query(
            Transaction.vendor_customer,
            db.func.sum(Transaction.amount).label('total_amount'),
            db.func.count(Transaction.id).label('transaction_count'),
            db.func.avg(Transaction.amount).label('avg_amount')
        ).filter(
            Transaction.type == 'payable'
        ).group_by(Transaction.vendor_customer).order_by(
            db.func.sum(Transaction.amount).desc()
        ).limit(5).all()
        
        return {
            'top_customers': [
                {
                    'name': customer.vendor_customer,
                    'total_amount': round(float(customer.total_amount), 2),
                    'transaction_count': customer.transaction_count,
                    'avg_amount': round(float(customer.avg_amount), 2)
                }
                for customer in top_customers
            ],
            'top_vendors': [
                {
                    'name': vendor.vendor_customer,
                    'total_amount': round(float(vendor.total_amount), 2),
                    'transaction_count': vendor.transaction_count,
                    'avg_amount': round(float(vendor.avg_amount), 2)
                }
                for vendor in top_vendors
            ]
        }