assignment = {
    "title": "Cộng số nguyên",
    "description": "Viết chương trình cộng 2 số nguyên",
    "category": "general",
    "sample_code": """
def add(a, b):
    return a + b
a, b = map(int, input().split())
print(add(a, b))
""".strip(),
    "test_cases": [
        {"input": "1 2", "output": "3", "type": "sample"},
        {"input": "2 4", "output": "6", "type": "hidden"},
        {"input": "-1 1", "output": "0", "type": "hidden"},
        {"input": "0 0", "output": "0", "type": "hidden"},
    ],
    "submissions": [
        {
            "code": """ 
def add(a, b):
    return a + b
a, b = map(int, input().split())
print(add(a, b))           
""".strip(),
        },
        {
            "code": """
def add(a, b):
    return a + b
a, b = map(int, input("Nhập a, b: ").split())
print(add(a, b))           
""".strip(),
        },
        {
            "code": """
def add(a, b):
    return a - b  # Sai
a, b = map(int, input().split())
print(add(a, b))           
""".strip(),
        },
        {
            "code": """
def add(a, b):
    return a + b
a, b = map(int, input().split())
print(add(a, b))           
""".strip(),
        },
    ],
    "saved_codes": [
        {
            "code": """
print("Hello, world!")
""".strip(),
        },
        {
            "code": """
print("Hehe")
""".strip(),
        },
    ],
}
