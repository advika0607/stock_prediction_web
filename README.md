Stock Prediction Web Application
Project Overview
The Stock Prediction Web Application is a comprehensive tool designed to predict stock prices using historical data and machine learning models via a user-friendly web interface. This project integrates Python backend processing for data retrieval, preprocessing, and prediction with a dynamic frontend for real-time stock visualization.

Features
Fetches and preprocesses historical stock data automatically.

Predicts future stock prices using a robust machine learning model.

Interactive web dashboard for visualizing stock trends and predictions.

User-friendly interface to input stock ticker symbols and view results.

Modular architecture separating backend logic and frontend display for easy maintenance.

Installation
Prerequisites
Python 3.7 or later

Git

Installation Steps
Clone the repository:
git clone https://github.com/advika0607/stock_prediction_web.git
cd stock_prediction_web

Set up and activate a Python virtual environment:
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate


Install the required Python packages:
pip install -r requirements.txt


Usage
Start the Flask backend server:
python app.py


Open a web browser and navigate to:
http://localhost:5000

Use the web interface to enter stock ticker symbols and view stock price trends and machine learning predictions on the dashboard.

Project Structure:

Component        |  Purpose                                                        
-----------------+-----------------------------------------------------------------
app.py           |  Main Flask application, runs the web server.                   
predictor.py     |  Contains the machine learning model and prediction logic.      
data_fetcher.py  |  Handles fetching historical stock data from APIs.              
preprocessor.py  |  Cleans and preprocesses raw stock data.                        
config.py        |  Stores configuration information, such as API keys.            
templates/       |  HTML files for the web pages (index.html, etc.)                
static/          |  Frontend assets: CSS (style.css), JavaScript (main.js), images.
watchlist.html   |  Web page to manage user stock watchlists.    


Contact
For questions or feedback, please reach out at advika0607@github.com.

