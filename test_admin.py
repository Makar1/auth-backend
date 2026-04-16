import requests

login_resp = requests.post(
    "http://127.0.0.1:8000/login",
    json={"email": "makar_new@example.com", "password": "super_secret_123"}
)
token = login_resp.json()["access_token"]
print(f"🎫 Токен получен: {token[:40]}...")


headers = {"Authorization": f"Bearer {token}"}
admin_resp = requests.get("http://127.0.0.1:8000/admin/dashboard", headers=headers)

print(f"\n📡 Статус: {admin_resp.status_code}")
print(f"📦 Ответ: {admin_resp.json()}")