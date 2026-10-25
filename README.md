# Restaurant Menu and Order Calculator

## Project Description
This is a beginner-friendly web application developed using Python Flask. It allows customers to enter their details, select food items, calculate their total bill, and view previous orders.

## Technologies Used
- Python
- Flask
- HTML
- CSS
- SQLite database

## Features
- Customer name and phone number form
- Restaurant menu with food prices
- Quantity selection for food items
- Automatic bill calculation
- Input validation and error handling
- Order history
- Restaurant dashboard

## Project Structure
- `app.py` – Flask application and routes
- `templates/` – HTML pages
- `static/` – CSS and food images
- `restaurant.db` – SQLite database containing saved orders
- `requirements.txt` – Required Python package

## Installation and Execution
1. Install Python.
2. Open the project folder in VS Code.
3. Open a terminal in the project folder.
4. Install the required package:

   `pip install -r requirements.txt`

5. Run the application:

   `python app.py`

6. Open the following address in your browser:

   `http://127.0.0.1:5000/`

## Testing
The application should be tested with valid customer details, different food quantities, empty fields, invalid phone numbers, and zero quantities.

## Conclusion
This project demonstrates basic Flask routing, GET and POST requests, HTML forms, input validation, database operations, and dynamic bill calculation.
