from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import DBhandler
from datetime import date, datetime
import hashlib
import os
import random
import re
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # 업로드 사진 한 장당 5MB까지
DB = DBhandler()

UPLOAD_DIR = os.path.join(app.root_path, "static", "images")
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
# 등록 폼에서 받는 필수 항목 (판매자 ID·이메일은 로그인한 계정에서 가져오고, 설명은 선택)
ITEM_FIELDS = ["name", "category", "price", "original_price", "addr", "expire", "status"]
ITEM_STATUSES = {"selling", "reserved", "sold"}
FORBIDDEN_KEY_CHARS = ".#$[]/"
USER_ID_PATTERN = re.compile(r"[A-Za-z0-9]{4,20}")
MIN_PW_LENGTH = 8                                   # 회원가입 폼 안내와 동일: 영문·숫자 포함 8자 이상
EMAIL_DOMAINS = {"ewha.ac.kr", "ewhain.net"}        # 학교 이메일만 가입 가능
EMAIL_ID_PATTERN = re.compile(r"[A-Za-z0-9._-]{1,64}")
SCHOOL_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._-]{1,64}@(ewha\.ac\.kr|ewhain\.net)")
PHONE_PATTERN = re.compile(r"01[016789][ -]?\d{3,4}[ -]?\d{4}")


CATEGORIES = ["카페·베이커리", "치킨·피자·버거", "외식", "편의점", "영화·문화", "상품권", "기타"]

ITEMS_PER_PAGE = 12
LIST_SORTS = {"latest": "최신 등록순", "deadline": "마감 임박순", "price": "가격 낮은순"}
DEFAULT_ITEM_IMAGE = "americano_gifticon.png"   # img_path가 비어 있는 상품에 보여 줄 사진


def to_int(value, default=0):
    """DB에 문자열로 저장된 숫자("3500", "3,500")를 int로. 못 바꾸면 default"""
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def days_until(expire):
    """유효기간 문자열("2026-12-31" 또는 "2026.12.31")까지 남은 날. 없거나 형식이 다르면 None"""
    if not expire:
        return None
    try:
        return (date.fromisoformat(str(expire).replace(".", "-")[:10]) - date.today()).days
    except ValueError:
        return None


def normalize_item(name, data):
    """DB의 상품 한 건 {seller, price, ...}를 화면(목록·상세·특별페이지)이 쓰는 dict로 바꾼다.

    DB에는 seller · price · addr · status · email · img_path(실습 기본)에
    original_price · category · expire · desc · created_at(등록 폼 추가분)이 있고,
    값이 없는 상품은 기본값을 채운다. brand · rating은 아직 DB에 없다.
    """
    price = to_int(data.get("price"))
    original_price = to_int(data.get("original_price"), price)
    if original_price < price:
        original_price = price
    status = data.get("status", "selling")
    if status not in ITEM_STATUSES:
        status = "selling"
    dday = days_until(data.get("expire"))
    rating = data.get("rating")
    try:
        rating = float(rating) if rating not in (None, "") else None
    except (TypeError, ValueError):
        rating = None
    return {
        "name": name,
        "brand": data.get("brand", ""),
        "category": data.get("category") if data.get("category") in CATEGORIES else "기타",
        "price": price,
        "original_price": original_price,
        "discount": round((1 - price / original_price) * 100) if original_price else 0,
        "seller": data.get("seller", ""),
        "email": data.get("email", ""),
        "addr": data.get("addr", ""),
        "rating": rating,
        "dday": dday,            # 유효기간 정보가 없으면 None → D-day 표시 안 함, 음수면 만료
        "expire": data.get("expire", ""),
        "desc": data.get("desc", ""),
        "created_at": data.get("created_at", ""),   # 없으면 "" → 최신순에서 맨 뒤
        "status": status,
        "img": data.get("img_path") or DEFAULT_ITEM_IMAGE,
    }


def load_items():
    """DB.get_items()의 {상품명: {...}}를 목록 화면이 쓰는 dict 리스트로 바꾼다 (최신 등록순)"""
    items = [normalize_item(name, data) for name, data in DB.get_items().items() if isinstance(data, dict)]
    # 기본 정렬: 최신 등록순. 등록 시각이 없는 예전 상품은 뒤로 가고, 그 안에서는 이름순
    items.sort(key=lambda i: i["name"])
    items.sort(key=lambda i: i["created_at"], reverse=True)
    return items
# 특별페이지 예산 구간: (키, 표시 이름, 최소 이상, 최대 미만)
BUDGETS = [
    ("all", "전체", 0, None),
    ("u5", "5,000원 미만", 0, 5000),
    ("5-10", "5,000 ~ 10,000원 미만", 5000, 10000),
    ("10-20", "10,000 ~ 20,000원 미만", 10000, 20000),
    ("20-30", "20,000 ~ 30,000원 미만", 20000, 30000),
]


@app.route("/")
def hello():
    return redirect(url_for("view_list"))


@app.route("/list")
def view_list():
    category = request.args.get("category", "")
    sort = request.args.get("sort", "latest")
    selling_only = request.args.get("selling") == "1"
    query = request.args.get("q", "").strip()
    if category not in CATEGORIES:
        category = ""
    if sort not in LIST_SORTS:
        sort = "latest"

    all_items = load_items()
    items = all_items
    if category:
        items = [i for i in items if i["category"] == category]
    if selling_only:
        items = [i for i in items if i["status"] == "selling"]
    if query:
        items = [i for i in items if query.lower() in (i["brand"] + " " + i["name"]).lower()]
    if sort == "deadline":
        # 유효기간이 없는 상품은 맨 뒤로
        items = sorted(items, key=lambda i: (i["dday"] is None, i["dday"] or 0))
    elif sort == "price":
        items = sorted(items, key=lambda i: i["price"])

    total = len(items)
    page_count = max(1, -(-total // ITEMS_PER_PAGE))
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    page = min(max(page, 1), page_count)
    start = (page - 1) * ITEMS_PER_PAGE

    # 마감 임박 특가: 유효기간 3일 이내 · 판매중 (이미 지난 상품은 제외)
    deals = sorted((i for i in all_items if i["dday"] is not None and 0 <= i["dday"] <= 3 and i["status"] == "selling"),
                   key=lambda i: i["dday"])
    stats = {
        "count": len(all_items),
        "discount": round(sum(i["discount"] for i in all_items) / len(all_items)) if all_items else 0,
        "closing": sum(1 for i in all_items if i["dday"] is not None and 0 <= i["dday"] <= 1 and i["status"] == "selling"),
    }
    return render_template(
        "list.html", items=items[start:start + ITEMS_PER_PAGE], total=total, page=page, page_count=page_count,
        categories=CATEGORIES, sorts=LIST_SORTS, deals=deals[:3], stats=stats,
        category=category, sort=sort, selling_only=selling_only, query=query,
    )


def special_context():
    """특별페이지(오늘 뭐 먹지?) 전·후 화면이 같이 쓰는 조건·후보 목록"""
    budget_key = request.args.get("budget", "u5")
    budget = next((b for b in BUDGETS if b[0] == budget_key), BUDGETS[1])
    category = request.args.get("category", "")
    if category not in CATEGORIES:
        category = ""
    # 판매 중이고 유효기간이 지나지 않은 DB 상품 중에서 고른다 (유효기간 정보가 없는 상품도 포함)
    candidates = [
        i for i in load_items()
        if i["status"] == "selling"
        and (i["dday"] is None or i["dday"] >= 0)
        and i["price"] >= budget[2]
        and (budget[3] is None or i["price"] < budget[3])
        and (not category or i["category"] == category)
    ]
    return {
        "budgets": BUDGETS, "budget": budget, "categories": CATEGORIES[:-1],
        "category": category, "candidates": candidates,
    }


@app.route("/today")
def view_special():
    return render_template("special.html", **special_context())


@app.route("/today/result")
def view_special_result():
    context = special_context()
    if not context["candidates"]:
        return render_template("special.html", **context)
    pick = random.choice(context["candidates"])
    budget_max = context["budget"][3]
    spare = budget_max - pick["price"] if budget_max else None
    return render_template("special_result.html", pick=pick, spare=spare, **context)


@app.route("/review")
def view_review():
    return render_template("review.html")


@app.route("/seller_reviews/<seller>")
def view_seller_reviews(seller):
    return render_template("seller_reviews.html", seller=seller)


@app.route("/review_detail/<int:review_id>")
def view_review_detail(review_id):
    return render_template("review_detail.html", review_id=review_id)


@app.route("/reg_items")
def reg_item():
    # 판매자 ID·이메일은 로그인한 계정에서 가져오므로 로그인이 필요
    if not session.get("id"):
        flash("기프티콘을 판매하려면 로그인해 주세요.")
        return redirect(url_for("login"))
    user = DB.get_user(session["id"]) or {}
    return render_template("reg_items.html", categories=CATEGORIES,
                           seller=session["id"], seller_email=user.get("email", ""))


@app.route("/view_detail/<name>")
def view_item_detail(name):
    raw = DB.get_item_byname(str(name))
    if not isinstance(raw, dict):
        flash("존재하지 않는 상품이에요.")
        return redirect(url_for("view_list"))
    # 목록과 같은 규칙으로 정리한 값(숫자 가격·원가·할인율·D-day·기본 사진)을 DB 원본 위에 덮어 쓴다
    item = normalize_item(name, raw)
    data = {**raw, **item, "img_path": item["img"], "seller_rating": item["rating"]}
    # 판매자 리뷰는 이번 과제 범위가 아니라 샘플 그대로 둠 (리뷰 백엔드 때 교체)
    reviews = [
        {"rating": 4.0, "title": "바코드도 잘 찍히고 바로 사용했어요!",
         "body": "바코드가 바로 인식돼서 매장에서 문제없이 결제했어요. 유효기간도 설명대로 넉넉했어요.",
         "author": "ewha_park", "item": "메가커피 아이스 아메리카노", "date": "2026.09.28"},
        {"rating": 5.0, "title": "구매하자마자 바로 쓸 수 있었어요",
         "body": "구매하기 누르자마자 기프티콘함에 원본이 떠서 바로 사용했어요. 설명이랑 똑같았어요.",
         "author": "ewha_lee", "item": "스타벅스 카페라떼 T", "date": "2026.10.03"},
    ]
    return render_template("item_detail.html", name=name, data=data, reviews=reviews)


@app.route("/reg_reviews")
def reg_review():
    return render_template("reg_reviews.html")


# 내 기프티콘함(특별페이지) 샘플 데이터: 로그인한 구매자가 산 기프티콘
MY_GIFTICONS = [
    {"id": 1, "brand": "스타벅스", "name": "아이스 카페 아메리카노 T 2잔", "dday": 3, "used": False,
     "img": "sample_starbucks_americano.jpg", "number": "9120 4471 0385 2216",
     "expire": "2026.10.09까지", "seller": "ewha_kim", "bought": "2026.10.02",
     "paid": 7300, "original_price": 9400},
    {"id": 2, "brand": "BBQ", "name": "황금올리브치킨순살+콜라1.25L", "dday": 128, "used": False,
     "img": "sample_bbq_chicken.jpg", "number": "5837 2069 4412 7750",
     "expire": "2027.02.11까지", "seller": "pear_blossom", "bought": "2026.10.04",
     "paid": 22500, "original_price": 27500},
    {"id": 3, "brand": "CU", "name": "모바일 상품권 5,000원", "dday": None, "used": True,
     "img": "sample_cu_voucher.jpg", "number": "3306 9184 6627 0943",
     "expire": "2026.10.01 사용", "seller": "ewha23", "bought": "2026.09.28",
     "paid": 4500, "original_price": 5000},
]
MY_TABS = {"all": "전체", "usable": "사용 가능", "used": "사용 완료"}


def barcode_bars(number):
    """기프티콘 번호로 바코드 막대 굵기(2~5px) 46개를 만든다. 같은 번호면 항상 같은 모양."""
    seed = int(number.replace(" ", "")) % 233280
    bars = []
    for _ in range(46):
        seed = (seed * 9301 + 49297) % 233280
        bars.append(2 + seed * 4 // 233280)
    return bars


def subject_particle(word):
    """한글 받침에 맞는 주격 조사('이' 또는 '가')를 고른다. 한글로 끝나지 않으면 '이(가)'."""
    last = word[-1]
    if not "가" <= last <= "힣":
        return "이(가)"
    return "이" if (ord(last) - ord("가")) % 28 else "가"


@app.route("/my_gifticons")
def view_my_gifticons():
    tab = request.args.get("tab", "all")
    if tab not in MY_TABS:
        tab = "all"
    owned = [
        dict(g, bars=barcode_bars(g["number"]), particle=subject_particle(g["name"]))
        for g in MY_GIFTICONS
    ]
    usable = [g for g in owned if not g["used"]]
    used = [g for g in owned if g["used"]]
    # 유효기간 임박순: 사용 가능한 것이 먼저, 그 안에서는 남은 날이 적은 순
    cards = {"all": usable + used, "usable": usable, "used": used}[tab]
    cards = sorted(cards, key=lambda g: (g["used"], g["dday"] or 0))
    closing = [g for g in usable if g["dday"] <= 3]
    summary = {
        "usable": len(usable), "closing": closing, "used": used,
        "saved": sum(g["original_price"] - g["paid"] for g in owned),
    }
    history = sorted(owned, key=lambda g: g["bought"], reverse=True)
    counts = {"all": len(owned), "usable": len(usable), "used": len(used)}
    return render_template(
        "my_gifticons.html", cards=cards, tab=tab, tabs=MY_TABS, counts=counts,
        summary=summary, history=history,
    )


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/home")
def home_logged_in():
    if not session.get("id"):
        return redirect(url_for("login"))
    return render_template("home_logged_in.html")

@app.route("/login_confirm", methods=["POST"])
def login_confirm():
    id_ = request.form.get("id", "").strip()
    pw = request.form.get("pw", "")

    pw_hash = hashlib.sha256(
        pw.encode("utf-8")
    ).hexdigest()

    if DB.find_user(id_, pw_hash):
        session["id"] = id_
        return redirect(url_for("home_logged_in"))

    flash("Wrong ID or PW!")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("view_list"))


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signup_post", methods=["POST"])
def register_user():
    # 회원가입 폼 필드: id · pw · pw_confirm · email_id · email_domain · phone(선택)
    data = {
        "id": request.form.get("id", "").strip(),
        "email_id": request.form.get("email_id", "").strip(),
        "email_domain": request.form.get("email_domain", "").strip().lstrip("@"),
        "phone": request.form.get("phone", "").strip(),
    }
    pw = request.form.get("pw", "")
    pw_confirm = request.form.get("pw_confirm", "")

    error = None
    if not data["id"] or not pw or not pw_confirm or not data["email_id"]:
        error = "아이디, 비밀번호, 비밀번호 확인, 학교 이메일을 모두 입력해 주세요."
    elif not USER_ID_PATTERN.fullmatch(data["id"]):
        error = "아이디는 영문과 숫자로 4~20자까지 쓸 수 있어요."
    elif len(pw) < MIN_PW_LENGTH or not re.search(r"[A-Za-z]", pw) or not re.search(r"[0-9]", pw):
        error = "비밀번호는 영문과 숫자를 포함해 {}자 이상으로 입력해 주세요.".format(MIN_PW_LENGTH)
    elif pw != pw_confirm:
        error = "비밀번호가 일치하지 않아요."
    elif data["email_domain"] not in EMAIL_DOMAINS or not EMAIL_ID_PATTERN.fullmatch(data["email_id"]):
        error = "학교 이메일(@ewha.ac.kr 또는 @ewhain.net)을 확인해 주세요."
    elif data["phone"] and not PHONE_PATTERN.fullmatch(data["phone"]):
        error = "전화번호는 010 0000 0000 형식으로 입력해 주세요."
    if error:
        return render_template("signup.html", error=error, form=data)

    pw_hash = hashlib.sha256(pw.encode("utf-8")).hexdigest()
    if DB.insert_user(data, pw_hash):
        # Redirect so refreshing the next page does not resubmit the sign-up form
        flash("회원가입이 완료되었어요. 로그인해 주세요.")
        return redirect(url_for("login"))
    else:
        return render_template("signup.html", error="이미 존재하는 아이디입니다.", form=data)


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


@app.errorhandler(413)
def upload_too_large(_error):
    flash("사진은 한 장당 5MB까지 올릴 수 있어요.")
    return redirect(url_for("reg_item"))


@app.route("/submit_item_post", methods=["POST"])
def reg_item_submit_post():
    if not session.get("id"):
        flash("기프티콘을 판매하려면 로그인해 주세요.")
        return redirect(url_for("login"))

    data = {field: request.form.get(field, "").strip() for field in ITEM_FIELDS}
    data["desc"] = request.form.get("desc", "").strip()
    # 판매자 ID는 폼 값이 아니라 로그인한 계정 (남의 아이디로 등록 방지).
    # 이메일도 계정에 있으면 그 값을 쓰고, 이메일 없이 가입한 예전 계정만 폼에서 받는다
    user = DB.get_user(session["id"]) or {}
    data["seller"] = session["id"]
    data["email"] = user.get("email") or request.form.get("email", "").strip()
    image_file = request.files.get("file_input")
    ext = os.path.splitext(image_file.filename)[1].lower() if image_file else ""

    error = None
    if not all(data[field] for field in ITEM_FIELDS) or not data["email"]:
        error = "모든 항목을 입력해 주세요."
    elif not SCHOOL_EMAIL_PATTERN.fullmatch(data["email"]):
        error = "이메일은 학교 이메일(@ewha.ac.kr 또는 @ewhain.net)로 입력해 주세요."
    elif any(c in data["name"] for c in FORBIDDEN_KEY_CHARS):
        error = "상품명에는 . # $ [ ] / 를 쓸 수 없어요."
    elif data["category"] not in CATEGORIES:
        error = "카테고리를 다시 선택해 주세요."
    elif not data["price"].isdigit() or not data["original_price"].isdigit():
        error = "판매가와 원가는 0 이상의 숫자로 입력해 주세요."
    elif int(data["price"]) > int(data["original_price"]):
        error = "판매가는 원가보다 높을 수 없어요."
    elif days_until(data["expire"]) is None:
        error = "유효기간을 다시 선택해 주세요."
    elif days_until(data["expire"]) < 0:
        error = "유효기간이 이미 지난 기프티콘은 등록할 수 없어요."
    elif data["status"] not in ITEM_STATUSES:
        error = "상태를 다시 선택해 주세요."
    elif not image_file or not image_file.filename:
        error = "사진을 올려 주세요."
    elif ext not in ALLOWED_IMAGE_EXTS:
        error = "사진은 png, jpg, jpeg, gif, webp 파일만 올릴 수 있어요."
    elif DB.item_exists(data["name"]):
        error = "이미 등록된 상품명이에요. 다른 이름으로 등록해 주세요."
    if error:
        return render_template("reg_items.html", error=error, form=data, categories=CATEGORIES,
                               seller=data["seller"], seller_email=data["email"])

    # Save under a random name so uploads never overwrite each other or escape the folder
    filename = uuid.uuid4().hex + ext
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    image_file.save(os.path.join(UPLOAD_DIR, filename))

    DB.insert_item(data["name"], data, filename)

    # 등록 결과 표 대신 방금 올린 상품 상세로 이동 (새로고침해도 다시 등록되지 않음)
    flash("기프티콘이 등록되었어요.")
    return redirect(url_for("view_item_detail", name=data["name"]))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
