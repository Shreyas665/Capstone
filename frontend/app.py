from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host='34.93.42.89',
        user='root',
        password='root@123',
        database='capstone'
    )

@app.route('/')
def home():
    return render_template('index.html')

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
    return execute_query(query, values, "Employee added successfully.")

# 2. Departments
@app.route('/api/departments', methods=['POST'])
def add_department():
    data = request.json
    query = "INSERT INTO departments (department_id, department_name) VALUES (%s, %s)"
    values = (data['department_id'], data['department_name'])
    return execute_query(query, values, "Department added successfully.")

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
    return execute_query(query, values, "Attendance logged successfully.")

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
    return execute_query(query, values, "Leave record added successfully.")

# 5. Leave Types
@app.route('/api/leave-types', methods=['POST'])
def add_leave_type():
    data = request.json
    query = """
        INSERT INTO leave_types (leave_type_id, leave_type, description)
        VALUES (%s, %s, %s)
    """
    values = (data['leave_type_id'], data['leave_type'], data['description'])
    return execute_query(query, values, "Leave type added successfully.")

# 6. Locations
@app.route('/api/locations', methods=['POST'])
def add_location():
    data = request.json
    query = "INSERT INTO locations (location_id, location_name) VALUES (%s, %s)"
    values = (data['location_id'], data['location_name'])
    return execute_query(query, values, "Location added successfully.")

# 7. Job Roles
@app.route('/api/job-roles', methods=['POST'])
def add_job_role():
    data = request.json
    query = """
        INSERT INTO job_roles (designation_id, designation_name)
        VALUES (%s, %s)
    """
    values = (data['designation_id'], data['designation_name'])
    return execute_query(query, values, "Job role added successfully.")

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
        data['project_id'], data['project_name'],
        data['tech_stack'], data['employee_id'], data['lead_id']
    )
    return execute_query(query, values, "Project added successfully.")

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
        data.get('task_quality_score'),
        data.get('productivity_score'),
        data['remarks']
    )
    return execute_query(query, values, "Productivity record added successfully.")

# 🔁 Utility to avoid repetition
# def execute_query(query, values, success_message):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute(query, values)
#         conn.commit()
#         return jsonify({"message": success_message})
#     except Exception as e:
#         return jsonify({"error": str(e)})
#     finally:
#         cursor.close()
#         conn.close()

def execute_query(query, values, success_message):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(query, values)
        conn.commit()

        # Confirm at least 1 row was affected
        if cursor.rowcount == 0:
            return jsonify({"error": "Insert failed or no rows affected."}), 400

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


# Run app
if __name__ == '__main__':
    app.run(debug=True, port=5007)
