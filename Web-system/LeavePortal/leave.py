import sqlite3
from flask import Flask, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT,
        date TEXT,
        reason TEXT,
	mail TEXT,
        leave_type TEXT,
        number TEXT,
	supervisor_name TEXT,
        staff_id TEXT,
	status TEXT

    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    conn.commit()
    conn.close()

leave=Flask(__name__)
leave.secret_key = "000"
@leave.route('/')
def login_page():
	return render_template("Login.html")
@leave.route('/login', methods=['POST'])
def login():
    username = request.form['name']
    password = request.form['password']

    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        role = user[3]

        if role == "admin":
            return redirect('/dashboard')
        else:
            return redirect('/staff_dashboard')
    else:
        flash("Invalid username or password", "error")
        return redirect('/')

@leave.route('/register')
def register_page():
    return render_template("register.html")

@leave.route('/register_user', methods=['POST'])
def register_user():
    username = request.form['name']
    raw_password = request.form['password']
    role = request.form['role']

    password = generate_password_hash(raw_password)

    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        flash("Registration successful. Please login.", "success")

    except:
        flash("Username already exists.", "error")

    conn.close()

    return redirect('/')

@leave.route('/staff_dashboard')
def staff_dashboard():
    return render_template("staff_dashboard.html")

@leave.route('/leave_portal')
def leave_portal():
	return render_template("leave2.html")
	
@leave.route('/submit_leave', methods=['POST'])
def submit_leave():
	name=request.form['name']
	department=request.form['department']
	date=request.form['date']
	reason=request.form['reason']
	mail=request.form['mail']
	leave_type=request.form['leave_type']
	number=request.form['number']
	supervisor_name=request.form['supervisor_name']
	staff_id=request.form['ID']

	conn = sqlite3.connect("leave.db")
	cursor = conn.cursor()

	cursor.execute(
	"INSERT INTO leave_requests (name, department, date, reason,mail, leave_type, number, supervisor_name, staff_id) VALUES (?, ?, ?, ?,?, ?, ?, ?, ?)",
        (name, department, date, reason,mail, leave_type, number, supervisor_name, staff_id)
    )
	conn.commit()
	conn.close()
	return render_template("success.html",
		 name=name,
		 department=department,
		 date=date
	)

@leave.route('/requests')
def view_requests():
    search = request.args.get('search', '')
    status = request.args.get('status', '')

    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    query = "SELECT * FROM leave_requests WHERE 1=1"
    values = []

    if search:
        query += " AND name LIKE ?"
        values.append(f"%{search}%")

    if status:
        query += " AND status = ?"
        values.append(status)

    cursor.execute(query, values)
    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "requests.html",
        rows=rows
    )

@leave.route('/profile')
def profile():
    search = request.args.get('search', '')
    role = request.args.get('role', '')

    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE 1=1"
    values = []

    if search:
        query += " AND username LIKE ?"
        values.append(f"%{search}%")

    if role:
        query += " AND role = ?"
        values.append(role)

    cursor.execute(query, values)
    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "profile.html",
        rows=rows
    )

@leave.route('/approve/<int:id>')
def approve(id):
    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status='Approved' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/requests')

@leave.route('/update/<int:id>', methods=['POST'])
def update(id):
    name = request.form['name']
    department = request.form['department']
    date = request.form['date']
    mail=request.form['mail']
    leave_type=request.form['leave_type']
    number=request.form['number']
    supervisor_name=request.form['supervisor_name']
    staff_id=request.form['staff_id']
    reason = request.form['reason']

    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE leave_requests
        SET name=?, department=?, date=?, mail=?, leave_type=?, number=?, supervisor_name=?,staff_id=?,  reason=?
        WHERE id=?
    """, (name, department, date, mail, leave_type, number, supervisor_name, staff_id, reason,
 id))

    conn.commit()
    conn.close()

    return redirect('/requests')

@leave.route('/updateuser/<int:id>', methods=['POST'])
def updateuser(id):
    username = request.form['name']
    password = request.form['password']
    role = request.form['role']

    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET username=?, password=?, role=?
        WHERE id=?
    """, (username, password, role,
 id))

    conn.commit()
    conn.close()

    return redirect('/profile')

@leave.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM leave_requests WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/requests')

@leave.route('/deleteu/<int:id>')
def deleteu(id):
    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/profile')

@leave.route('/edit/<int:id>')
def edit(id):
    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leave_requests WHERE id=?", (id,))
    row = cursor.fetchone()

    conn.close()

    return render_template("edit.html", row=row)

@leave.route('/edituser/<int:id>')
def edituser(id):
    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=?", (id,))
    row = cursor.fetchone()

    conn.close()

    return render_template("edituser.html", row=row)

@leave.route('/reject/<int:id>')
def reject(id):
    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status='Rejected' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/requests')


@leave.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("leave.db")
    cursor = conn.cursor()

    # Total
    cursor.execute("SELECT COUNT(*) FROM leave_requests")
    total = cursor.fetchone()[0]

    # Approved
    cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status='Approved'")
    approved = cursor.fetchone()[0]

    # Pending
    cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status='Pending'")
    pending = cursor.fetchone()[0]

    # Rejected
    cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        approved=approved,
        pending=pending,
        rejected=rejected
    )

	
init_db()
if __name__ == "__main__":
    leave.run(debug=True)