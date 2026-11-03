from flask import Flask, render_template, request
from database import DBhandler

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


@app.route("/submit_item_post", methods=["POST"])
def reg_item_submit_post():
    name = request.form["name"].strip()

    if not name or any(c in name for c in ".#$[]/"):
        return render_template(
            "reg_items.html",
            error="상품명은 비워 둘 수 없고 . # $ [ ] / 는 쓸 수 없어요."
        )

    image_file = request.files["file_input"]
    image_file.save("static/images/{}".format(image_file.filename))
    
    data = request.form
    DB.insert_item(name, data, image_file.filename)

    return render_template("result.html", data=data,
                           img_path="static/images/{}".format(image_file.filename))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
