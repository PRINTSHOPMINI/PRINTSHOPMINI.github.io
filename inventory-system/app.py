"""
다점포 실시간 자동 재고관리 시스템 - Flask 백엔드
실행: python app.py  → http://localhost:5000
"""

import json
import os
from datetime import datetime

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from scraper import PrintnuriScraper

# ── Supabase 설정 ─────────────────────────────────────────────────────────────
SUPABASE_URL = "https://wbcfciiuiootbdezxfwy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndiY2ZjaWl1aW9vdGJkZXp4Znd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc1MjkyMTQsImV4cCI6MjA5MzEwNTIxNH0.UV4ukUXuAYKAqq85B4FTHO2BtIOqPaBHgAJN5lqyU5s"
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def fetch_product_sales(start_date: str, end_date: str) -> list:
    """Supabase product_sales 테이블에서 날짜 범위 데이터 조회"""
    url = (
        f"{SUPABASE_URL}/rest/v1/product_sales"
        f"?sale_date=gte.{start_date}&sale_date=lte.{end_date}"
        f"&select=sale_date,branch,product,quantity"
        f"&limit=50000"
    )
    resp = requests.get(url, headers=SUPABASE_HEADERS, timeout=30)
    if resp.status_code == 200:
        return resp.json()
    return []

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change-this-to-a-random-secret-key"
CORS(app)

DEFAULT_PRODUCTS: list[str] = ["제본", "코팅A4", "코팅A3", "L홀더", "서류봉투"]

DATA_FILE   = os.path.join(os.path.dirname(__file__), "data", "inventory.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "data", "config.json")

DEFAULT_BRANCHES: list[str] = [
    "서정리역점", "동탄호수점", "신영통점",   "동백역점",
    "수원시청역점", "기흥구청점", "망포역점", "권선점",
    "지점9",  "지점10", "지점11", "지점12",
    "지점13", "지점14", "지점15", "지점16",
]

scraper = PrintnuriScraper()


# ══════════════════════════════ 설정 (지점 목록) ═══════════════════════════════

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        cfg = {"branches": DEFAULT_BRANCHES, "products": DEFAULT_PRODUCTS}
        _save_config(cfg)
        return cfg
    cfg = json.load(open(CONFIG_FILE, "r", encoding="utf-8"))
    cfg.setdefault("branches", DEFAULT_BRANCHES)
    cfg.setdefault("products", DEFAULT_PRODUCTS)
    return cfg

def _save_config(cfg: dict) -> None:
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def get_branches() -> list[str]:
    return load_config().get("branches", DEFAULT_BRANCHES)

def get_products() -> list[str]:
    return load_config().get("products", DEFAULT_PRODUCTS)


# ══════════════════════════════ 재고 영속성 ════════════════════════════════════

def load_inventory() -> dict:
    branches = get_branches()
    if not os.path.exists(DATA_FILE):
        inv = {b: {p: {"initial_stock": 0, "sold": 0} for p in get_products()} for b in branches}
        _save_inventory(inv)
        return inv
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        inv = json.load(f)
    for b in branches:
        inv.setdefault(b, {})
        for p in get_products():
            inv[b].setdefault(p, {"initial_stock": 0, "sold": 0})
    return inv

def _save_inventory(inv: dict) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(inv, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════ 라우트 ════════════════════════════════════

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


# ── 설정 / 지점 목록 ──────────────────────────────────────────────────────────

@app.route("/api/config")
def get_config():
    return jsonify({"branches": get_branches(), "products": get_products()})


# ── 상품 관리 CRUD ─────────────────────────────────────────────────────────────

@app.route("/api/products/add", methods=["POST"])
def product_add():
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()
    if not name:
        return jsonify({"error": "상품명을 입력하세요"}), 400
    cfg = load_config()
    if name in cfg["products"]:
        return jsonify({"error": "이미 존재하는 상품명입니다"}), 400
    cfg["products"].append(name)
    _save_config(cfg)
    inv = load_inventory()
    for b in inv:
        inv[b].setdefault(name, {"initial_stock": 0, "sold": 0})
    _save_inventory(inv)
    return jsonify({"success": True, "products": cfg["products"]})


@app.route("/api/products/rename", methods=["POST"])
def product_rename():
    body     = request.get_json(force=True) or {}
    old_name = (body.get("old_name") or "").strip()
    new_name = (body.get("new_name") or "").strip()
    if not old_name or not new_name:
        return jsonify({"error": "상품명을 입력하세요"}), 400
    if old_name == new_name:
        return jsonify({"success": True, "products": get_products()})
    cfg = load_config()
    if old_name not in cfg["products"]:
        return jsonify({"error": "존재하지 않는 상품입니다"}), 400
    if new_name in cfg["products"]:
        return jsonify({"error": "이미 존재하는 상품명입니다"}), 400
    idx = cfg["products"].index(old_name)
    cfg["products"][idx] = new_name
    _save_config(cfg)
    inv = load_inventory()
    for b in inv:
        if old_name in inv[b]:
            inv[b][new_name] = inv[b].pop(old_name)
    _save_inventory(inv)
    return jsonify({"success": True, "products": cfg["products"]})


@app.route("/api/products/delete", methods=["POST"])
def product_delete():
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()
    cfg = load_config()
    if name not in cfg["products"]:
        return jsonify({"error": "존재하지 않는 상품입니다"}), 400
    cfg["products"].remove(name)
    _save_config(cfg)
    inv = load_inventory()
    for b in inv:
        inv[b].pop(name, None)
    _save_inventory(inv)
    return jsonify({"success": True, "products": cfg["products"]})


# ── 지점 관리 CRUD ─────────────────────────────────────────────────────────────

@app.route("/api/branches/add", methods=["POST"])
def branch_add():
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()
    if not name:
        return jsonify({"error": "지점명을 입력하세요"}), 400

    cfg = load_config()
    if name in cfg["branches"]:
        return jsonify({"error": "이미 존재하는 지점명입니다"}), 400

    cfg["branches"].append(name)
    _save_config(cfg)

    inv = load_inventory()
    inv[name] = {p: {"initial_stock": 0, "sold": 0} for p in get_products()}
    _save_inventory(inv)

    return jsonify({"success": True, "branches": cfg["branches"]})


@app.route("/api/branches/rename", methods=["POST"])
def branch_rename():
    body     = request.get_json(force=True) or {}
    old_name = (body.get("old_name") or "").strip()
    new_name = (body.get("new_name") or "").strip()

    if not old_name or not new_name:
        return jsonify({"error": "지점명을 입력하세요"}), 400
    if old_name == new_name:
        return jsonify({"success": True, "branches": get_branches()})

    cfg = load_config()
    if old_name not in cfg["branches"]:
        return jsonify({"error": "존재하지 않는 지점입니다"}), 400
    if new_name in cfg["branches"]:
        return jsonify({"error": "이미 존재하는 지점명입니다"}), 400

    idx = cfg["branches"].index(old_name)
    cfg["branches"][idx] = new_name
    _save_config(cfg)

    inv = load_inventory()
    if old_name in inv:
        inv[new_name] = inv.pop(old_name)
    _save_inventory(inv)

    return jsonify({"success": True, "branches": cfg["branches"]})


@app.route("/api/branches/delete", methods=["POST"])
def branch_delete():
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip()

    cfg = load_config()
    if name not in cfg["branches"]:
        return jsonify({"error": "존재하지 않는 지점입니다"}), 400

    cfg["branches"].remove(name)
    _save_config(cfg)

    inv = load_inventory()
    inv.pop(name, None)
    _save_inventory(inv)

    return jsonify({"success": True, "branches": cfg["branches"]})


# ── 인증 ──────────────────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    body = request.get_json(force=True) or {}
    ok, msg = scraper.login(body.get("username", ""), body.get("password", ""))
    return jsonify({"success": ok, "message": msg}), (200 if ok else 401)

@app.route("/api/auth/cookie", methods=["POST"])
def auth_cookie():
    body = request.get_json(force=True) or {}
    ok, msg = scraper.set_cookie(body.get("cookie", ""))
    return jsonify({"success": ok, "message": msg}), (200 if ok else 401)

@app.route("/api/auth/status")
def auth_status():
    return jsonify({"authenticated": scraper.is_authenticated})


# ── 동기화 ────────────────────────────────────────────────────────────────────

@app.route("/api/sync", methods=["POST"])
def sync_data():
    try:
        body = request.get_json(force=True) or {}
        start_date = body.get("start_date", "2026-02-01")
        end_date   = body.get("end_date", datetime.now().strftime("%Y-%m-%d"))

        sales = fetch_product_sales(start_date, end_date)
        if not isinstance(sales, list):
            return jsonify({"success": False, "message": "Supabase 조회 실패"}), 500

        branches = get_branches()
        inv = load_inventory()

        for b in branches:
            for p in get_products():
                inv[b][p]["sold"] = 0

        matched = 0
        for entry in sales:
            b = (entry.get("branch") or "").strip()
            p = (entry.get("product") or "").strip()
            q = int(entry.get("quantity") or 0)
            if b in branches and p in get_products() and q > 0:
                inv[b][p]["sold"] += q
                matched += 1

        _save_inventory(inv)
        return jsonify({
            "success": True,
            "message": f"{start_date} ~ {end_date} / {len(sales)}건 조회, {matched}건 매칭 완료",
            "total": len(sales), "matched": matched,
            "synced_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"동기화 오류: {e}"}), 500


# ── 재고 조회 / 수정 ──────────────────────────────────────────────────────────

@app.route("/api/inventory")
def get_inventory():
    inv    = load_inventory()
    branch = request.args.get("branch")
    if not branch:
        return jsonify(inv)
    if branch not in get_branches():
        return jsonify({"error": "존재하지 않는 지점입니다"}), 400
    rows = []
    for p in get_products():
        d = inv[branch][p]
        rows.append({
            "product": p, "initial_stock": d["initial_stock"],
            "sold": d["sold"], "remaining": d["initial_stock"] - d["sold"],
        })
    return jsonify(rows)

@app.route("/api/inventory/update", methods=["POST"])
def update_inventory():
    body = request.get_json(force=True) or {}
    branch  = body.get("branch", "")
    product = body.get("product", "")
    try:
        initial_stock = int(body.get("initial_stock", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "재고 수량은 정수여야 합니다"}), 400
    if branch not in get_branches():
        return jsonify({"error": "존재하지 않는 지점입니다"}), 400
    if product not in get_products():
        return jsonify({"error": "존재하지 않는 상품입니다"}), 400
    inv = load_inventory()
    inv[branch][product]["initial_stock"] = initial_stock
    _save_inventory(inv)
    return jsonify({"success": True, "remaining": initial_stock - inv[branch][product]["sold"]})


# ── 대시보드 ──────────────────────────────────────────────────────────────────

@app.route("/api/dashboard")
def get_dashboard():
    branches = get_branches()
    inv = load_inventory()
    branches_data, grand_initial, grand_sold, grand_remaining = [], 0, 0, 0
    for b in branches:
        b_initial   = sum(inv[b][p]["initial_stock"] for p in get_products())
        b_sold      = sum(inv[b][p]["sold"]          for p in get_products())
        b_remaining = b_initial - b_sold
        grand_initial += b_initial; grand_sold += b_sold; grand_remaining += b_remaining
        branches_data.append({
            "branch": b, "total_initial": b_initial,
            "total_sold": b_sold, "total_remaining": b_remaining,
            "products": [{"product": p, "initial_stock": inv[b][p]["initial_stock"],
                          "sold": inv[b][p]["sold"],
                          "remaining": inv[b][p]["initial_stock"] - inv[b][p]["sold"]}
                         for p in get_products()],
        })
    return jsonify({"branches": branches_data, "grand_initial": grand_initial,
                    "grand_sold": grand_sold, "grand_remaining": grand_remaining,
                    "synced_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


if __name__ == "__main__":
    print("=" * 55)
    print(" 다점포 실시간 재고관리 시스템")
    print(" http://localhost:5000  으로 접속하세요")
    print("=" * 55)
    app.run(debug=True, port=5000, host="0.0.0.0")
