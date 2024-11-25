# Brickfund-Credit-Model

## Description
This project leverages Python and Streamlit to build an interactive tool that processes information from real estate developers obtained via a form and generates personalized preliminary bridge loan offers.
The system evaluates key data such as income, debts, requested amount, collateral value, and desired term to assess loan feasibility and provide a preliminary evaluation based on internal policies.

## Features
+ Automatic Connection with Google Sheets: Extracts and updates data directly from a spreadsheet linked to the form.
+ Interactive Interface with Streamlit: Offers a dropdown list to select clients and presents detailed information in a pre-offer format.
+ **Automated Financial Calculations**:
  + Loan-to-Value Ratio (LTV).
  + Comparison of payment capacity against the requested loan amount.
  + Alerts for additional reviews, such as credit reports, financial statements, and collateral valuation.

+ Flexibility and Scalability: Ready to adapt to new evaluation criteria and expand with additional functionalities.


## Technologies Used

* Python: For business logic and financial calculations.
* Streamlit: For creating an interactive and user-friendly web application.
* Google Sheets API: For syncing form data with the application.


## How It Works
1. The client fills out a form with key project information.
2. The data is automatically stored in a Google spreadsheet.
3. The Streamlit application processes the data, evaluates the information, and generates a pre-offer based on predefined loan policies.
4. Alerts are displayed if the client fails to meet specific key criteria, such as the minimum collateral value or inconsistencies in payment capacity.
