from flask import Flask, render_template, request
from database import DBhandler
import hashlib

app = Flask(__name__)
DB = DBhandler()


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
    image_file = request.files["file_input"]
    image_file.save("static/images/{}".format(image_file.filename))
    data = request.form
    return render_template("result.html", data=data,
                           img_path="static/images/{}".format(image_file.filename))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
