from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from sqlalchemy import func
from datetime import datetime
from fastapi.responses import FileResponse
import os
import pandas as pd

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/expenses")
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    new_expense = models.Expense(**expense.dict())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return {"message": "Expense created successfully", "expense_id": new_expense.expense_id}

@app.get("/expenses")
def get_expenses(db: Session = Depends(get_db)):
    return db.query(models.Expense).filter(models.Expense.deleted_date == None).all()

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = db.query(models.Expense).filter(models.Expense.expense_id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for key, value in expense.dict().items():
        setattr(db_expense, key, value)
    db.commit()
    return {"message": "Expense updated successfully"}

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.expense_id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense.deleted_date = datetime.now()
    db.commit()
    return {"message": "Expense deleted successfully"}

@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    return db.query(
        models.Expense.category,
        func.sum(models.Expense.amount)
    ).filter(models.Expense.deleted_date == None)\
     .group_by(models.Expense.category).all()

@app.get("/export/excel")
def export_excel(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter(models.Expense.deleted_date == None).all()
    data = [{
        "Expense ID": e.expense_id,
        "Category": e.category,
        "Amount": float(e.amount),
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

    return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        filename="expenses.xlsx")

if __name__ == "__main__":
    app.run(debug=True)