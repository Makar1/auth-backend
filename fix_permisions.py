import requests

BASE = "http://127.0.0.1:8000"

# Логинимся как admin
resp = requests.post(f"{BASE}/login", json={
    "email": "admin@test.com",
    "password": "Admin1234"
})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Добавляем недостающие права
permissions_to_add = [
    {"role": "manager", "resource": "product", "action": "create"},
    {"role": "manager", "resource": "order",   "action": "create"},
]

for perm in permissions_to_add:
    r = requests.post(f"{BASE}/admin/permissions", json=perm, headers=headers)
    if r.status_code == 201:
        print(f"✅ Добавлено: {perm['role']} / {perm['resource']} / {perm['action']}")
    else:
        print(f"⚠️  {r.status_code}: {r.json()} — {perm}")