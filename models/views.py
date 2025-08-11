from database import db

class VCashflowDaily(db.Model):
    __tablename__ = 'v_cashflow_daily'
    txn_date = db.Column(db.Date, primary_key=True)
    inflows = db.Column(db.Numeric)
    outflows = db.Column(db.Numeric)
    net_flow = db.Column(db.Numeric)
    transaction_count = db.Column(db.Integer)


class VApOpen(db.Model):
    __tablename__ = 'v_ap_open'
    id = db.Column(db.Integer, primary_key=True)
    vendor_customer = db.Column(db.String)
    amount = db.Column(db.Numeric)
    due_date = db.Column(db.Date)
    status = db.Column(db.String)
    invoice_number = db.Column(db.String)
    description = db.Column(db.Text)


class VArOpen(db.Model):
    __tablename__ = 'v_ar_open'
    id = db.Column(db.Integer, primary_key=True)
    vendor_customer = db.Column(db.String)
    amount = db.Column(db.Numeric)
    due_date = db.Column(db.Date)
    status = db.Column(db.String)
    invoice_number = db.Column(db.String)
    description = db.Column(db.Text)


class VPoSummary(db.Model):
    __tablename__ = 'v_po_summary'
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String)
    vendor = db.Column(db.String)
    total_amount = db.Column(db.Numeric)
    status = db.Column(db.String)
    order_date = db.Column(db.Date)
    expected_delivery = db.Column(db.Date)
