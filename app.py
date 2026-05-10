import json
from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

def safe_get_likes(post):
    return post.get("likes", 0)

def load_posts():
    try:
        with open("posts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_posts(posts):
    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

posts = load_posts()

@app.route("/")
def home():
    keyword = request.args.get("keyword", "")
    category = request.args.get("category", "")

    filtered_posts = []

    for post in posts:

        keyword_match = (
            keyword == "" or
            keyword in post["title"] or
            keyword in post["material"]
        )

        category_match = (
            category == "" or
            post["category"] == category
        )

        if keyword_match and category_match:
            filtered_posts.append(post)

    filtered_posts = sorted(
        filtered_posts,
        key=lambda post: post.get("likes", 0),
        reverse=True
    )

    popular_posts = sorted(
    posts,
    key=lambda post: post.get("likes", 0),
    reverse=True
)[:3]

    return render_template(
    "index.html",
    posts=filtered_posts,
    popular_posts=popular_posts
)


@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    material = request.form["material"]
    price = request.form["price"]
    category = request.form["category"]
    image = request.files["image"]
    filename = image.filename
    image.save(os.path.join("static/uploads", filename))
    steps = request.form.get("steps", "")

    posts.append({
        "title": title,
        "material": material,
        "price": price,
        "category": category,
        "likes": 0,
        "image": filename,
        "steps": steps,
        
    })

    save_posts(posts)

    return redirect("/")

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    post = posts[index]

    # 画像削除
    image_path = os.path.join("static/uploads", post["image"])
    if os.path.exists(image_path):
        os.remove(image_path)

    # 投稿削除
    posts.pop(index)
    save_posts(posts)

    return redirect("/")

@app.route("/like/<int:index>", methods=["POST"])
def like(index):
    posts[index]["likes"] += 1
    save_posts(posts)
    return redirect("/")

@app.route("/edit/<int:index>")
def edit(index):
    post = posts[index]
    return render_template("edit.html", post=post, index=index)

@app.route("/update/<int:index>", methods=["POST"])
def update(index):
    posts[index]["title"] = request.form["title"]
    posts[index]["material"] = request.form["material"]
    posts[index]["price"] = request.form["price"]

    save_posts(posts)
    return redirect("/")

@app.route("/detail/<int:index>")
def detail(index):
    post = posts[index]
    return render_template("detail.html", post=post)

if __name__ == "__main__":
    app.run(debug=True)