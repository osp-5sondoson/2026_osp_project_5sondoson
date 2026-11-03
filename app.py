from flask import Flask, render_template, request
from database import DBhandler
import hashlib
import os
import uuid

app = Flask(__name__)
DB = DBhandler()

UPLOAD_DIR = os.path.join(app.root_path, "static", "images")
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
ITEM_FIELDS = ["name", "seller", "email", "price", "addr", "status"]
ITEM_STATUSES = {"selling", "reserved", "sold"}
FORBIDDEN_KEY_CHARS = ".#$[]/"


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/list")
def view_list():
    return render_template("list.html")


@app.route("/review")
def view_review():
    return render_template("review.html")


@app.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")


@app.route("/reg_reviews")
def reg_review():
    return render_template("reg_reviews.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signup_post", methods=["POST"])
def register_user():
    data = request.form
    pw = request.form["pw"]
    pw_hash = hashlib.sha256(pw.encode("utf-8")).hexdigest()
    if DB.insert_user(data, pw_hash):
        return render_template("login.html")
    else:
        return render_template("signup.html", error="이미 존재하는 아이디입니다.")


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
