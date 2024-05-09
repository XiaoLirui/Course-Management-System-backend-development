from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

course_instructor = db.Table('course_instructor',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

course_student = db.Table('course_student',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    # netid = db.Column(db.String(64), unique=True, nullable=False)
    netid = db.Column(db.String(64), nullable=False)
    teaching_courses = db.relationship('Course', secondary=course_instructor, back_populates='instructors')
    learning_courses = db.relationship('Course', secondary=course_student, back_populates='students')
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'courses': [course.serialize_simple() for course in self.teaching_courses+self.learning_courses]
        }
    
    def serialize_simple(self):
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid
        }
    
# your classes here
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    code = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    assignments = db.relationship('Assignment',cascade="delete")
    instructors = db.relationship('User', secondary=course_instructor, back_populates='teaching_courses')
    students = db.relationship('User', secondary=course_student, back_populates='learning_courses')

    def serialize(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'assignments': [assignment.serialize_simple() for assignment in self.assignments],
            'instructors': [instructor.serialize_simple() for instructor in self.instructors],
            'students': [student.serialize_simple() for student in self.students]
        }
    
    def serialize_simple(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }



class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    due_date = db.Column(db.Integer, nullable=False)  # Unix timestamp
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'due_date': self.due_date,
            'course': Course.query.filter_by(id=self.course_id).first().serialize_simple()
        }
    def serialize_simple(self):
        return {
            'id': self.id,
            'title': self.title,
            'due_date': self.due_date
        }

