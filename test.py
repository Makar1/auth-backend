import requests

BASE = "http://127.0.0.1:8000"


def login(email, password):
    resp = requests.post(f"{BASE}/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        print(f"  ❌ Логин не удался для {email}: {resp.json()}")
        return None
    return resp.json()["access_token"]


def test(label, method, url, token=None, expected=200):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = getattr(requests, method)(f"{BASE}{url}", headers=headers)
    ok = resp.status_code == expected
    icon = "✅" if ok else "❌"
    print(f"  {icon} [{resp.status_code}] {method.upper()} {url} — {label}")


print("\n=== БЕЗ ТОКЕНА ===")
test("нет токена → 401", "get", "/products", expected=401)
test("нет токена → 401", "get", "/orders",   expected=401)

print("\n=== РОЛЬ: user ===")
token_user = login("viewer@test.com", "Viewer1234")
if token_user:
    test("product:read — есть",   "get",  "/products",          token_user, expected=200)
    test("product:create — нет",  "post", "/products",          token_user, expected=403)
    test("order:read — нет",      "get",  "/orders",            token_user, expected=403)
    test("admin панель — нет",    "get",  "/admin/dashboard",   token_user, expected=403)

print("\n=== РОЛЬ: manager ===")
token_manager = login("manager@test.com", "Manager1234")
if token_manager:
    test("product:read — есть",   "get",  "/products",          token_manager, expected=200)
    test("product:create — есть", "post", "/products",          token_manager, expected=200)
    test("order:read — есть",     "get",  "/orders",            token_manager, expected=200)
    test("order:create — есть",   "post", "/orders",            token_manager, expected=200)
    test("admin панель — нет",    "get",  "/admin/dashboard",   token_manager, expected=403)

print("\n=== РОЛЬ: admin ===")
token_admin = login("admin@test.com", "Admin1234")
if token_admin:
    test("product:read — есть",   "get",  "/products",          token_admin, expected=200)
    test("order:read — есть",     "get",  "/orders",            token_admin, expected=200)
    test("admin панель — есть",   "get",  "/admin/dashboard",   token_admin, expected=200)
    test("список прав — есть",    "get",  "/admin/permissions", token_admin, expected=200)
    test("список ролей — есть",   "get",  "/admin/roles",       token_admin, expected=200)