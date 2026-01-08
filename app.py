from flask import Flask, render_template, request, redirect, url_for, send_file
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from datetime import datetime
import pandas as pd
import os

# Create tables
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- ROUTES --------------------

# Home page: List expenses
@app.route('/')
def index():
    db = next(get_db())
    expenses = db.query(models.Expense).filter(models.Expense.deleted_date == None).order_by(models.Expense.created_date.desc()).all()
    return render_template('index.html', expenses=expenses)

# Add expense
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        db = next(get_db())
        new_expense = models.Expense(
            category=request.form['category'],
            amount=float(request.form['amount']),
            description=request.form.get('description'),
            payment_mode=request.form.get('payment_mode'),
            merchant_name=request.form.get('merchant_name'),
            location=request.form.get('location'),
            notes=request.form.get('notes'),
            created_by="Admin"
        )
        db.add(new_expense)
        db.commit()
        return redirect(url_for('index'))
    return render_template('add_expense.html')

# Edit expense
@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    db = next(get_db())
    expense = db.query(models.Expense).filter(models.Expense.expense_id == expense_id).first()
    if request.method == 'POST':
        expense.category = request.form['category']
        expense.amount = float(request.form['amount'])
        expense.description = request.form.get('description')
        expense.payment_mode = request.form.get('payment_mode')
        expense.merchant_name = request.form.get('merchant_name')
        expense.location = request.form.get('location')
        expense.notes = request.form.get('notes')
        expense.updated_date = datetime.now()
        db.commit()
        return redirect(url_for('index'))
    return render_template('edit_expense.html', expense=expense)

# Delete expense (soft delete)
@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    db = next(get_db())
    expense = db.query(models.Expense).filter(models.Expense.expense_id == expense_id).first()
    if expense:
        expense.deleted_date = datetime.now()
        db.commit()
    return redirect(url_for('index'))

# Export to Excel
@app.route('/export')
def export_expenses():
    db = next(get_db())
    expenses = db.query(models.Expense).filter(models.Expense.deleted_date == None).all()
    data = [{
        "Expense ID": e.expense_id,
        "Category": e.category,
        "Amount": e.amount,
        "Description": e.description,
        "Payment Mode": e.payment_mode,
        "Merchant": e.merchant_name,
        "Location": e.location,
        "Notes": e.notes,
        "Created By": e.created_by,
        "Created Date": e.created_date,
        "Updated Date": e.updated_date
    } for e in expenses]

    df = pd.DataFrame(data)
    os.makedirs("reports", exist_ok=True)
    file_path = "reports/expenses.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)
@app.route('/summary')
def summary():
    db = next(get_db())
    # Total by category
    category_summary = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label("total_amount")
    ).filter(models.Expense.deleted_date == None)\
     .group_by(models.Expense.category).all()
    
    # Total overall
    total_expense = db.query(func.sum(models.Expense.amount)).filter(models.Expense.deleted_date == None).scalar() or 0
    
    return render_template('summary.html',
                           total_expense=total_expense,
                           category_summary=category_summary)


if __name__ == '__main__':
    app.run(debug=True)
