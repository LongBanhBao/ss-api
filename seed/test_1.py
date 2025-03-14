from app.run_code import create_result

assignment = {
    "title": "Nhập và xuất dữ liệu",
    "description": "Viết chương trình nhập nội dung sau đó xuất ra nội dung vừa nhập",
    "category": "general",
    "sample_code": """
s = input()
print(s)
""".strip(),
    "test_cases": [
        {"input": "Hello", "output": "Hello", "type": "sample"},
        {"input": "World", "output": "World", "type": "hidden"},
        {"input": "Hello, world!", "output": "Hello, world!", "type": "hidden"},
        {"input": "Hello, world!", "output": "Hello, world!", "type": "hidden"},
    ],
    "submissions": [
        {
            "code": """
print(input())
""".strip(),
        },
        {
            "code": """
s = input("Nhập nội dung: ")
print(s)
""".strip(),
        },
    ],
    "saved_codes": [
        {
            "code": """
s = input("Lưu nội dung: ")
print("Nội dung đã lưu:", s)    
""".strip(),
        },
        {
            "code": """
s = input("Nhập nội dung để lưu: ")
print("Nội dung đã lưu:", s)
""".strip(),
        },
    ],
}
