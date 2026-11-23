import mysql.connector
from mysql.connector import Error
from tabulate import tabulate
from datetime import datetime
import sys
import math
import re
from pathlib import Path
from db_config import DB_CONFIG

DEPT_PREFIX = {
    'Finance': '1',
    'IT': '2',
    'Marketing': '3',
    'Sales': '4',
    'HR': '5'
}

def sql_str(v):
    return "'" + str(v).replace("\\", "\\\\").replace("'", "''") + "'"

EMPLOYEE_SELECT = """
    SELECT
        id, first_name, last_name, email, phone, department,
        position,
        CONCAT('$', FORMAT(salary, 2)) as salary,
        DATE_FORMAT(hire_date, '%Y-%m-%d') as hire_date
    FROM employees
"""

EMPLOYEE_HEADERS = [
    "ID", "First Name", "Last Name", "Email", "Phone",
    "Department", "Position", "Salary", "Hire Date"
]

def print_employees(rows):
    print(tabulate(
        rows,
        headers=EMPLOYEE_HEADERS,
        tablefmt="grid",
        colalign=(
            "center", "left", "left", "left", "center",
            "left", "left", "right", "center"
        ),
        numalign="center"
    ))

class EmployeeManagement:
    def __init__(self):
        self.connection = None
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            print("Connected to database successfully!")
        except Error as e:
            print(f"Error connecting to database: {e}")
            sys.exit(1)

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def fetch_employee(self, emp_id):
        query = EMPLOYEE_SELECT + " WHERE id = %s"
        return self.execute_query(query, (emp_id,))

    def add_employee(self):
        try:
            print("\n=== Add New Employee ===")
            
            # Get department first to determine ID prefix
            print("\nAvailable Departments:")
            departments = [(dept,) for dept in sorted(DEPT_PREFIX)]
            for i, dept in enumerate(departments, 1):
                print(f"{i}. {dept[0]}")
            
            while True:
                try:
                    dept_choice = int(input("\nSelect department number: "))
                    if 1 <= dept_choice <= len(departments):
                        department = departments[dept_choice-1][0]
                        break
                    else:
                        print("Invalid department number. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Get the next available ID for the selected department
            dept_prefix = DEPT_PREFIX.get(department)
            if dept_prefix is None:
                print("Invalid department selected.")
                return
            
            # Get the highest ID for this department
            id_query = f"""
                SELECT MAX(CAST(SUBSTRING(id, 2) AS UNSIGNED))
                FROM employees
                WHERE id LIKE '{dept_prefix}%'
            """
            rows = self.execute_query(id_query)
            if rows is None:
                print("Could not determine the next ID.")
                return
            max_id = rows[0][0]
            if max_id and max_id >= 99:
                print("Department ID range is full.")
                return
            new_id = f"{dept_prefix}{str(max_id + 1).zfill(2)}" if max_id else f"{dept_prefix}01"
            
            # Get employee details
            first_name = input("Enter first name: ").strip()
            last_name = input("Enter last name: ").strip()
            position = input("Enter position: ").strip()
            
            if not (first_name and last_name and position):
                print("All fields are required.")
                return
            
            # Generate email
            first_clean = re.sub(r"[^a-z0-9]", "", first_name.lower())
            last_clean = re.sub(r"[^a-z0-9]", "", last_name.lower())
            if not (first_clean and last_clean):
                print("Names must contain at least one letter A-Z or digit.")
                return
            email = f"{first_clean[0]}.{last_clean}@company.com"
            
            # Generate phone number
            phone = f"555-555-{new_id}"
            
            # Get salary
            while True:
                try:
                    salary = float(input("Enter salary: $"))
                    if 0 < salary < 100_000_000 and math.isfinite(salary):
                        break
                    else:
                        print("Salary must be greater than 0 and less than $100,000,000.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Get hire date
            while True:
                hire_date = input("Enter hire date (YYYY-MM-DD): ")
                try:
                    datetime.strptime(hire_date, '%Y-%m-%d')
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
            
            # Insert the new employee
            query = """
                INSERT INTO employees 
                (id, first_name, last_name, email, phone, department, position, salary, hire_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            if self.execute_query(query, (
                new_id, first_name, last_name, email, phone,
                department, position, salary, hire_date
            )):
                print(f"\nEmployee added successfully!")
                print(f"Generated ID: {new_id}")
                print(f"Generated Email: {email}")
                print(f"Generated Phone: {phone}")
            
        except Error as e:
            print(f"Error adding employee: {e}")

    def view_all_employees(self):
        try:
            # Get all departments
            dept_query = """
                SELECT DISTINCT department 
                FROM employees 
                ORDER BY department
            """
            departments = self.execute_query(dept_query)
            
            if departments:
                print("\n" + "="*120)
                print("EMPLOYEE MANAGEMENT SYSTEM - DEPARTMENT WISE EMPLOYEE LIST".center(120))
                print("="*120)
                
                total_employees = 0
                
                # For each department, get and display its employees
                for dept in departments:
                    department = dept[0]
                    query = """
                        SELECT 
                            id,
                            first_name,
                            last_name,
                            email,
                            phone,
                            position,
                            CONCAT('$', FORMAT(salary, 2)) as salary,
                            DATE_FORMAT(hire_date, '%Y-%m-%d') as hire_date
                        FROM employees 
                        WHERE department = %s
                        ORDER BY CAST(id AS UNSIGNED)
                    """
                    results = self.execute_query(query, (department,))
                    
                    if results:
                        print(f"\n{'='*120}")
                        print(f"{department.upper()} DEPARTMENT".center(120))
                        print(f"{'='*120}")
                        
                        headers = [
                            "ID", "First Name", "Last Name", "Email", "Phone",
                            "Position", "Salary", "Hire Date"
                        ]
                        
                        print(tabulate(
                            results,
                            headers=headers,
                            tablefmt="grid",
                            colalign=(
                                "center",  # ID
                                "left",    # First Name
                                "left",    # Last Name
                                "left",    # Email
                                "center",  # Phone
                                "left",    # Position
                                "right",   # Salary
                                "center"   # Hire Date
                            ),
                            numalign="center"
                        ))
                        
                        # Print department summary
                        print(f"\nTotal {department} Employees: {len(results)}")
                        total_employees += len(results)
                
                # Print overall summary
                print("\n" + "="*120)
                print("DEPARTMENT SUMMARY".center(120))
                print("="*120)
                
                # Get department counts
                dept_summary_query = """
                    SELECT department, COUNT(*) as count
                    FROM employees
                    GROUP BY department
                    ORDER BY department
                """
                dept_summary = self.execute_query(dept_summary_query)
                
                if dept_summary:
                    dept_headers = ["Department", "Employee Count"]
                    print(tabulate(
                        dept_summary,
                        headers=dept_headers,
                        tablefmt="grid",
                        colalign=("left", "center")
                    ))
                
                print(f"\nTotal Employees Across All Departments: {total_employees}")
                print("="*120)
            else:
                print("No employees found.")
        except Error as e:
            print(f"Error viewing employees: {e}")

    def search_employee(self):
        try:
            print("\n=== Search Employee ===")
            search_term = input("Enter search term (ID, name, email, or department): ").strip()
            
            query = EMPLOYEE_SELECT + """
                WHERE id LIKE %s
                OR first_name LIKE %s
                OR last_name LIKE %s
                OR email LIKE %s
                OR department LIKE %s
                OR position LIKE %s
                ORDER BY department, last_name, first_name
            """
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (
                search_pattern, search_pattern, search_pattern, search_pattern,
                search_pattern, search_pattern
            ))
            
            if results:
                print_employees(results)
                print(f"\nFound {len(results)} employee(s)")
            else:
                print("No employees found matching the search term.")
        except Error as e:
            print(f"Error searching employees: {e}")

    def update_employee(self):
        try:
            print("\n=== Update Employee ===")
            emp_id = input("Enter employee ID to update: ").strip()
            
            # First check if employee exists
            employee = self.fetch_employee(emp_id)
            
            if not employee:
                print("Employee not found!")
                return
            
            print("\nCurrent employee information:")
            print_employees(employee)
            
            print("\nEnter new information (press Enter to keep current value):")
            
            # Get current values
            current_values = {
                'first_name': employee[0][1],
                'last_name': employee[0][2],
                'email': employee[0][3],
                'phone': employee[0][4],
                'department': employee[0][5],
                'position': employee[0][6],
                'salary': float(employee[0][7].replace('$', '').replace(',', '')),
                'hire_date': employee[0][8]
            }
            
            # Get new values
            new_values = {}
            
            # First name
            first_name = input(f"First name [{current_values['first_name']}]: ").strip()
            if first_name:
                new_values['first_name'] = first_name
            
            # Last name
            last_name = input(f"Last name [{current_values['last_name']}]: ").strip()
            if last_name:
                new_values['last_name'] = last_name
            
            # Email
            email = input(f"Email [{current_values['email']}]: ").strip()
            if email:
                new_values['email'] = email
            
            # Phone
            phone = input(f"Phone [{current_values['phone']}]: ").strip()
            if phone:
                new_values['phone'] = phone
            
            # Department
            department = input(f"Department [{current_values['department']}]: ").strip()
            if department:
                if department in DEPT_PREFIX:
                    new_values['department'] = department
                else:
                    print("Invalid department. Keeping current value.")
            
            # Position
            position = input(f"Position [{current_values['position']}]: ").strip()
            if position:
                new_values['position'] = position
            
            # Salary
            salary_input = input(f"Salary [{current_values['salary']}]: ").strip()
            if salary_input:
                try:
                    salary = float(salary_input)
                    if 0 < salary < 100_000_000 and math.isfinite(salary):
                        new_values['salary'] = salary
                    else:
                        print("Salary must be greater than 0 and less than $100,000,000. Keeping current value.")
                except ValueError:
                    print("Invalid salary format. Keeping current value.")
            
            # Hire date
            hire_date_input = input(f"Hire date [{current_values['hire_date']}]: ").strip()
            if hire_date_input:
                try:
                    datetime.strptime(hire_date_input, '%Y-%m-%d')
                    new_values['hire_date'] = hire_date_input
                except ValueError:
                    print("Invalid date format. Keeping current value.")
            
            # If no changes were made
            if not new_values:
                print("\nNo changes were made.")
                return
            
            # Build the UPDATE query dynamically based on changed fields
            update_parts = []
            params = []
            for field, value in new_values.items():
                update_parts.append(f"{field} = %s")
                params.append(value)
            
            # Add the WHERE clause parameter
            params.append(emp_id)
            
            # Execute the update
            query = f"""
                UPDATE employees 
                SET {', '.join(update_parts)}
                WHERE id = %s
            """
            
            if self.execute_query(query, tuple(params)):
                print("\nEmployee updated successfully!")
                print("Updated fields:", ", ".join(new_values.keys()))
            
        except Error as e:
            print(f"Error updating employee: {e}")

    def delete_employee(self):
        try:
            print("\n=== Delete Employee ===")
            emp_id = input("Enter employee ID to delete: ").strip()
            
            # First check if employee exists
            employee = self.fetch_employee(emp_id)
            
            if not employee:
                print("Employee not found!")
                return
            
            print("\nEmployee to be deleted:")
            print_employees(employee)
            
            confirm = input("\nAre you sure you want to delete this employee? (yes/no): ").strip().lower()
            if confirm == 'yes':
                query = "DELETE FROM employees WHERE id = %s"
                if self.execute_query(query, (emp_id,)):
                    print("Employee deleted successfully!")
            else:
                print("Deletion cancelled.")
        except Error as e:
            print(f"Error deleting employee: {e}")

    def promote_employee(self):
        try:
            print("\n=== Promote Employee ===")
            emp_id = input("Enter employee ID to promote: ").strip()
            
            # First check if employee exists
            employee = self.fetch_employee(emp_id)
            
            if not employee:
                print("Employee not found!")
                return
            
            print("\nCurrent employee information:")
            print_employees(employee)
            
            print("\nEnter new position and salary:")
            new_position = input("New position: ").strip()
            if not new_position:
                print("Position cannot be empty.")
                return

            while True:
                try:
                    new_salary = float(input("New salary: $"))
                    if 0 < new_salary < 100_000_000 and math.isfinite(new_salary):
                        break
                    else:
                        print("Salary must be greater than 0 and less than $100,000,000.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Update employee
            query = """
                UPDATE employees 
                SET position = %s,
                    salary = %s
                WHERE id = %s
            """
            if self.execute_query(query, (new_position, new_salary, emp_id)):
                print("\nEmployee promoted successfully!")
                print(f"New Position: {new_position}")
                print(f"New Salary: ${new_salary:,.2f}")
        except Error as e:
            print(f"Error promoting employee: {e}")

    def export_database_state(self):
        """Export the current database state to the SQL file"""
        try:
            print("\n=== Export Database State ===")
            
            # Export to a separate backup file so the seed SQL stays intact
            filename = Path(__file__).parent / "backup_employee_management.sql"
            
            # Get all employees
            query = """
                SELECT 
                    id, first_name, last_name, email, phone,
                    department, position, salary, hire_date
                FROM employees
                ORDER BY department, id
            """
            employees = self.execute_query(query)
            if employees is None:
                print("Could not read employee data. Backup was not created.")
                return

            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                f.write("-- Employee Management System Database\n")
                f.write(f"-- Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write database creation
                f.write("-- Drop database if exists and create new one\n")
                f.write("DROP DATABASE IF EXISTS employee_management;\n")
                f.write("CREATE DATABASE employee_management;\n")
                f.write("USE employee_management;\n\n")
                
                # Write table structure
                f.write("-- Create employees table\n")
                f.write("""CREATE TABLE employees (
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
);\n\n""")
                
                # Write employee data
                if employees:
                    f.write("-- Insert employee data\n")
                    f.write("INSERT INTO employees (id, first_name, last_name, email, phone, department, position, salary, hire_date) VALUES\n")
                    
                    for i, emp in enumerate(employees):
                        values = (
                            f"({sql_str(emp[0])}, {sql_str(emp[1])}, {sql_str(emp[2])}, "
                            f"{sql_str(emp[3])}, {sql_str(emp[4])}, {sql_str(emp[5])}, "
                            f"{sql_str(emp[6])}, {emp[7]}, {sql_str(emp[8])})"
                        )
                        if i < len(employees) - 1:
                            f.write(f"{values},\n")
                        else:
                            f.write(f"{values};\n\n")
                
                # Write indexes
                f.write("-- Create indexes for better performance\n")
                f.write("CREATE INDEX idx_department ON employees(department);\n")
                f.write("CREATE INDEX idx_position ON employees(position);\n")
                f.write("CREATE INDEX idx_hire_date ON employees(hire_date);\n\n")
                
                # Write view
                f.write("-- Create a view for employee summary\n")
                f.write("""CREATE VIEW employee_summary AS
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    MIN(salary) as min_salary,
    MAX(salary) as max_salary
FROM employees
GROUP BY department;\n\n""")
            

            print(f"\nDatabase state exported successfully to: {filename}")
            print("Backup written. The seed file employee_management.sql is unchanged.")
            
        except Error as e:
            print(f"Error exporting database state: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def analyze_salaries(self):
        """Analyze salary distributions across departments and positions"""
        try:
            print("\n=== Salary Analysis ===")
            
            # 1. Overall salary statistics
            overall_query = """
                SELECT 
                    COUNT(*) as total_employees,
                    CONCAT('$', FORMAT(AVG(salary), 2)) as avg_salary,
                    CONCAT('$', FORMAT(MIN(salary), 2)) as min_salary,
                    CONCAT('$', FORMAT(MAX(salary), 2)) as max_salary,
                    CONCAT('$', FORMAT(SUM(salary), 2)) as total_salary
                FROM employees
            """
            overall = self.execute_query(overall_query)
            if not overall:
                return
            overall_stats = overall[0]
            
            print("\nOverall Salary Statistics:")
            print("=" * 50)
            print(f"Total Employees: {overall_stats[0]}")
            print(f"Average Salary: {overall_stats[1]}")
            print(f"Minimum Salary: {overall_stats[2]}")
            print(f"Maximum Salary: {overall_stats[3]}")
            print(f"Total Salary Expense: {overall_stats[4]}")
            
            # 2. Department-wise salary analysis
            dept_query = """
                SELECT 
                    department,
                    COUNT(*) as employee_count,
                    CONCAT('$', FORMAT(AVG(salary), 2)) as avg_salary,
                    CONCAT('$', FORMAT(MIN(salary), 2)) as min_salary,
                    CONCAT('$', FORMAT(MAX(salary), 2)) as max_salary,
                    CONCAT('$', FORMAT(SUM(salary), 2)) as total_salary
                FROM employees
                GROUP BY department
                ORDER BY AVG(salary) DESC
            """
            dept_stats = self.execute_query(dept_query) or []
            
            print("\nDepartment-wise Salary Analysis:")
            print("=" * 80)
            headers = ["Department", "Employees", "Avg Salary", "Min Salary", "Max Salary", "Total Salary"]
            print(tabulate(
                dept_stats,
                headers=headers,
                tablefmt="grid",
                colalign=("left", "center", "right", "right", "right", "right")
            ))
            
            # 3. Position-wise salary analysis
            position_query = """
                SELECT 
                    position,
                    COUNT(*) as employee_count,
                    CONCAT('$', FORMAT(AVG(salary), 2)) as avg_salary,
                    CONCAT('$', FORMAT(MIN(salary), 2)) as min_salary,
                    CONCAT('$', FORMAT(MAX(salary), 2)) as max_salary
                FROM employees
                GROUP BY position
                ORDER BY AVG(salary) DESC
            """
            position_stats = self.execute_query(position_query) or []
            
            print("\nPosition-wise Salary Analysis:")
            print("=" * 80)
            headers = ["Position", "Employees", "Avg Salary", "Min Salary", "Max Salary"]
            print(tabulate(
                position_stats,
                headers=headers,
                tablefmt="grid",
                colalign=("left", "center", "right", "right", "right")
            ))
            
            # 4. Salary range distribution
            range_query = """
                SELECT 
                    CASE 
                        WHEN salary < 50000 THEN 'Under $50,000'
                        WHEN salary < 75000 THEN '$50,000 - $74,999.99'
                        WHEN salary < 100000 THEN '$75,000 - $99,999.99'
                        WHEN salary < 150000 THEN '$100,000 - $149,999.99'
                        ELSE '$150,000 and over'
                    END as salary_range,
                    COUNT(*) as employee_count,
                    CONCAT('$', FORMAT(AVG(salary), 2)) as avg_salary
                FROM employees
                GROUP BY salary_range
                ORDER BY MIN(salary)
            """
            range_stats = self.execute_query(range_query) or []
            
            print("\nSalary Range Distribution:")
            print("=" * 60)
            headers = ["Salary Range", "Employees", "Average Salary"]
            print(tabulate(
                range_stats,
                headers=headers,
                tablefmt="grid",
                colalign=("left", "center", "right")
            ))
            
        except Error as e:
            print(f"Error analyzing salaries: {e}")

def main():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        emp_management = EmployeeManagement()
        
        while True:
            print("\n=== Employee Management System ===")
            print("1. ➕ Add New Employee")
            print("2. 📋 View Employee List")
            print("3. 🔍 Search Employee")
            print("4. 📝 Update Employee Details")
            print("5. 🗑️ Remove Employee")
            print("6. 🚀 Promote Employee")
            print("7. 💾 Export Database State")
            print("8. 📊 Analyze Salaries")
            print("9. ❌ Exit")
            
            choice = input("\nEnter your choice (1-9): ")
            
            if choice == '1':
                emp_management.add_employee()
            elif choice == '2':
                emp_management.view_all_employees()
            elif choice == '3':
                emp_management.search_employee()
            elif choice == '4':
                emp_management.update_employee()
            elif choice == '5':
                emp_management.delete_employee()
            elif choice == '6':
                emp_management.promote_employee()
            elif choice == '7':
                emp_management.export_database_state()
            elif choice == '8':
                emp_management.analyze_salaries()
            elif choice == '9':
                print("\nThank you for using Employee Management System!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if 'emp_management' in locals():
            emp_management.close_connection()

if __name__ == "__main__":
    main() 