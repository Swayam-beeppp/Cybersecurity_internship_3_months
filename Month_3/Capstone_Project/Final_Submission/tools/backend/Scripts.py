
import face_recognition
import face_recognition_models

import cv2
import numpy as np
import os
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

# --- MongoDB Connection Setup ---
client = MongoClient('mongodb://localhost:27017/')
db_mongo = client['face'] # Your database name
register_collection = db_mongo['register']
login_history_collection = db_mongo['login_history']
attendance_collection = db_mongo['attendance']
tasks_collection = db_mongo['tasks']

# --- Global variable and paths (unchanged) ---
db = []
known_path = os.path.join(os.getcwd(), "Images/Known_faces/")
unknown_path = os.path.join(os.getcwd(), "Images/Unknown_faces/")

def get_data():
    """Fetches user data from MongoDB and populates the global 'db' list."""
    global db
    db.clear()
    for user in register_collection.find({}, {"name": 1, "encoding": 1}):
        db.append([str(user['_id']), user['name'], user['encoding']])

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

@app.route('/register', methods=['GET'])
def register():
    name = request.args.get("name")
    if not name:
        return "Missing name", 400

    video_capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    frame = None
    first_frame = None

    while True:
        ret, current_frame = video_capture.read()
        if not ret or current_frame is None:
            continue

        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if first_frame is None:
            first_frame = gray
            continue

        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = any(cv2.contourArea(contour) > 1000 for contour in contours)
        cv2.imshow('Motion Detection - Register (Wait for motion + press Q)', current_frame)

        if motion_detected:
            print("Motion Detected!")

        if cv2.waitKey(1) & 0xFF == ord('q') and motion_detected:
            frame = current_frame
            break

    video_capture.release()
    cv2.destroyAllWindows()

    if frame is None:
        return "Error: Could not capture image."

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    if not face_encodings:
        return "No face detected. Try again in better lighting."

    # --- Store encoding as a list in MongoDB ---
    encoding_list = face_encodings[0].tolist()
    result = register_collection.insert_one({"name": name, "encoding": encoding_list})
    inserted_id = str(result.inserted_id)

    return jsonify({"message": "Face registered", "id": inserted_id, "name": name})

@app.route('/register/details', methods=['POST'])
def register_details():
    data = request.get_json()
    id = data.get("id")
    department = data.get("department")
    region = data.get("region")

    if not all([id, department, region]):
        return "Missing data", 400

    # --- Update document in MongoDB ---
    register_collection.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'department': department, 'region': region}}
    )
    return "Details updated successfully"

@app.route("/login")
def login():
    get_data()
    if not db:
        return jsonify({"error": "You are unknown. First register yourself."}), 404

    known_face_encodings = [i[2] for i in db]
    known_face_ids = [i[0] for i in db]

    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    frame = None
    first_frame = None

    while True:
        ret, current_frame = video_capture.read()
        if not ret or current_frame is None:
            continue
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if first_frame is None:
            first_frame = gray
            continue
        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_detected = any(cv2.contourArea(contour) > 1000 for contour in contours)
        cv2.imshow('Motion Detection - Login (Wait for motion + press Q)', current_frame)
        if motion_detected:
            print("Motion Detected!")
        if cv2.waitKey(1) & 0xFF == ord('q') and motion_detected:
            frame = current_frame
            break

    if frame is None:
        return jsonify({"error": "Error: Failed to capture image."}), 500

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    msg = {"name": "Unknown", "redirect": "/unauthorized"}

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            user_id = known_face_ids[best_match_index] # This is now a string ObjectId
            user_id_obj = ObjectId(user_id)
            
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in ip_address:
                ip_address = ip_address.split(',')[0].strip()

            # --- Insert login record into MongoDB ---
            login_history_collection.insert_one({
                "user_id": user_id_obj,
                "time": datetime.now(),
                "ip_address": ip_address
            })
            
            # --- Fetch user details from MongoDB ---
            row = register_collection.find_one({'_id': user_id_obj})

            if row and row.get('department'):
                department = row['department'].lower()
                msg = {
                    "id": user_id,
                    "name": row['name'],
                    "department": row['department'],
                    "region": row.get('region'),
                    "redirect": "/admin" if department == "admindashboard" else "/UserDashboard"
                }
            break

    os.makedirs(unknown_path, exist_ok=True)
    rand_no = np.random.random_sample()
    cv2.imwrite(os.path.join(unknown_path, f"{rand_no}.jpg"), frame)

    video_capture.release()
    cv2.destroyAllWindows()
    return jsonify(msg)

@app.route("/UserDashboard/<user_id>")
def user_dashboard(user_id):
    user_id_obj = ObjectId(user_id)

    user = register_collection.find_one(
        {'_id': user_id_obj}, 
        {'name': 1, 'department': 1, 'region': 1, '_id': 0}
    )

    history_cursor = login_history_collection.find(
        {'user_id': user_id_obj}
    ).sort('time', -1).limit(10)
    history = [row['time'].strftime('%Y-%m-%d %I:%M %p') for row in history_cursor]

    row = attendance_collection.find_one({'user_id': user_id_obj})
    attendance = {
        "totalDays": row['total_days'] if row else 0,
        "present": row['present_days'] if row else 0,
        "absent": (row['total_days'] - row['present_days']) if row else 0
    }

    tasks_cursor = tasks_collection.find({'user_id': user_id_obj})
    tasks = []
    for task in tasks_cursor:
        tasks.append({
            'id': str(task['_id']),
            'task': task['task'],
            'status': task['status'],
            'task_image_url': f"http://localhost:5000/static/images/{task.get('task_image_url')}" if task.get('task_image_url') else None
        })
    
    return jsonify({
        "user": user,
        "login_history": history,
        "attendance": attendance,
        "tasks": tasks
    })

@app.route("/all-users")
def all_users():
    users_cursor = register_collection.find({}, {'name': 1, 'department': 1, 'region': 1})
    users = []
    for user in users_cursor:
        users.append({
            'id': str(user['_id']),
            'name': user.get('name'),
            'department': user.get('department'),
            'region': user.get('region')
        })
    return jsonify(users)

@app.route("/AdminDashboard/<admin_id>")
def admin_dashboard(admin_id):
    admin_id_obj = ObjectId(admin_id)
    admin = register_collection.find_one(
        {'_id': admin_id_obj, 'department': 'admin'},
        {'name': 1, 'department': 1, 'region': 1, '_id': 0}
    )

    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    history_cursor = login_history_collection.find({'user_id': admin_id_obj}).sort('time', -1).limit(10)
    history = [row['time'].strftime('%Y-%m-%d %I:%M %p') for row in history_cursor]

    total_users = register_collection.count_documents({'department': {'$ne': 'admin'}})
    total_tasks = tasks_collection.count_documents({})

    return jsonify({
        "admin": admin,
        "login_history": history,
        "stats": {
            "total_users": total_users,
            "total_tasks": total_tasks
        }
    })

@app.route("/edit-user/<user_id>", methods=['POST'])
def edit_user(user_id):
    data = request.get_json()
    name = data.get("name")
    department = data.get("department")
    region = data.get("region")

    register_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'name': name, 'department': department, 'region': region}}
    )
    return jsonify({"message": "User updated successfully."})

@app.route("/assign-task", methods=['POST'])
def assign_task():
    data = request.get_json()
    user_id = data.get("user_id")
    task = data.get("task")
    status = data.get("status", "Pending")

    tasks_collection.insert_one({
        'user_id': ObjectId(user_id),
        'task': task,
        'status': status
    })
    return jsonify({"message": "Task assigned successfully."})

@app.route("/get-tasks/<user_id>")
def get_tasks(user_id):
    tasks_cursor = tasks_collection.find({'user_id': ObjectId(user_id)})
    tasks = []
    for task in tasks_cursor:
        tasks.append({
            'id': str(task['_id']),
            'task': task['task'],
            'status': task['status']
        })
    return jsonify(tasks)

@app.route("/get-attendance/<user_id>")
def get_attendance(user_id):
    attendance_cursor = attendance_collection.find({'user_id': ObjectId(user_id)})
    attendance = []
    for record in attendance_cursor:
        attendance.append({
            'user_id': str(record['user_id']),
            'total_days': record['total_days'],
            'present_days': record['present_days']
        })
    return jsonify(attendance)

@app.route("/get-login-history/<user_id>")
def get_login_history(user_id):
    history_cursor = login_history_collection.find({'user_id': ObjectId(user_id)}).sort('time', -1)
    history = []
    for row in history_cursor:
        history.append({
            'id': str(row['_id']),
            'user_id': str(row['user_id']),
            'time': row['time'],
            'ip_address': row['ip_address']
        })
    return jsonify(history)

@app.route('/update-task-status', methods=['POST'])
def update_task_status():
    data = request.get_json()
    task_id = data.get('task_id')
    new_status = data.get('status')
    
    tasks_collection.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': {'status': new_status}}
    )
    return jsonify({'message': 'Task status updated successfully'}), 200

@app.route('/login-history', methods=['GET'])
def get_all_login_history():
    history_cursor = login_history_collection.find({}).sort('time', -1).limit(20)
    history = [{
        "id": str(row['_id']),
        "user_id": str(row['user_id']),
        "login_time": row['time'].strftime('%Y-%m-%d %I:%M %p'),
        "ip_address": row['ip_address']
    } for row in history_cursor]
    return jsonify(history)

@app.route('/delete-login-history/<login_id>', methods=['DELETE'])
def delete_login_history(login_id):
    login_history_collection.delete_one({'_id': ObjectId(login_id)})
    return jsonify({"message": "Login entry deleted successfully"})

@app.route('/delete-user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user_id_obj = ObjectId(user_id)
    
    # Delete related data in other collections
    tasks_collection.delete_many({"user_id": user_id_obj})
    login_history_collection.delete_many({"user_id": user_id_obj})
    attendance_collection.delete_many({"user_id": user_id_obj})

    # Delete the user from the register collection
    register_collection.delete_one({"_id": user_id_obj})
    
    return jsonify({'message': 'User and related data deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)