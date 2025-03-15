import io
import re
import sys

from app.models import TestCaseBase


def run_safe_code(user_code, user_input: str) -> dict:
    """
    Chạy code Python với `input()`, nhưng hạn chế bảo mật và xóa prompt input.

    :param user_code: (str) Mã Python cần thực thi.
    :param user_input: (str) Chuỗi input giả lập, cách nhau bởi dòng mới `\n`.
    :return: (dict) Output đã xử lý và lỗi (nếu có).
    """
    # Danh sách các từ khóa nguy hiểm cần chặn
    forbidden_keywords = [
        "import",
        "exec",
        "eval",
        "compile",
        "open",
        "os",
        "sys",
        "subprocess",
        "shutil",
        "__import__",
        "globals",
        "locals",
    ]

    # Kiểm tra nếu code chứa từ khóa nguy hiểm
    for word in forbidden_keywords:
        if word in user_code:
            return {
                "output": "",
                "error": f"🚫 Cấm sử dụng từ khóa '{word}' trong code!",
            }

    # Xóa bỏ nội dung trong hàm input() ví dụ input("Nhập số: ") thành input()
    user_code = re.sub(r'input\([\'"].*?[\'"]\)', "input()", user_code)

    # Chuyển hướng stdin để giả lập input từ bàn phím
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    sys.stdin = io.StringIO(user_input)

    # Chuyển hướng stdout để thu thập output
    output_capture = io.StringIO()
    sys.stdout = output_capture

    # Môi trường an toàn: chỉ cho phép một số hàm cơ bản
    safe_globals = {
        "__builtins__": {
            "print": print,
            "input": input,
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "enumerate": enumerate,
            "zip": zip,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "pow": pow,
            "round": round,
            "sorted": sorted,
            "reversed": reversed,
            "all": all,
            "any": any,
            "map": map,
            "filter": filter,
        }
    }
    try:
        # Thực thi code
        exec(user_code, safe_globals, {})

        # Lấy output
        output = output_capture.getvalue()
        return {"output": output.strip(), "error": None}

    except Exception as e:
        print(e)
        return {"output": output_capture.getvalue(), "error": str(e)}

    finally:
        # Khôi phục stdin và stdout về trạng thái ban đầu
        sys.stdin = original_stdin
        sys.stdout = original_stdout


def create_result(code: str, testcases: list[TestCaseBase]) -> dict:
    score = 0
    for tc in testcases:
        result = run_safe_code(code, tc.input)
        if result["error"]:
            raise Exception(result["error"])
        if result["output"] != tc.output:
            continue
        score += 1
    status = "PASSED" if score == len(testcases) else "FAILED"
    return {"status": status, "result": score}


if __name__ == "__main__":
    user_code = """
print(input())
    """.strip()

    try:
        result = run_safe_code(user_code, "2")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Test failed: {e}")
