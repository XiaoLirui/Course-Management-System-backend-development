from db import db
from flask import Flask
from flask import request
import json
from db import Course, User, Assignment
from flask import jsonify
import os



app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# your routes here
# basic port
@app.route('/', methods=['GET'])
def hello_world():
    return os.environ["NETID"] + " was here!"


# Get all courses
@app.route('/api/courses/', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    # courses = db.session.query(Course).all()
    result = {'courses': [course.serialize() for course in courses]}
    return json.dumps(result), 200
    # return jsonify(result), 200

# Create courses
@app.route('/api/courses/', methods=['POST'])
def create_course():
    # data = request.json
    data=json.loads(request.data)
    
    if not data.get('code') or not data.get('name'):
        return json.dumps({'error': 'Missing required fields'}), 400
    
    # if Course.query.filter_by(code=data['code']).first():
    #     return json.dumps({'error': 'Course code already exists'}), 400

    course = Course(code=data['code'], name=data['name'])
    db.session.add(course)
    db.session.commit()
    return json.dumps(course.serialize()), 201
    # return jsonify(course.serialize()), 201

# Get a specific course
@app.route('/api/courses/<int:id>/', methods=['GET'])
def get_course(id):
    course = db.session.get(Course, id)
    if not course:
        return json.dumps({'error': 'Course not found'}), 404
    return json.dumps({
        "id": course.id,
        "code": course.code,
        "name": course.name,
        "assignments": [assignment.serialize() for assignment in course.assignments],
        "instructors": [instructor.serialize() for instructor in course.instructors],
        "students": [student.serialize() for student in course.students]
    }), 200

# Delete a specific course
@app.route('/api/courses/<int:id>/', methods=['DELETE'])
def delete_course(id):
    course = db.session.get(Course, id)
    if not course:
        return json.dumps({'error': 'Course not found'}), 404
    db.session.delete(course)
    db.session.commit()
    return json.dumps({
        "id": course.id,
        "code": course.code,
        "name": course.name,
        "assignments": [assignment.serialize() for assignment in course.assignments],
        "instructors": [instructor.serialize() for instructor in course.instructors],
        "students": [student.serialize() for student in course.students]
    }), 200



# Get all users
@app.route('/api/users/', methods=['GET'])
def get_users():
    users = db.session.query(User).all()
    # users = User.query.all()
    if not users:
        return json.dumps({'error': 'Users not found'}), 404
    result = {'users': [user.serialize() for user in users]}
    return json.dumps(result), 200
    # return jsonify(result), 201

# Create a user
@app.route('/api/users/', methods=['POST'])
def create_user():
    # data = request.json
    data=json.loads(request.data)
    if not data.get('netid') or not data.get('name'):
        return json.dumps({'error': 'Missing required fields'}), 400
    
    user = User(netid=data['netid'], name=data['name'])
    db.session.add(user)
    db.session.commit()
    # return jsonify(user.serialize()), 201
    return json.dumps(user.serialize()), 201

# Get a specific user
@app.route('/api/users/<int:id>/', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    if not user:
        return json.dumps({'error': 'User not found'}), 404
    return json.dumps({
        "id": user.id,
        "name": user.name,
        "netid": user.netid,
        "courses": [course.serialize_simple() for course in user.teaching_courses + user.learning_courses]
    }), 200

# Add a user to a course
@app.route('/api/courses/<int:course_id>/add/', methods=['POST'])
def add_user_to_course(course_id):
    # data = request.json
    data=json.loads(request.data)
    course = db.session.get(Course, course_id)
    if not course:
        return json.dumps({'error': 'Course not found'}), 404
    user = User.query.get(data['user_id'])
    if not user:
        return json.dumps({'error': 'User not found'}), 404
    
    if data['type'] == 'student':
        course.students.append(user)
    elif data['type'] == 'instructor':
        course.instructors.append(user)
    else:
        return json.dumps({'error': 'Invalid type specified'}), 400
    db.session.commit()
    
    return json.dumps({
        "id": course.id,
        "code": course.code,
        "name": course.name,
        "assignments": [assignment.serialize() for assignment in course.assignments],
        "instructors": [instructor.serialize() for instructor in course.instructors],
        "students": [student.serialize() for student in course.students]
    }), 200


# Create an assignment for a course
@app.route('/api/courses/<int:course_id>/assignment/', methods=['POST'])
def create_assignment(course_id):
    # data = request.json
    data=json.loads(request.data)
    course = db.session.get(Course, course_id)
    if not course:
        # return jsonify({'error': 'Course not found'}), 404
        return json.dumps({'error': 'Course not found'}), 404
    
    if not data.get('title') or not data.get('due_date'):
        return  json.dumps({'error': 'Missing required fields'}), 400
    
    assignment = Assignment(title=data['title'], due_date=data['due_date'], course_id=course_id)
    db.session.add(assignment)
    db.session.commit()

    return json.dumps({
        "id": assignment.id,
        "title": assignment.title,
        "due_date": assignment.due_date,
        "course": {
            "id": course.id,
            "code": course.code,
            "name": course.name
        }
    }), 201

@app.route('/api/courses/<int:course_id>/assignments/', methods=['GET'])
def get_course_assignments(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    assignments = course.assignments
    serialized_assignments = [assignment.serialize() for assignment in assignments]
    return json.dumps({'assignments': serialized_assignments}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
