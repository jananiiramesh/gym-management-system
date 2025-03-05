from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from utils.db_helper import db, execute_sql
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gms1234'  # Use a secure secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Janu%401802@localhost/gym_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # or 'None' if needed
app.config['SESSION_COOKIE_HTTPONLY'] = False

CORS(app, supports_credentials=True)
db.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    member_id = request.json.get('member_id')
    password = request.json.get('password')

    print("received info",member_id,password)

    query_member = text("SELECT member_id, password FROM Member WHERE member_id = :member_id AND password = :password")
    query_instructor = text("SELECT instructor_id, password FROM Instructor WHERE instructor_id = :member_id AND password = :password")
    query_admin = text("SELECT admin_id, password FROM Admin WHERE username = :member_id AND password = :password")

    result_member = db.session.execute(query_member, {"member_id": member_id, "password": password}).fetchone()
    result_instructor = db.session.execute(query_instructor, {"member_id": member_id, "password": password}).fetchone()
    result_admin = db.session.execute(query_admin, {"member_id": member_id, "password": password}).fetchone()

    if result_member:
        session.clear()
        session['user_id'] = result_member[0]  # Access by index (0 for member_id)
        session['role'] = 2  # 2 for Member
        print(session)
        return jsonify({"success": True,"user": {"id": result_member[0], "role": 2}}), 200
    elif result_instructor:
        session.clear()
        session['user_id'] = result_instructor[0]  # Access by index (0 for instructor_id)
        session['role'] = 3  # 3 for Instructor
        return jsonify({"success": True, "user": {"id": result_instructor[0], "role": 3}}), 200
    elif result_admin:
        session.clear()
        session['user_id'] = result_admin[0]  # Access by index (0 for admin_id)
        session['role'] = 1  # 1 for Admin
        return jsonify({"success": True, "user": {"id": result_admin[0], "role": 1}}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/members', methods = ['GET'])
def view_members():
    print("Current session", session)
    if not session.get('role') == 1:
        return jsonify({"error": "Unauthorized access"}), 403

    query = text("""
    SELECT
        m.member_id, m.name, m.dob, m.phone_number, m.gender,
        mem.type, mem.start_date, mem.end_date
    FROM Member m
    LEFT JOIN Membership mem ON m.member_id = mem.member_id
    """)
    
    # Fetch results as a list of tuples
    result = db.session.execute(query).fetchall()

    if result:
        members = [
            {
                "member_id": row[0],  # Access by index
                "name": row[1],
                "dob": row[2],
                "phone_number": row[3],
                "gender": row[4],
                "membership_type": row[5] if row[5] else "N/A",
                "start_date": row[6] if row[6] else "N/A",
                "end_date": row[7] if row[7] else "N/A"
            }
            for row in result
        ]
        return jsonify(members), 200
    else:
        return jsonify({"error": "some issue"}), 500
    
##display instructors as soon as admin clicks on 'instructors' all instructors details need to be fetched
@app.route('/instructors', methods = ['GET'])
def view_instructors():
    if not session.get('role') == 1:
        return jsonify({"error":"Unauthorized access"}), 403

    query = text("""
    SELECT
        instructor_id, name, specialization, years_of_experience, gender
    FROM Instructor 
    """)
    result = db.session.execute(query).fetchall()

    if result:
        instructors = [
        {
            "instructor_id": row[0],
            "name": row[1],
            "specialization": row[2],
            "years_of_experience": row[3],
            "gender": row[4]
        }
        for row in result
        ]
        return jsonify(instructors), 200
    else:
        return jsonify({"error": "some issue"}), 500

##lets only Admin add a new member, take in member details and add into db
@app.route('/members/add_member', methods=['POST'])
def add_member():
    if session.get('role') != 1:
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.get_json()

    query = text("""
    INSERT INTO Member (member_id, name, password, dob, phone_number, gender, role_id)
    VALUES (:member_id, :name, :password, :dob, :phone_number, :gender, :role_id)
    """)

    params = {
        "member_id": data['member_id'],
        "name": data['name'],
        "password": data['password'],
        "dob": data['dob'],
        "phone_number": data['phone_number'],
        "gender": data['gender'],
        "role_id": 2  #Default for a member
    }

    result = execute_sql(query, params)

    if result:
        return jsonify({"message":"member added successfully"}), 201
    else:
        return jsonify({"mesage":"an error occured"}), 500

##lets only Admin remove a member, based on his/her member_id
@app.route('/members/remove_member', methods=['POST'])
def remove_member():
    if not session.get('role') == 1:
        return jsonify({"error": "Unauthorized access"}), 403
    
    data = request.get_json()

    query = text("""
    DELETE FROM Member
    WHERE member_id = :member_id
    """)

    params = {
        "member_id": data['member_id']
    }

    result = execute_sql(query, params)

    if result:
        return jsonify({"message":"member removed successfully"}), 201
    else:
        return jsonify({"mesage":"an error occured"}), 500

##lets only Admin add a new instructor, with all the details
@app.route('/instructors/add_instructors', methods = ['POST'])
def add_instructor():
    if not session.get('role') == 1:
        return jsonify({"error":"Unauthorized access"}), 403
    
    data = request.get_json()

    query = text("""
    INSERT INTO Instructor (instructor_id, name, password, specialization, years_of_experience, gender, role_id)
    VALUES (:instructor_id, :name, :password, :specialization, :years_of_experience, :gender, :role_id)
    """)
    params = {
        "instructor_id": data['instructor_id'],
        "name": data['name'], 
        "password": data['password'],
        "specialization": data['specialization'],
        "years_of_experience": data['years_of_experience'], 
        "gender": data['gender'], 
        "role_id": 3}

    result = execute_sql(query, params)
    if result:
        return jsonify({"message":"instructor added successfully"}), 201
    else:
        return jsonify({"message":"an error occurred"}), 500
    
##lets only Admin remove an instructor, based on his/her id
@app.route('/instructors/remove_instructors', methods = ['POST'])
def remove_instructor():
    if not session.get('role') == 1:
        return jsonify({"error":"Unauthorized access"}), 403
    
    data = request.get_json()

    query = text("""
    DELETE FROM Instructor
    WHERE instructor_id = :instructor_id
    """)
    params = {
        "instructor_id": data['instructor_id']}

    result = execute_sql(query, params)
    if result:
        return jsonify({"message":"instructor removed successfully"}), 201
    else:
        return jsonify({"message":"an error occurred"}), 500
    
@app.route('/diet_plan', methods = ['GET'])
def view_diet_plan():
    if not session.get('role') == 2:
        return jsonify({"error": "Unauthorized access"}), 403

    query = text("""
    SELECT 
        mp.diet_id, 
        mp.day_of_week, 
        mp.meal_of_day, 
        mp.description, 
        mp.calories
    FROM 
        Diet_plan dp
    JOIN 
        Meal_plan mp ON dp.diet_id = mp.diet_id
    WHERE 
        dp.member_id = :user_id
        AND mp.day_of_week = DAYNAME(CURDATE());
    """)

    params = {
        "user_id": session.get('user_id')}

    result = db.session.execute(query, params).fetchall()

    if result:
        diet_plan = [
            {
                "diet_id": row[0],
                "day": row[1],
                "meal": row[2] if row[2] else "N/A",
                "description": row[3] if row[3] else "N/A",
                "calories": row[4] if row[4] else "N/A",

            }
            for row in result
        ]
        return jsonify(diet_plan), 200
    else:
        return jsonify({"error": "some issue"}), 500
    
@app.route('/diet_plan/modify', methods = ['GET'])
def modify_diet_plan():
    if not session.get('role') == 3:
        return jsonify({"error": "Unauthorized access"}), 403
    
    data = request.get_json()

    query = text("""
    UPDATE Meal_plan AS mp
    JOIN Diet_plan AS dp ON mp.diet_id = dp.diet_id
    SET mp.description = :description
    WHERE dp.member_id = :member_id AND mp.day_of_the_week = :day_of_week;
    """)

    params = {
        "description": data["description"],
        "day_of_week": data["day_of_week"],
        "member_id": data["member_id"]}

    result = db.session.execute(query, params).fetchall()

    if result:
        return jsonify({"message":"success"}), 201
    else:
        return jsonify({"mesage":"failed!!"}), 500
    
@app.route('/gym_equipment', methods = ['GET'])
def view_gym_equipment():
    if not session.get('role') == 1:
        return jsonify({"error":"Unauthorized access"}), 403

    query = text("""
    SELECT 
        name, equipment_status
    FROM Equipment
    """)
    result = db.session.execute(query).fetchall()

    if result:
        equipment = [
        {
            "name": row[0],
            "equipment_status": row[1],
        }
        for row in result
        ]
        return jsonify(equipment), 200
    else:
        return jsonify({"error": "some issue"}), 500
    
@app.route('/gym_equipment/add', methods = ['POST'])
def add_gym_equipment():
    if not session.get('role') == 1:
        return jsonify({"error":"Unauthorized access"}), 403

    name = request.json.get("name")
    equipment_status = request.json.get("equipment_status")

    query = text("""
    INSERT INTO Equipment (name, equipment_status)
    VALUES (:name, :equipment_status)
    """)

    params = {
        "name": name,
        "equipment_status": equipment_status
    }

    result = execute_sql(query, params)

    if result:
        return jsonify({"message":"equipment added successfully"}), 200
    else:
        return jsonify({"message":"equipment couldn't be added"}), 500
    
@app.route('/gym_equipment/remove', methods = ['POST'])
def remove_gym_equipment():
    if not session.get('role') == 1:
        return jsonify({"error":"Unauthorized access"}), 403

    name = request.json.get("name")

    query = text("""
    DELETE FROM Equipment
    WHERE name = :name
    """)

    params = {
        "name": name,
    }

    result = execute_sql(query, params)

    if result:
        return jsonify({"message":"equipment removed successfully"}), 200
    else:
        return jsonify({"message":"equipment couldn't be removed"}), 500
    
@app.route('/membership', methods = ['GET'])
def view_membership():
    if not session.get('role') == 2:
        return jsonify({"error":"Unauthorized access"}), 403

    query = text("""
    SELECT type, start_date, end_date
    FROM Membership
    WHERE member_id = :member_id
    """)

    params = {
        "member_id": session.get("user_id")
    }
    result = db.session.execute(query, params).fetchall()

    if result:
        membership = [
        {
            "type": row[0],
            "start_date": row[1],
            "end_date": row[2]
        }
        for row in result
        ]
        return jsonify(membership), 200
    else:
        return jsonify({"error": "some issue"}), 500
    
@app.route('/membership/modify', methods = ['GET'])
def modify_membership():
    if not session.get('role') == 1:
        return jsonify({"error":"Unauthorized access"}), 403
    
    data = request.get_json()

    query = text("""
    UPDATE Membership
    SET end_date = :end_date
    WHERE member_id = :member_id
    """)

    params = {
        "member_id": data["member_id"]
    }
    result = db.session.execute(query, params).fetchall()

    if result:
        return jsonify({"message":"success"}), 201
    else:
        return jsonify({"mesage":"failed!!"}), 500

@app.route('/payments', methods = ['GET'])
def view_payment():
    if not session.get('role') == 2:
        return jsonify({"error":"Unauthorized access"}), 403

    query = text("""
    SELECT amount, payment_date, payment_method
    FROM Payment
    WHERE member_id = :member_id
    """)

    params = {
        "member_id": session.get("user_id")
    }
    result = db.session.execute(query, params).fetchall()

    if result:
        payment = [
        {
            "amount": row[0],
            "payment_date": row[1],
            "payment_method": row[2]
        }
        for row in result
        ]
        return jsonify(payment), 200
    else:
        return jsonify({"error": "some issue"}), 500

@app.route('/schedules', methods=['GET'])
def view_all_schedules():
    if not session.get('role') == 1:
        return jsonify({"error":"Unauthorized access"}), 403

    query = text("""
    SELECT instructor_id, member_id, start_time, end_time
    FROM Schedule
    WHERE day = DAYNAME(CURDATE());
    """)

    result = db.session.execute(query).fetchall()

    if result:
        schedule = [
        {
            "instructor_id": row[0],
            "member_id": row[1],
            "start-time": row[2],
            "end-time": row[3]
        }
        for row in result
        ]
        return jsonify(schedule), 200
    else:
        return jsonify({"error": "some issue"}), 500
    
@app.route('/workout_plan', methods = ['GET'])
def view_workout_plan():
    if not session.get('role') == 2:
        return jsonify({"error":"Unauthorized access"}), 403

    query = text("""
    SELECT
        day, exercise_name, sets, reps
    FROM Exercises
    WHERE workout_id
    """)
    result = db.session.execute(query).fetchall()

    if result:
        equipment = [
        {
            "name": row[1],
            "equipment_status": row[2],
        }
        for row in result
        ]
        return jsonify(equipment), 200
    else:
        return jsonify({"error": "some issue"}), 500

if __name__ == '__main__':
    app.run(debug=True)