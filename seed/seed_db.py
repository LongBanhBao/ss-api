from datetime import date
from random import randint

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

import app.models as models
from app.database import create_db_and_tables, engine
from app.routers.auth import get_password_hash
from app.run_code import create_result


def create_user(session: Session, email: str, role: str):
    user = models.User(
        email=email,
        role=role,
        first_name="Thanh",
        last_name="Long",
        password=get_password_hash("test"),
        date_of_birth=date(2003, 8, 29),
    )
    session.add(user)
    return user


def create_assignment(
    session: Session,  # Thêm tham số session
    title: str,
    description: str,
    sample_code: str,
    teacher: models.User,
    test_cases: list[models.TestCase],
    submissions: list[models.Submission],
    saved_codes: list[models.SavedCode],
):
    assignment = models.Assignment(
        title=title,
        description=description,
        sample_code=sample_code,
        creator=teacher,
        test_cases=test_cases,
        submissions=submissions,
        saved_codes=saved_codes,
    )
    session.add(assignment)
    session.flush()  # Thêm dòng này để lấy ID của assignment
    return assignment


def create_test_cases(session: Session, input: str, output: str, type: str):
    tc = models.TestCase(input=input, output=output, type=type)
    session.add(tc)
    return tc


def create_submission(
    session: Session,
    code: str,
    test_cases: list[models.TestCaseBase],
    user: models.User,
):
    r = create_result(code, test_cases)
    submission = models.Submission(
        code=code, result=r["result"], status=r["status"], user=user
    )
    session.add(submission)
    return submission


def create_saved_code(session: Session, code: str, user: models.User):
    saved_code = models.SavedCode(code=code, user=user)
    session.add(saved_code)
    return saved_code


def create_classes(
    session: Session,
    title: str,
    description: str,
    teacher: models.User,
    students: list[models.User],
    messages: list[models.Message],
):
    class_ = models.Class(
        title=title,
        description=description,
        teacher=teacher,
        students=students,
        messages=messages,
    )
    session.add(class_)
    return class_


def create_message(
    session: Session,  # Thêm tham số session
    content: str,
    sender: models.User,
    messages: list[models.MessageAssignment],
):
    message = models.Message(content=content, sender=sender, messages=messages)
    session.add(message)
    return message


def create_message_assignment(
    session: Session,  # Thêm tham số session
    assignment: models.Assignment,
):
    message_assignment = models.MessageAssignment(assignment=assignment)
    session.add(message_assignment)
    return message_assignment


def clean_db():
    with Session(engine) as session:
        try:
            # Kiểm tra và xóa từng bảng theo thứ tự phụ thuộc
            tables = [
                "submission",  # Xóa submission trước vì nó phụ thuộc vào user, class và assignment
                "saved_code",  # Xóa saved_code vì nó phụ thuộc vào user và assignment
                "test_case",  # Xóa test_case vì nó phụ thuộc vào assignment
                "assignment",  # Xóa assignment sau khi đã xóa các bảng con
                "class",  # Xóa class
                "user",  # Xóa user cuối cùng
            ]

            for table in tables:
                try:
                    session.execute(text(f"DELETE FROM {table}"))
                except Exception as e:
                    print(f"Không thể xóa bảng {table}: {str(e)}")
                    continue

            session.commit()
        except Exception as e:
            print(f"Lỗi khi xóa database: {str(e)}")
            session.rollback()


def main():
    create_db_and_tables()
    clean_db()  # Thêm dòng này

    students_count = 5

    with Session(engine) as session:
        # Tạo người dùng
        admin = create_user(session, "hieuvnkudo040303@gmail.com", "admin")
        create_user(session, "learnshullkudo@gmail.com", "teacher")
        teacher_main = create_user(session, "teacher_main@gmail.com", "teacher")
        teacher_other = create_user(session, "teacher_other@gmail.com", "teacher")
        students = [
            create_user(session, f"student_{i}@gmail.com", "student")
            for i in range(students_count)
        ]

        print("Admin:", admin)
        print("Giáo viên:", teacher_main, teacher_other)
        print("Học sinh:", students)

        sample_code1 = """
a, b = map(int, input().split())
print(a+b)
"""
        # Tạo test cases trong cùng session
        test_cases = [
            create_test_cases(session, "1 2", "3", "sample"),
            create_test_cases(session, "-1 1", "0", "sample"),
            create_test_cases(session, "4 5", "9", "hidden"),
            create_test_cases(session, "6 7", "13", "hidden"),
        ]

        code_submission = """
a, b = map(int, input().split())
print(a+b)
"""
        submissions1 = [
            create_submission(session, code_submission, test_cases, students[0])
            for i in range(randint(1, 5))
        ]
        code_submission = """
a, b = map(int, input().split())
print(a+b*2)
"""
        submissions2 = [
            create_submission(session, code_submission, test_cases, students[1])
            for i in range(randint(1, 5))
        ]

        saved_code1 = create_saved_code(session, "haha - savedcode - 1", students[1])
        saved_code2 = create_saved_code(session, "hehe - savedcode - 2", students[0])

        assignment1 = create_assignment(
            session,  # Truyền session vào
            title="Cộng 2 số",
            description="Viết chương trình nhập vào 2 số, sau đó in ra tổng 2 số đó.",
            sample_code=sample_code1,
            teacher=teacher_main,
            test_cases=test_cases,
            submissions=submissions1 + submissions2,
            saved_codes=[
                saved_code1,
                saved_code2,
            ],  # Đổi tên từ saved_code thành saved_codes
        )
        session.refresh(assignment1)  # Thêm dòng này

        # Tạo bài tập 2
        sample_code = """
arr = list(map(int, input().split()))
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
print(insertion_sort(arr))
"""

        test_cases = [
            create_test_cases(session, "1 2 3 4 5", "1 2 3 4 5", "sample"),
            create_test_cases(session, "5 4 3 2 1", "1 2 3 4 5", "hidden"),
            create_test_cases(session, "3 2 1 4 5", "1 2 3 4 5", "hidden"),
            create_test_cases(session, "10 9 8 7 6", "6 7 8 9 10", "hidden"),
        ]

        sample_code = """
print(input())
"""

        submissions1 = [
            create_submission(session, sample_code, test_cases, students[0])
            for i in range(3)
        ]

        sample_code = """
arr = list(map(int, input().split()))
print(" ".join(map(str, sorted(arr))))
"""

        assignment2 = create_assignment(
            session,  # Truyền session vào
            title="Thuật toán Sắp xếp chọn",
            description="Viết thuật toán sắp xếp chọn tăng dần.\nInput: Dãy số nguyên\nOutput: Dãy số đã sắp xếp",
            sample_code=sample_code,
            teacher=teacher_main,
            test_cases=test_cases,
            submissions=submissions1 + submissions2,
            saved_codes=[
                saved_code1,
                saved_code2,
            ],  # Đổi tên từ saved_code thành saved_codes
        )
        session.refresh(assignment2)  # Thêm dòng này

        # Commit session sau khi tạo xong
        session.commit()

        print("Bài tập đã được tạo:")
        print(f"Assignment 1: {assignment1.title}")  # In thêm thông tin
        print(f"Assignment 2: {assignment2.title}")  # In thêm thông tin


if __name__ == "__main__":
    main()
