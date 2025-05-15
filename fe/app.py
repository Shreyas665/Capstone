from flask import Flask, request, jsonify, render_template_string
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(
        host='34.93.42.89',
        user='root',
        password='root@123',
        database='capstone'
)
cursor = conn.cursor(dictionary=True)

tables = {
    'employees': ['employee_id', 'name', 'dob', 'join_date', 'department_id', 'designation_id', 'location_id'],
    'departments': ['department_id', 'department_name'],
    'attendance': ['id', 'employee_id', 'date', 'check_in', 'check_out', 'status', 'working_hours', 'late_duration', 'is_half_day'],
    'leave-records': ['id', 'employee_id', 'leave_id', 'start_date', 'end_date', 'reason', 'status'],
    'leave-types': ['leave_id', 'leave_type', 'max_leaves_per_year'],
    'locations': ['location_id', 'location_name'],
    'job-roles': ['designation_id', 'designation_title'],
    'projects': ['project_id', 'project_name', 'employee_id', 'start_date', 'end_date'],
    'productivity': ['id', 'employee_id', 'date', 'tasks_completed', 'hours_worked', 'productivity_score']
}

@app.route('/')
def index():
    return render_template_string(open('/home/nineleaps/Downloads/Capstone/fe/index.html').read())

@app.route('/form/<table>')
def get_form(table):
    if table not in tables:
        return f"Unknown table: {table}", 404
    inputs = ''.join([f'<label>{col}:<input name="{col}" required></label>' for col in tables[table]])
    return f'''
      <form id="{table}Form">
        {inputs}
        <button type="submit">Submit</button>
      </form>
      <table id="{table}Table"></table>
    '''

@app.route('/api/<table>', methods=['POST'])
def insert_data(table):
    if table not in tables:
        return jsonify({"error": "Unknown table"}), 400
    data = request.json
    columns = ', '.join(tables[table])
    placeholders = ', '.join(['%s'] * len(tables[table]))
    values = [data.get(col) for col in tables[table]]
    try:
        cursor.execute(f"INSERT INTO {table.replace('-', '_')} ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        return jsonify({"message": "Record inserted"})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

@app.route('/api/<table>', methods=['GET'])
def get_data(table):
    if table not in tables:
        return jsonify({"error": "Unknown table"}), 400
    try:
        cursor.execute(f"SELECT * FROM {table.replace('-', '_')}")
        return jsonify(cursor.fetchall())
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

@app.route('/api/<table>/<id>', methods=['DELETE'])
def delete_data(table, id):
    if table not in tables:
        return jsonify({"error": "Unknown table"}), 400
    key_col = tables[table][0]  # Assume first column is primary key
    try:
        cursor.execute(f"DELETE FROM {table.replace('-', '_')} WHERE {key_col} = %s", (id,))
        conn.commit()
        return jsonify({"message": "Record deleted"})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

if __name__ == '__main__':
    app.run(debug = True,port=5009)
