# Employee Management System

A command-line employee management system built with Python and MySQL. It lets you add, update, search, promote and remove employees, and analyze salary data by department, position and salary range.

## Features

### 1. Employee Management
- ➕ Add new employees with auto-generated IDs, emails, and phone numbers
- 📋 View the employee list organized by department
- 🔍 Search employees by ID, name, email, or department
- 📝 Update employee information
- 🗑️ Remove employees from the system
- 🚀 Promote employees with position and salary updates

### 2. Salary Analysis
- 📊 Salary analysis across departments
- 💰 Position-wise salary distribution
- 📈 Salary range analysis
- 📉 Department-wise salary statistics
- 💵 Overall salary metrics

### 3. Database Management
- 💾 Export the database state to an SQL file
- 🔄 One-command database setup (`python db_config.py`, asks for confirmation)
- 📑 Indexes and an employee summary view

## Prerequisites

- Python (developed and tested on 3.13)
- MySQL Server
- Required Python packages (installed from `requirements.txt`):
  - mysql-connector-python
  - tabulate
  - python-dotenv

## Installation

1. Clone the repository:
```bash
git clone https://github.com/imerla/Data-Projects.git
cd "Employee Management System"
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. As a MySQL admin, create the app user:
```sql
CREATE USER 'employee_app'@'localhost' IDENTIFIED BY 'choose_a_password';
GRANT ALL PRIVILEGES ON employee_management.* TO 'employee_app'@'localhost';
```

4. Copy `.env.example` to `.env` and set `DB_PASSWORD`.

5. Create the tables and demo data:
```bash
python db_config.py
```
Type `YES` when asked; this DROPS and recreates the `employee_management` database.

## Configuration

`.env` should contain:

```dotenv
DB_HOST=127.0.0.1
DB_USER=employee_app
DB_PASSWORD=change_me
DB_NAME=employee_management
```

Never commit your `.env` file. It is listed in `.gitignore`.

## Usage

1. Run the program:
```bash
python employee_management.py
```

2. Use the main menu to navigate:
   - 1: Add New Employee
   - 2: View Employee List
   - 3: Search Employee
   - 4: Update Employee Details
   - 5: Remove Employee
   - 6: Promote Employee
   - 7: Export Database State
   - 8: Analyze Salaries
   - 9: Exit

## Employee ID System

IDs are based on the department:
- Finance: 1xx
- IT: 2xx
- Marketing: 3xx
- Sales: 4xx
- HR: 5xx

Each department can hold up to 99 employees. Changing an employee's department does not change their ID.

## Database Structure

### Employees Table
```sql
CREATE TABLE employees (
    id VARCHAR(3) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    department VARCHAR(50) NOT NULL,
    position VARCHAR(50) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    hire_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Features in Detail

### Adding Employees
- Automatic ID generation based on department
- Email generation using first initial and last name
- Phone number generation based on employee ID
- Input validation for required fields, salary and hire date
- Names should be entered in Latin letters; emails are generated from ASCII characters

### Viewing Employees
- Department-wise organization
- Formatted tables using tabulate
- Summary statistics for each department
- Total employee count

### Salary Analysis
- Overall salary statistics
- Department-wise analysis
- Position-wise analysis
- Salary range distribution
- Minimum, maximum, and average salaries

### Database Export
- Exports the table structure, indexes, summary view and employee records to `backup_employee_management.sql` (created_at timestamps are regenerated on import)
- The seed file `employee_management.sql` is left untouched; `backup_*.sql` files are listed in `.gitignore`

## Error Handling

The system handles database connection and query errors and validates numeric, date and required fields.

## Notes

- All employee data in this project is fictional demo data.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
