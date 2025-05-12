from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
CORS(app)

# Google Sheets Setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/nineleaps/Downloads/Capstone/frontend/credentials.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open("HR_Database_Sheets")  # Name of the Google Sheet file

# MySQL DB connection
def get_db_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='root@123',
        database='capstone1'
    )

@app.route('/')
def home():
    return render_template('index.html')

# Helper: Append to specific worksheet in the single file
def append_to_google_sheet(sheet_tab, row_data):
    try:
        worksheet = spreadsheet.worksheet(sheet_tab)
        worksheet.append_row(row_data)
    except Exception as e:
        print("Google Sheet update failed:", str(e))

# Generic DB + Sheet Insert Handler
def execute_query(query, values, success_message, sheet_tab=None, row_data=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Insert failed or no rows affected."}), 400

        if sheet_tab and row_data:
            append_to_google_sheet(sheet_tab, row_data)

        return jsonify({"message": success_message}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 1. Employees
@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.json
    full_name = f"{data['first_name']} {data['last_name']}"
    query = """
        INSERT INTO employees (
            employee_id, first_name, last_name, full_name,
            mail_id, gender, dob, employment_type,
            department_id, join_date, location_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data['employee_id'], data['first_name'], data['last_name'], full_name,
        data['mail_id'], data['gender'], data['dob'], data['employment_type'],
        data['department_id'], data['join_date'], data['location_id']
    )
    return execute_query(query, values, "Employee added successfully.", "Employees", list(values))


# 2. Departments
@app.route('/api/departments', methods=['POST'])
def add_department():
    data = request.json
    query = "INSERT INTO departments (department_id, department_name) VALUES (%s, %s)"
    values = (data['department_id'], data['department_name'])
    return execute_query(query, values, "Department added successfully.", "Departments", list(values))


# 3. Attendance
@app.route('/api/attendance', methods=['POST'])
def add_attendance():
    data = request.json
    query = """
        INSERT INTO attendance_logs (
            employee_id, date, check_in, check_out,
            working_hours, is_half_day
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        data['employee_id'], data['date'], data['check_in'],
        data['check_out'], data['working_hours'], data['is_half_day']
    )
    return execute_query(query, values, "Attendance logged successfully.", "Attendance", list(values))


# 4. Leave Records
@app.route('/api/leave-records', methods=['POST'])
def add_leave_record():
    data = request.json
    query = """
        INSERT INTO leave_records (
            employee_id, leave_type_id, start_date,
            end_date, duration, reason
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        data['employee_id'], data['leave_type_id'],
        data['start_date'], data['end_date'],
        data['duration'], data['reason']
    )
    return execute_query(query, values, "Leave record added successfully.", "Leave Records", list(values))


# 5. Leave Types
@app.route('/api/leave-types', methods=['POST'])
def add_leave_type():
    data = request.json
    query = """
        INSERT INTO leave_types (leave_type_id, leave_type, description)
        VALUES (%s, %s, %s)
    """
    values = (data['leave_type_id'], data['leave_type'], data['description'])
    return execute_query(query, values, "Leave type added successfully.", "Leave Types", list(values))


# 6. Locations
@app.route('/api/locations', methods=['POST'])
def add_location():
    data = request.json
    query = "INSERT INTO locations (location_id, location_name) VALUES (%s, %s)"
    values = (data['location_id'], data['location_name'])
    return execute_query(query, values, "Location added successfully.", "Locations", list(values))


# 7. Job Roles
@app.route('/api/job-roles', methods=['POST'])
def add_job_role():
    data = request.json
    query = """
        INSERT INTO job_roles (designation_id, designation_name)
        VALUES (%s, %s)
    """
    values = (data['designation_id'], data['designation_name'])
    return execute_query(query, values, "Job role added successfully.", "Job Roles", list(values))


# 8. Projects
@app.route('/api/projects', methods=['POST'])
def add_project():
    data = request.json
    query = """
        INSERT INTO projects (
            project_id, project_name, tech_stack,
            employee_id, lead_id
        ) VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        data['project_id'], data['project_name'], data['tech_stack'],
        data['employee_id'], data['lead_id']
    )
    return execute_query(query, values, "Project added successfully.", "Projects", list(values))


# 9. Productivity
@app.route('/api/productivity', methods=['POST'])
def add_productivity():
    data = request.json
    query = """
        INSERT INTO productivity (
            employee_id, project_id, assigned_date,
            tasks_assigned, tasks_completed, task_quality_score,
            productivity_score, remarks
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data['employee_id'], data['project_id'], data['assigned_date'],
        data['tasks_assigned'], data['tasks_completed'],
        data.get('task_quality_score'), data.get('productivity_score'),
        data['remarks']
    )
    return execute_query(query, values, "Productivity record added successfully.", "Productivity", list(values))


if __name__ == '__main__':
    app.run(debug=True, port=5007)
