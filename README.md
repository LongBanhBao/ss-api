# Tạo môi trường ảo
```bash
python3 -m venv venv
```

# Kích hoạt môi trường ảo
```bash
.venv\Scripts\activate
```

# Cài đặt thư viện
```bash
pip install -r requirements.txt
```

# Cập nhật file requirements.txt
```bash
pip freeze > requirements.txt
```

# Chạy chương trình
```bash
fastapi dev app/main.py
```

# Run test
```bash
pytest
```

# Loại bỏ file cache trên PowerShell
```bash
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Remove-Item -Recurse -Force .pytest_cache
Remove-Item -Force database.db
```

# Loại bỏ database.db
```bash
Remove-Item -Force database.db | python -m seed.seed_db
```

# Thứ tự chạy

## Mở Terminal trong thư mục gốc

## Kiểm tra phiên bản python, yêu cầu 3.12
```bash
python --version
```

## Tạo môi trường ảo
```bash
python3 -m venv venv
```

## Kích hoạt môi trường ảo
```bash
.venv\Scripts\activate
```

## Cài đặt thư viện
```bash
pip install -r requirements.txt
```

## Chạy chương trình
```bash
Remove-Item -Force test.db | python -m seed.seed_db
fastapi dev app/main.py
```

## Chạy với uvicorn trên Render
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```