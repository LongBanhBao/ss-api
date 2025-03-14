import seed.test_1 as test_1
import seed.test_2 as test_2

teacher_emails = ["teacher1@gmail.com", "teacher2@gmail.com"]

password = "test"

students_emails = [
    "student1@gmail.com",
    "student2@gmail.com",
    "student3@gmail.com",
    "student4@gmail.com",
]

admins_emails = ["admin@gmail.com"]


def create_user(email, password, role):
    return {
        "email": email,
        "password": password,
        "first_name": f"{email.split('@')[0]}",
        "last_name": "Haha",
        "role": role,
        "date_of_birth": "2003-08-29",
    }


teachers = [create_user(email, password, "teacher") for email in teacher_emails]

students = [create_user(email, password, "student") for email in students_emails]

admins = [create_user(email, password, "admin") for email in admins_emails]

assignments = [test_1.assignment, test_2.assignment]

classes = [
    {
        "title": "Lớp 12A",
        "description": "Lớp học 12A",
        "image_url": None,
        "teacher_emails": teacher_emails,
        "student_emails": students_emails[0:2],
    },
    {
        "title": "Lớp 12B",
        "description": "Lớp học 12B",
        "image_url": None,
        "teacher_emails": teacher_emails,
        "student_emails": students_emails[2:4],
    },
]
