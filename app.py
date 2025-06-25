import pickle

from fastapi import FastAPI, Form, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from typing import Optional
from decimal import Decimal
from datetime import datetime, timedelta

# ------------------------------
# Database connection function
# ------------------------------


# Load the trained model

with open('model.pkl', 'rb') as file:

    model = pickle.load(file)

load_dotenv()

def get_db():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT")
    )

# ------------------------------
# FastAPI App & CORS Setup
# ------------------------------
app = FastAPI()


origins = [

    "http://localhost:3000",  # Allow your Next.js app's origin

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request model

class ForecastRequest(BaseModel):

    start_date: str  # Expected format: YYYY-MM-DD

# ------------------------------
# Forecast Endpoint (Already Working)
# ------------------------------
class OrderRequest(BaseModel):
    order_date: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pizza Store Forecasting API!"}

@app.post("/predict/")

def predict_sales(request: ForecastRequest):
    try:

        # Convert input date to datetime object

        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        

        # Generate future dates for the next 7 days

        future_dates = [start_date + timedelta(days=i) for i in range(7)]

        

        # Prepare DataFrame for Prophet

        future_df = pd.DataFrame({'ds': future_dates})

        

        # Predict sales

        forecast = model.predict(future_df)

        

        # Aggregate total sales for the next 7 days

        total_predicted_sales = forecast['yhat'].sum()

        

        return {"total_predicted_sales": round(total_predicted_sales, 2)}



    except ValueError as e:

        # Catch any date parsing errors

        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")


    except Exception as e:

        # Catch any other unexpected errors

        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/sales-forecast-week/")

def sales_forecast_week(order: OrderRequest):
    try:

        # Determine the start of the week (Monday)

        current_date = datetime.strptime(order.order_date, "%Y-%m-%d")

        start_of_week = current_date - timedelta(days=current_date.weekday())  # Start from Monday

        end_of_week = start_of_week + timedelta(days=6)  # End on Sunday

        # Create a range of dates for the week

        week_dates = pd.date_range(start=start_of_week, end=end_of_week)
        # Prepare input data for model (Prophet needs 'ds' column)

        input_data = pd.DataFrame({'ds': week_dates})
        # Predict sales for the entire week

        forecast = model.predict(input_data)
        # Aggregate the sales for the week

        aggregated_sales = forecast['yhat'].sum()

        return {"predicted_sales": aggregated_sales}
    except ValueError as e:

        # Catch any date parsing errors

        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")

    except Exception as e:

        # Catch any other unexpected errors

        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

# ------------------------------
# ✅ ✅ ✅ Insert Order Endpoint
# ------------------------------
@app.post("/place-order/")
def place_order(
    cust_name: str = Form(...),
    phone_number: int = Form(...),
    pizza_type: str = Form(...),
    pizza_size: str = Form(...),
    db=Depends(get_db)
):
    try:
        cursor = db.cursor()

        # ----------- Calculate Total Price -----------
        pizza_types = pizza_type.split(",")
        pizza_sizes = pizza_size.split(",")

        if len(pizza_types) != len(pizza_sizes):
            raise HTTPException(status_code=400, detail="Pizza types and sizes count mismatch")

        total_price = Decimal(0)
        for p_type, p_size in zip(pizza_types, pizza_sizes):
            cursor.execute("""
                SELECT unit_price FROM pizza 
                WHERE pizza_name = %s AND pizza_size = %s
            """, (p_type.strip(), p_size.strip()))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail=f"Pizza '{p_type}' with size '{p_size}' not found")
            total_price += Decimal(result[0])

        # ----------- Insert into orders table ----------
        cursor.execute("""
            INSERT INTO orders 
            (cust_name, phone_number, pizza_type, pizza_size, total_price, order_date, order_timestamp,status)
            VALUES (%s, %s, %s, %s, %s, current_date, current_time,'in prep')
            RETURNING order_id
        """, (cust_name, phone_number, pizza_type, pizza_size, total_price))

        order_id = cursor.fetchone()[0]
        db.commit()

        return {"order_id": order_id, "total_price": total_price, "message": "Order placed successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        db.close()


@app.post("/update-order-status/")
def update_order_status(
    order_id: int = Form(...),
    status: str = Form(...),
    db=Depends(get_db)
):
    try:
        with db.cursor() as cursor:  # Using context manager for cursor
            cursor.execute(
                """
                UPDATE orders
                SET status = %s
                WHERE order_id = %s
                RETURNING order_id;  -- This will return the updated order_id
                """,
                (status, order_id)
            )
            updated_order = cursor.fetchone()

            if not updated_order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            db.commit()  # Commit the transaction to make the update permanent
        return {"message": "Order status updated successfully", "order_id": updated_order[0]}
    
    except Exception as e:
        db.rollback()  # If something goes wrong, rollback the transaction
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-orders/")
def get_orders(
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),  # format: YYYY-MM-DD
    date_to: Optional[str] = Query(None),    # format: YYYY-MM-DD
    db=Depends(get_db)
):
    cursor = db.cursor()

    # base query
    query = """
    SELECT 
        order_id as Order_Number,
        cust_name as Customer_Name,
        phone_number as Phone_Number,
        pizza_type as Pizzas,
        total_price as Total_Price,
        status as Status
    FROM orders
    WHERE 1=1
    """

    params = []

    # dynamic filters
    if status:
        query += " AND status = %s"
        params.append(status)
    if date_from:
        query += " AND order_date >= %s"
        params.append(date_from)
    if date_to:
        query += " AND order_date <= %s"
        params.append(date_to)

    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()

    return {"orders": result}
