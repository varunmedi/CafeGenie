# CafeGenie

## Overview

CafeGenie is the backend service powering the CafeGenie platform, focused on cafe/restaurant data analytics, sales forecasting, and operations management. It is written in Python (FastAPI), connects to a PostgreSQL database, and exposes a rich REST API for managing orders, retrieving sales data, and generating forecasts using data science libraries such as Prophet and Statsmodels.

## Key Features

- **Order Management**: Create, update, and retrieve customer orders (with fields for customer info, pizza type/size, status, etc.).
- **Sales Forecasting**: Predict sales using historical data and Facebook Prophet time-series models.
- **Analytics Endpoints**: APIs for weekly sales forecasts, order summaries, and filtered order listings.
- **Database Integration**: Uses PostgreSQL for persistent storage; connection parameters are controlled via environment variables.
- **Modular API Design**: Endpoints for CRUD operations and analytics, easily extendable for new business needs.

## Main Business Endpoints

- `GET /`  
  Welcome endpoint; basic health check.

- `POST /predict/`  
  Input: `ForecastRequest` (start_date, etc.)  
  Output: Sales forecasts for a specified range.

- `POST /sales-forecast-week/`  
  Input: `OrderRequest` (order_date, etc.)  
  Output: Weekly sales forecast.

- `POST /place-order/`  
  Input: customer name, phone, pizza type/size (as form fields)  
  Output: Order confirmation.

- `POST /update-order-status/`  
  Input: order_id, status (as form fields)  
  Output: Status update result.

- `GET /get-orders/`  
  Query Parameters: status, date_from, date_to  
  Output: List of orders (with filtering by status/date range).

## Data Models

- **Order**: order_id, cust_name, phone_number, pizza_type, pizza_size, total_price, status, order_date
- **ForecastRequest/OrderRequest**: Pydantic models for request body validation

## How It Relates to the UI

- The CafeGenie-UI frontend calls these endpoints to fetch live data for dashboards, sales charts, and order management screens.
- All order placement, status updates, and analytics are handled via these REST APIs.

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database
- (Recommended) Create and activate a virtual environment

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/varunmedi/CafeGenie.git
    cd CafeGenie
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    # or manually install: fastapi, psycopg2, pydantic, prophet, statsmodels, etc.
    ```

4. Set environment variables for PostgreSQL connection:
    ```
    POSTGRES_DB=your_db
    POSTGRES_USER=your_user
    POSTGRES_PASSWORD=your_password
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    ```

5. Start the API server:
    ```bash
    uvicorn app:app --reload
    ```

## Example API Usage

- Place an order:
    ```
    POST /place-order/
    Form data: cust_name, phone_number, pizza_type, pizza_size
    ```
- Get all orders for "delivered" status this week:
    ```
    GET /get-orders/?status=delivered&date_from=2025-06-17&date_to=2025-06-24
    ```
- Predict sales:
    ```
    POST /predict/
    Body: { "start_date": "2025-07-01" }
    ```

## Extending Functionality

- Add new models to `app.py` or split logic into separate modules as the codebase grows.
- Integrate new analytics or reporting endpoints for advanced business intelligence.

## Project Structure

- `app.py`: Main FastAPI app with all endpoints and business logic
- `venv/`: Virtual environment (should be excluded from version control)
- `requirements.txt`: Python dependencies

## Contributing

Open to contributions, bug reports, and feature requests!
