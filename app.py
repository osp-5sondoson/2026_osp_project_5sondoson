from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import DBhandler
import hashlib
import os
import random
import re
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
DB = DBhandler()

UPLOAD_DIR = os.path.join(app.root_path, "static", "images")
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
ITEM_FIELDS = ["name", "seller", "email", "price", "addr", "status"]
ITEM_STATUSES = {"selling", "reserved", "sold"}
FORBIDDEN_KEY_CHARS = ".#$[]/"
USER_ID_PATTERN = re.compile(r"[A-Za-z0-9]{4,20}")
MIN_PW_LENGTH = 4


# ---------- 화면 구현 단계용 샘플 상품 ----------
# TODO: 백엔드 단계에서 DB.get_items()로 교체
CATEGORIES = ["카페·베이커리", "치킨·피자·버거", "외식", "편의점", "영화·문화", "상품권", "기타"]
SAMPLE_ITEMS = [
    {"brand": "스타벅스", "name": "아이스 카페 아메리카노 T", "category": "카페·베이커리", "price": 3500, "original_price": 4500,
     "seller": "ewha_kim", "rating": 4.8, "dday": 3, "status": "selling", "addr": "전국 스타벅스 매장", "img": "sample_starbucks_americano.jpg"},
    {"brand": "CU", "name": "모바일 상품권 5,000원", "category": "편의점", "price": 4500, "original_price": 5000,
     "seller": "ewha23", "rating": 4.6, "dday": 327, "status": "selling", "addr": "전국 CU 편의점", "img": "sample_cu_voucher.jpg"},
    {"brand": "BBQ", "name": "황금올리브치킨순살+콜라1.25L", "category": "치킨·피자·버거", "price": 22500, "original_price": 27500,
     "seller": "pear_blossom", "rating": 4.9, "dday": 7, "status": "reserved", "addr": "전국 BBQ 매장", "img": "sample_bbq_chicken.jpg"},
    {"brand": "투썸플레이스", "name": "생딸기 생크림 케이크", "category": "카페·베이커리", "price": 29700, "original_price": 35000,
     "seller": "sweet_ewha", "rating": 4.7, "dday": 45, "status": "selling", "addr": "전국 투썸플레이스 매장", "img": "sample_twosome_cake.jpg"},
    {"brand": "던킨", "name": "먼치킨 10개입 2ea", "category": "카페·베이커리", "price": 9000, "original_price": 12000,
     "seller": "donut_lover", "rating": 4.5, "dday": 1, "status": "selling", "addr": "전국 던킨 매장", "img": "sample_dunkin_munchkin.jpg"},
    {"brand": "공차", "name": "블랙 밀크티 J", "category": "카페·베이커리", "price": 4500, "original_price": 5700,
     "seller": "tea_time", "rating": 4.8, "dday": 30, "status": "sold", "addr": "전국 공차 매장", "img": "sample_gongcha_milktea.jpg"},
    {"brand": "맘스터치", "name": "휠렛버거 세트", "category": "치킨·피자·버거", "price": 6600, "original_price": 7500,
     "seller": "mom_touch", "rating": 4.3, "dday": 88, "status": "selling", "addr": "전국 맘스터치 매장", "img": "sample_momstouch_burger.jpg"},
    {"brand": "배스킨라빈스", "name": "쿼터 아이스크림", "category": "카페·베이커리", "price": 15300, "original_price": 18500,
     "seller": "ice_ewha", "rating": 5.0, "dday": 152, "status": "reserved", "addr": "전국 배스킨라빈스 매장", "img": "sample_baskin_quarter.jpg"},
    {"brand": "이디야커피", "name": "시그니처라떼 ICED (L)", "category": "카페·베이커리", "price": 3300, "original_price": 4700,
     "seller": "latte_ewha", "rating": 4.7, "dday": 2, "status": "selling", "addr": "전국 이디야커피 매장", "img": "sample_ediya_latte.jpg"},
    {"brand": "이마트24", "name": "모바일 금액권 1만원권", "category": "상품권", "price": 9200, "original_price": 10000,
     "seller": "cu_holic", "rating": 4.4, "dday": 210, "status": "selling", "addr": "전국 이마트24 편의점", "img": "sample_emart24_voucher.jpg"},
    {"brand": "교촌치킨", "name": "반반콤보", "category": "치킨·피자·버거", "price": 19500, "original_price": 23000,
     "seller": "chicken_day", "rating": 4.9, "dday": 19, "status": "reserved", "addr": "전국 교촌치킨 매장", "img": "sample_kyochon_combo.jpg"},
    {"brand": "파리바게뜨", "name": "시즌과일 우유 생크림 케이크 1호", "category": "카페·베이커리", "price": 27500, "original_price": 32000,
     "seller": "cake_ewha", "rating": 4.6, "dday": 63, "status": "selling", "addr": "전국 파리바게뜨 매장", "img": "sample_paris_cake.jpg"},
]
for _item in SAMPLE_ITEMS:
    _item["discount"] = round((1 - _item["price"] / _item["original_price"]) * 100)

ITEMS_PER_PAGE = 12
LIST_SORTS = {"latest": "최신 등록순", "deadline": "마감 임박순", "price": "가격 낮은순"}
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

    items = SAMPLE_ITEMS
    if category:
        items = [i for i in items if i["category"] == category]
    if selling_only:
        items = [i for i in items if i["status"] == "selling"]
    if query:
        items = [i for i in items if query.lower() in (i["brand"] + " " + i["name"]).lower()]
    if sort == "deadline":
        items = sorted(items, key=lambda i: i["dday"])
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

    # 마감 임박 특가: 유효기간 3일 이내 · 판매중
    deals = sorted((i for i in SAMPLE_ITEMS if i["dday"] <= 3 and i["status"] == "selling"), key=lambda i: i["dday"])
    stats = {
        "count": len(SAMPLE_ITEMS),
        "discount": round(sum(i["discount"] for i in SAMPLE_ITEMS) / len(SAMPLE_ITEMS)),
        "closing": sum(1 for i in SAMPLE_ITEMS if i["dday"] <= 1 and i["status"] == "selling"),
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
    candidates = [
        i for i in SAMPLE_ITEMS
        if i["status"] == "selling"
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
    return render_template("reg_items.html")


@app.route("/view_detail/<name>")
def view_item_detail(name):
    data = DB.get_item_byname(str(name))
    if not data:
        flash("존재하지 않는 상품이에요.")
        return redirect(url_for("view_list"))
    # DB에 없는 값(브랜드·카테고리·원가·D-day·평점)은 상품명이 같은 샘플이 있을 때만 채움
    # 상품명이 "아이스 카페 아메리카노 T"든 "스타벅스 아이스 카페 아메리카노 T"든 같은 샘플로 찾음
    sample = next((i for i in SAMPLE_ITEMS
                   if name in (i["name"], i["brand"] + " " + i["name"])), None)
    if sample:
        extra = {"brand": sample["brand"], "category": sample["category"],
                 "original_price": sample["original_price"], "dday": sample["dday"],
                 "seller_rating": sample["rating"]}
        data = {**extra, **data}
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

@app.route("/login_confirm", methods=["POST"])
def login_confirm():
    id_ = request.form.get("id", "").strip()
    pw = request.form.get("pw", "")

    pw_hash = hashlib.sha256(
        pw.encode("utf-8")
    ).hexdigest()

    if DB.find_user(id_, pw_hash):
        session["id"] = id_
        return redirect(url_for("view_list"))

    flash("Wrong ID or PW!")
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signup_post", methods=["POST"])
def register_user():
    data = {
        "id": request.form.get("id", "").strip(),
        "nickname": request.form.get("nickname", "").strip()
    }
    pw = request.form.get("pw", "")

    error = None
    if not data["id"] or not data["nickname"] or not pw:
        error = "아이디, 비밀번호, 닉네임을 모두 입력해 주세요."
    elif not USER_ID_PATTERN.fullmatch(data["id"]):
        error = "아이디는 영문과 숫자로 4~20자까지 쓸 수 있어요."
    elif len(pw) < MIN_PW_LENGTH:
        error = "비밀번호는 {}자 이상으로 입력해 주세요.".format(MIN_PW_LENGTH)
    if error:
        return render_template("signup.html", error=error, form=data)

    pw_hash = hashlib.sha256(pw.encode("utf-8")).hexdigest()
    if DB.insert_user(data, pw_hash):
        # Redirect so refreshing the next page does not resubmit the sign-up form
        flash("회원가입이 완료되었어요. 로그인해 주세요.")
        return redirect(url_for("login"))
    else:
        return render_template("signup.html", error="이미 존재하는 아이디입니다.", form=data)


@app.route("/submit_item_post", methods=["POST"])
def reg_item_submit_post():
    data = {field: request.form.get(field, "").strip() for field in ITEM_FIELDS}
    image_file = request.files.get("file_input")
    ext = os.path.splitext(image_file.filename)[1].lower() if image_file else ""

    error = None
    if not all(data.values()):
        error = "모든 항목을 입력해 주세요."
    elif any(c in data["name"] for c in FORBIDDEN_KEY_CHARS):
        error = "상품명에는 . # $ [ ] / 를 쓸 수 없어요."
    elif not data["price"].isdigit():
        error = "판매가는 0 이상의 숫자로 입력해 주세요."
    elif data["status"] not in ITEM_STATUSES:
        error = "상태를 다시 선택해 주세요."
    elif not image_file or not image_file.filename:
        error = "사진을 올려 주세요."
    elif ext not in ALLOWED_IMAGE_EXTS:
        error = "사진은 png, jpg, jpeg, gif, webp 파일만 올릴 수 있어요."
    elif DB.item_exists(data["name"]):
        error = "이미 등록된 상품명이에요. 다른 이름으로 등록해 주세요."
    if error:
        return render_template("reg_items.html", error=error, form=data)

    # Save under a random name so uploads never overwrite each other or escape the folder
    filename = uuid.uuid4().hex + ext
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    image_file.save(os.path.join(UPLOAD_DIR, filename))

    DB.insert_item(data["name"], data, filename)

    return render_template("result.html", data=data,
                           img_path="static/images/{}".format(filename))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
