# soupERP

>Note on AI Usage: 

>I did not use AI to write any code for this project. All code and logic were written by me. I only used AI to learn and understand ERP concepts, business rules, financial logic, and accounting flows.

A backend project built to learn and understand how enterprise ERP systems work under the hood.

- What is soupERP?

soupERP is a backend-only ERP (Enterprise Resource Planning) system. It simulates how businesses manage their daily operations—like buying, selling, inventory tracking, manufacturing, and accounting—all in one backend setup.

Note: This is a learning project built for practice and portfolio, not a live production product.

- Project Goals

Learn Complex Backend Logic: Build real business workflows like double-entry accounting and stock movements.

Practice Modular Code: Keep different business areas (sales, HR, inventory) separate and easy to manage.

Build Good APIs: Create clean endpoints that could easily connect to a frontend in the future.

- Modules

Here are the main parts of the system:

Foundation: System, Authorization, Authentication, Organization, Configuration, Audit.

Master Data: Products, Customers, Suppliers, Warehouses, Units, Taxes.

Inventory: Stock ledger, Stock Balance, Stock Transfers, Adjustments, Reservations, Valuations.

Purchasing: Purchase Receipt, Purchase Order, Goods Receipt, Purchase Invoice, Purchase Return.

Sales: Quotation, Sales Order, Sales Delivery, Sales Invoice, Sales Return.

Accounting: Chart of accounts, Journal Entries, GL, AR, AP, Payments, Financial Reports.

HR: Employees, Attendance, Leave, Payroll.

Supporting Systems: Notifications, Background Jobs, Files, Workflow Engine, Reports, Dashboards.


- How to Run Locally

Clone the repo:

git clone https://github.com/your-username/soupERP.git
cd soupERP


Set up virtual environment:

python -m venv .venv
.venv\Scripts\activate.ps1
pip install -r requirements.txt


Run Database (via Docker):

docker-compose up -d


Run migrations & start server:

python manage.py migrate
python manage.py runserver


View API Docs:

Open http://localhost:8000/docs in your browser.
