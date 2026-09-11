"""
Sales transaction routes.
"""

from flask import Blueprint, render_template, request
from routes.auth import login_required
from models import Sale

sales_bp = Blueprint("sales", __name__)

@sales_bp.route("/sales")
@login_required
def list_sales():
    status_filter = request.args.get("status", "ALL")
    query = Sale.query
    if status_filter != "ALL":
        query = query.filter_by(status=status_filter)
    sales = query.order_by(Sale.sale_date.desc()).all()
    
    total_revenue = sum(s.amount for s in sales if s.status == "COMPLETED")
    return render_template(
        "sales.html",
        sales=sales,
        selected_status=status_filter,
        total_revenue=round(total_revenue, 2)
    )
