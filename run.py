#!/usr/bin/env python3
import os
from app import create_app, db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.purchase_order import PurchaseOrder

application = create_app(os.getenv('FLASK_CONFIG') or 'default')

@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Transaction': Transaction, 'PurchaseOrder': PurchaseOrder}

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5000)