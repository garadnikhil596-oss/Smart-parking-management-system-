from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = "tms_secret_key"

# DATABASE CONNECTION
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="nikhil",
        user="postgres",
        password="1993",
        port="5432"
    )

# ==============================
# LOGIN
# ==============================
@app.route('/')
def home():
    return render_template("index.html")


# LOGIN
@app.route('/index', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(
        "SELECT * FROM admin WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        session['username'] = user['username']
        return redirect(url_for('dashboard'))

    else:
        return "Invalid Username or Password"


# SIGNUP
@app.route('/signup', methods=['POST'])
def signup():

    name = request.form['name']
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO admin (name, username, password) VALUES (%s,%s,%s)",
        (name, username, password)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('home'))
# ==============================
# DASHBOARD
# ==============================

@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT COUNT(*) FROM category")
    total_category = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM category WHERE status=1")
    active_category = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(vehicle_limit),0) FROM category")
    total_slots = cur.fetchone()[0]

    vehicles = session.get('vehicles', [])

    vehicles_parked = sum(1 for v in vehicles if v.get('status') == "Parked")
    departed_vehicles = sum(1 for v in vehicles if v.get('status') == "Departed")

    total_earnings = sum(float(v.get('charge',0)) for v in vehicles)

    total_records = len(vehicles)

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        username=session['username'],
        vehicles_parked=vehicles_parked,
        departed_vehicles=departed_vehicles,
        active_category=active_category,
        total_earnings=total_earnings,
        total_records=total_records,
        total_slots=total_slots,
        vehicles=vehicles
    )

# ==============================
# CATEGORY PAGE
# ==============================

@app.route('/category')
def category():
    if 'username' not in session:
        return redirect(url_for('home'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM category ORDER BY cat_id DESC")
    categories = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("category.html", categories=categories)

@app.route('/add_category', methods=['POST'])
def add_category():
    area_number = request.form['area_number']
    vehicle_type = request.form['vehicle_type']
    vehicle_limit = request.form['vehicle_limit']
    parking_charge = request.form['parking_charge']
    status = int(request.form.get('status', 1))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO category (parking_area_no, vehicle_type, vehicle_limit, parking_charge, status)
        VALUES (%s,%s,%s,%s,%s)
    """, (area_number, vehicle_type, vehicle_limit, parking_charge, status))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('category'))


# ==============================
# EDIT CATEGORY PAGE
# ==============================
@app.route('/edit_category/<int:id>', methods=['GET'])
def edit_category(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT * FROM category WHERE cat_id = %s", (id,))
    category = cur.fetchone()

    cur.close()
    conn.close()

    if not category:
        return "Category Not Found", 404

    return render_template("edit_category.html", category=category)

@app.route('/toggle_status/<int:id>')
def toggle_status(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM category WHERE cat_id = %s", (id,))
    result = cur.fetchone()
    if result:
        new_status = 0 if result[0]==1 else 1
        cur.execute("UPDATE category SET status=%s WHERE cat_id=%s", (new_status,id))
        conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('category'))

@app.route('/delete_category/<int:id>')
def delete_category(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM category WHERE cat_id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('category'))


@app.route('/update_category/<int:id>', methods=['POST'])
def update_category(id):
    area_number = request.form['area_number']
    vehicle_type = request.form['vehicle_type']
    vehicle_limit = request.form['vehicle_limit']
    parking_charge = request.form['parking_charge']
    status = int(request.form['status'])

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE category
        SET parking_area_no=%s,
            vehicle_type=%s,
            vehicle_limit=%s,
            parking_charge=%s,
            status=%s
        WHERE cat_id=%s
    """, (area_number, vehicle_type, vehicle_limit, parking_charge, status, id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('category'))

# ==============================
# VEHICLE ENTRY
# ==============================

from datetime import datetime
import psycopg2.extras

app.secret_key = "nikhil_secret_key"

# ------------------- Vehicle Entry Route -------------------
@app.route('/vehicle-entry', methods=['GET','POST'])
def vehicle_entry():
    if 'username' not in session:
        return redirect(url_for('home'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Active categories fetch
    cur.execute("SELECT * FROM category WHERE status=1")
    categories = cur.fetchall()

    # Vehicles from session
    vehicles = session.get('vehicles', [])

    if request.method == 'POST':
        vehicle_no = request.form.get('vehicle_no')
        vehicle_type = request.form.get('vehicle_type')
        parking_area_no = request.form.get('parking_area_no')

        # DB मधून charge fetch करा (column नाव बदलले आहे)
        cur.execute("SELECT parking_charge FROM category WHERE parking_area_no=%s", (parking_area_no,))
        result = cur.fetchone()
        parking_charge = result['parking_charge'] if result else 0

        # Vehicle dictionary तयार करा
        vehicle = {
            "vehicle_no": vehicle_no,
            "vehicle_type": vehicle_type,
            "parking_area_no": parking_area_no,
            "charge": parking_charge,
            "arrival_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Parked"
        }

        vehicles.append(vehicle)
        session['vehicles'] = vehicles

        return redirect(url_for('vehicle_entry'))

    cur.close()
    conn.close()

    return render_template(
        "vehicle_entry.html",
        categories=categories,
        vehicles=vehicles
    )


# ------------------- View Receipt Route -------------------
@app.route('/view-receipt/<int:index>')
def view_receipt(index):
    vehicles = session.get('vehicles', [])

    if index < 0 or index >= len(vehicles):
        return "Invalid Receipt"

    vehicle = vehicles[index]
    return render_template("receipt.html", vehicle=vehicle)

@app.route('/manage-vehicles')
def manage_vehicles():

    if 'username' not in session:
        return redirect(url_for('home'))

    vehicles = session.get('vehicles', [])

    return render_template("manage_vehicles.html", vehicles=vehicles)



@app.route('/update-status', methods=['POST'])
def update_status():

    index = int(request.form.get('index'))
    vehicles = session.get('vehicles', [])

    if 0 <= index < len(vehicles):
        vehicles[index]['status'] = "Departed"
        session['vehicles'] = vehicles

    return redirect(url_for('manage_vehicles'))


# report//

from flask import Flask, render_template
import psycopg2
import json
from datetime import datetime, timedelta
@app.route("/report")
def report():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        data_points = []

        # Last 7 days
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            formatted_date = date.strftime("%Y-%m-%d")

            cur.execute(
                "SELECT COUNT(*) FROM add_vehicle WHERE DATE(arrival_time) = %s",
                (formatted_date,)
            )
            count = cur.fetchone()[0]

            data_points.append({
                "x": int(date.timestamp() * 1000),
                "y": count
            })

        cur.close()
        conn.close()

        # Sort data by date
        data_points = sorted(data_points, key=lambda k: k["x"])

        return render_template("report.html", data_points=data_points)

    except Exception as e:
        return f"Error: {str(e)}"



        # vehicle record 


@app.route('/records', methods=['GET','POST'])
def records():

    all_vehicles = session.get('vehicles', [])
    vehicles = []
    search = ""

    if request.method == "POST":

        search = request.form.get('search','').strip().lower()

        if search:
            filtered = []

            for i, v in enumerate(all_vehicles):
                receipt_no = str(i+1)

                if search in v['vehicle_no'].lower() or search == receipt_no:
                    filtered.append(v)

            vehicles = filtered

    return render_template("search.html", vehicles=vehicles, search=search)


   # account setting


@app.route('/account_setting', methods=['GET','POST'])
def account_setting():

    if 'password' not in session:
        session['password'] = "admin123"   # default password

    message = ""

    if request.method == "POST":

        current = request.form.get("current_password")
        new = request.form.get("new_password")
        confirm = request.form.get("confirm_password")

        stored_password = session['password']

        if current != stored_password:
            message = "Current password is wrong"

        elif new != confirm:
            message = "New password and confirm password do not match"

        else:
            session['password'] = new
            message = "Password changed successfully"

    return render_template("account_setting.html", message=message)



  # add admin######



@app.route('/admin_list')
def admin_list():

    conn = psycopg2.connect(
        host="localhost",
        database="nikhil",
        user="postgres",
        password="1993"
    )

    cur = conn.cursor()

    cur.execute("SELECT * FROM admin ORDER BY id")

    admins = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin_list.html", admins=admins)



@app.route('/delete_admin/<int:id>')
def delete_admin(id):

    conn = psycopg2.connect(
        host="localhost",
        database="nikhil",
        user="postgres",
        password="1993"
    )

    cur = conn.cursor()

    cur.execute("DELETE FROM admin WHERE id=%s", (id,))

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('admin_list'))


@app.route('/edit_admin/<int:id>', methods=['GET','POST'])
def edit_admin(id):

    conn = psycopg2.connect(
        host="localhost",
        database="nikhil",
        user="postgres",
        password="1993"
    )

    cur = conn.cursor()

    # POST → Update Admin
    if request.method == "POST":

        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")

        query = """
        UPDATE admin
        SET name=%s, username=%s, password=%s
        WHERE id=%s
        """

        cur.execute(query, (name, username, password, id))
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for('admin_list'))

    # GET → Show Admin Data

    cur.execute("SELECT * FROM admin WHERE id=%s", (id,))
    admin = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("edit_admin.html", admin=admin)
# ==============================
# LOGOUT
# ==============================

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ==============================
# RUN SERVER
# ==============================

if __name__ == '__main__':
    app.run(debug=True)