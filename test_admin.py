import requests

print("🔐 Тестируем вход...")

# 1. Логинимся
login_resp = requests.post(
    "http://127.0.0.1:8000/login",
    json={"email": "maka2r_1final_test@example.com", "password": "1s3uper_secret_123"}
)

print(f"📡 Login статус: {login_resp.status_code}")
print(f"📦 Login заголовки: {login_resp.headers.get('content-type')}")
print(f"📄 Login тело (первые 300 символов): {login_resp.text[:300]}")

# Если статус не 200 — останавливаемся
if login_resp.status_code != 200:
    print("❌ Login не удался, останавливаем тест")
    exit()

# Пробуем распарсить JSON
try:
    token = login_resp.json()["access_token"]
    print(f"🎫 Токен получен: {token[:40]}...")
except Exception as e:
    print(f"❌ Ошибка парсинга JSON: {e}")
    print(f"💡 Возможно, сервер вернул ошибку. Проверь терминал с сервером!")
    exit()

# 2. Пробуем зайти в админку
print("\n🔐 Тестируем доступ к /admin/dashboard...")
headers = {"Authorization": f"Bearer {token}"}
admin_resp = requests.get("http://127.0.0.1:8000/admin/dashboard", headers=headers)

print(f"📡 Admin статус: {admin_resp.status_code}")
print(f"📦 Admin ответ: {admin_resp.text[:300]}")