import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os, random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecret"

DB_FILE = "user.db"

def init_db():
    first_time = not os.path.exists(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if first_time:
        c.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zenid TEXT UNIQUE,
                wallet TEXT UNIQUE,
                username TEXT,
                bio TEXT,
                avatar TEXT,
                cover TEXT,
                followers INTEGER DEFAULT 0,
                following INTEGER DEFAULT 0
            )
        """)

        # Bảng posts
        c.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content TEXT,
                media TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        # Bảng comments
        c.execute("""
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                user_id INTEGER,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(post_id) REFERENCES posts(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        # Bảng lưu like
        c.execute("""
            CREATE TABLE IF NOT EXISTS post_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                user_id INTEGER,
                UNIQUE(post_id, user_id),
                FOREIGN KEY(post_id) REFERENCES posts(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

# Bảng lưu repost
        c.execute("""
            CREATE TABLE IF NOT EXISTS post_reposts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                user_id INTEGER,
                UNIQUE(post_id, user_id),
                FOREIGN KEY(post_id) REFERENCES posts(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        # Bảng earnings (tùy chọn)
        c.execute("""
            CREATE TABLE earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                post_id INTEGER,
                reward REAL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(post_id) REFERENCES posts(id)
            )
        """)
        conn.commit()
    else:
        # Nếu DB có rồi mà chưa có cột media thì thêm vào
        try:
            c.execute("ALTER TABLE posts ADD COLUMN media TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # cột đã tồn tại

    conn.close()

@app.route("/")
def home():
    if "zenid" not in session:
        return redirect(url_for("login"))

    zenid = session["zenid"]

    # lấy username + avatar để đồng bộ avatar ở composer và modal
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, avatar FROM users WHERE zenid=?", (zenid,))
    row = c.fetchone()
    conn.close()

    username = row[0] if row else None
    avatar   = row[1] if row else None

    return render_template(
        "index.html",
        zenid=zenid,
        username=username or (zenid[:6] + "..."),
        avatar_url=avatar or url_for("static", filename="default_avatar.png"),
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        zenid = request.form.get("zenid")
        if not zenid:
            return render_template("login.html", error="Please enter your ZenID")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE zenid=?", (zenid,))
        user = c.fetchone()
        conn.close()

        if user:
            session["zenid"] = zenid
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="ZenID not found, please mint one")
    return render_template("login.html")

@app.route("/mint", methods=["GET", "POST"])
def mint():
    # generate random ZenID like wallet
    chars = "abcdef0123456789"
    addr = "0x" + "".join(random.choice(chars) for _ in range(40))

    # save to DB
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (zenid) VALUES (?)", (addr,))
    conn.commit()
    conn.close()

    session["zenid"] = addr

    if request.method == "POST":
        return jsonify({"zenid": addr})
    else:
        return render_template("mint_success.html", zenid=addr)

@app.route("/register_zenid", methods=["POST"])
def register_zenid():
    zenid = request.json.get("zenid")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (zenid) VALUES (?)", (zenid,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.route("/profile")
def profile():
    if "zenid" not in session:
        return redirect(url_for("login"))

    zenid = session["zenid"]

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # lấy thông tin user
    c.execute(
        """
        SELECT id, username, bio, avatar, cover, followers, following 
        FROM users 
        WHERE zenid=? OR wallet=?
        """,
        (zenid, zenid),
    )
    row = c.fetchone()

    if row:
        user_db_id, username, bio, avatar, cover, followers, following = row
    else:
        conn.close()
        return redirect(url_for("login"))

    # lấy posts của user
    c.execute(
        """
        SELECT id, content, media, created_at, likes, comments, shares
        FROM posts
        WHERE user_id=?
        ORDER BY created_at DESC
        """,
        (user_db_id,),
    )
    posts = c.fetchall()

    posts_data = []
    for p in posts:
        post_id, content, media, created_at, likes, comments, shares = p

        # ✅ lấy danh sách comments cho từng post
        c.execute("""
            SELECT users.username, comments.content
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id=?
            ORDER BY comments.created_at ASC
        """, (post_id,))
        comments_list = [{"username": u, "content": ct} for u, ct in c.fetchall()]

        posts_data.append({
            "id": post_id,
            "content": content,
            "media": media,
            "created_at": created_at,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "comments_list": comments_list  # ✅ thêm vào context để profile.html dùng
        })

    conn.close()

    return render_template(
        "profile.html",
        zenid=zenid,
        username=username or (zenid[:6] + "..."),
        bio=bio or "This is my ZenSocial profile.",
        avatar_url=avatar or url_for("static", filename="default_avatar.png"),
        cover_url=cover or url_for("static", filename="default_cover.jpg"),
        followers=followers,
        following=following,
        posts=posts_data,
    )


# Upload config
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/edit_profile", methods=["POST"])
def edit_profile():
    if "zenid" not in session:
        return redirect(url_for("login"))

    zenid = session["zenid"]
    username = request.form.get("username")
    bio = request.form.get("bio")

    avatar_url, cover_url = None, None

    # Handle avatar upload
    if "avatar" in request.files:
        avatar = request.files["avatar"]
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(f"{zenid}_avatar.{avatar.filename.rsplit('.', 1)[1].lower()}")
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            avatar.save(path)
            avatar_url = "/" + path.replace("\\", "/")

    # Handle cover upload
    if "cover" in request.files:
        cover = request.files["cover"]
        if cover and allowed_file(cover.filename):
            filename = secure_filename(f"{zenid}_cover.{cover.filename.rsplit('.', 1)[1].lower()}")
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            cover.save(path)
            cover_url = "/" + path.replace("\\", "/")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE users 
        SET username=?, bio=?, 
            avatar=COALESCE(?, avatar), 
            cover=COALESCE(?, cover)
        WHERE zenid=?
    """, (username, bio, avatar_url, cover_url, zenid))
    conn.commit()
    conn.close()

    return ("", 204)

@app.route("/earn")
def earn():
    if "zenid" not in session:
        return redirect(url_for("login"))

    zenid = session["zenid"]

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Lấy thông tin user
    c.execute(
        "SELECT id, username, avatar FROM users WHERE zenid=?",
        (zenid,),
    )
    row = c.fetchone()

    if not row:
        conn.close()
        return redirect(url_for("login"))

    user_id, username, avatar = row

    # Đếm tổng like, comment, repost từ posts của user
    c.execute(
        """
        SELECT 
            COALESCE(SUM(likes),0),
            COALESCE(SUM(comments),0),
            COALESCE(SUM(shares),0)
        FROM posts
        WHERE user_id=?
        """,
        (user_id,),
    )
    likes, comments, reposts = c.fetchone()

    # Tạm tính earnings = likes*0.01 + comments*0.02 + reposts*0.05 (ví dụ)
    earnings = likes * 0.01 + comments * 0.02 + reposts * 0.05

    conn.close()

    return render_template(
        "earn.html",
        username=username,
        avatar=avatar if avatar else "https://via.placeholder.com/60",
        likes=likes,
        comments=comments,
        reposts=reposts,
        earnings=earnings,
    )

@app.route("/like_post/<int:post_id>", methods=["POST"])
def like_post(post_id):
    if "zenid" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE zenid=?", (session["zenid"],))
    user_id = c.fetchone()[0]

    # Kiểm tra đã like chưa
    c.execute("SELECT id FROM post_likes WHERE post_id=? AND user_id=?", (post_id, user_id))
    liked = c.fetchone()
    if liked:
        # Nếu đã like → bỏ like
        c.execute("DELETE FROM post_likes WHERE id=?", (liked[0],))
        c.execute("UPDATE posts SET likes = likes - 1 WHERE id=?", (post_id,))
        status = "unliked"
    else:
        # Nếu chưa like → thêm like
        c.execute("INSERT INTO post_likes (post_id, user_id) VALUES (?, ?)", (post_id, user_id))
        c.execute("UPDATE posts SET likes = likes + 1 WHERE id=?", (post_id,))
        status = "liked"

    conn.commit()
    conn.close()
    return jsonify({"status": status}), 200

@app.route("/repost_post/<int:post_id>", methods=["POST"])
def repost_post(post_id):
    if "zenid" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE zenid=?", (session["zenid"],))
    user_id = c.fetchone()[0]

    c.execute("SELECT id FROM post_reposts WHERE post_id=? AND user_id=?", (post_id, user_id))
    reposted = c.fetchone()
    if reposted:
        c.execute("DELETE FROM post_reposts WHERE id=?", (reposted[0],))
        c.execute("UPDATE posts SET shares = shares - 1 WHERE id=?", (post_id,))
        status = "unreposted"
    else:
        c.execute("INSERT INTO post_reposts (post_id, user_id) VALUES (?, ?)", (post_id, user_id))
        c.execute("UPDATE posts SET shares = shares + 1 WHERE id=?", (post_id,))
        status = "reposted"

    conn.commit()
    conn.close()
    return jsonify({"status": status}), 200

@app.route("/comment_post/<int:post_id>", methods=["POST"])
def comment_post(post_id):
    if "zenid" not in session:
        return redirect(url_for("login"))

    content = request.json.get("content")
    if not content:
        return {"error": "Empty comment"}, 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE zenid=?", (session["zenid"],))
    user_row = c.fetchone()
    if not user_row:
        return {"error": "User not found"}, 404

    user_id, username = user_row
    c.execute("INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
              (post_id, user_id, content))
    c.execute("UPDATE posts SET comments = comments + 1 WHERE id=?", (post_id,))
    conn.commit()
    conn.close()

    return {"username": username or session["zenid"][:6], "content": content}, 201

@app.route("/create_post", methods=["POST"])
def create_post():
    if "zenid" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    zenid = session["zenid"]

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Lấy user_id, username, avatar
    c.execute("SELECT id, username, avatar FROM users WHERE zenid=?", (zenid,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404

    user_id, username, avatar = row

    # Lấy content từ form (text)
    content = request.form.get("content", "").strip()
    if not content and "media" not in request.files:
        return jsonify({"success": False, "message": "Post is empty"}), 400

    # Xử lý file upload (nếu có)
    media_url = None
    if "media" in request.files:
        file = request.files["media"]
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = secure_filename(f"{zenid}_{random.randint(1000,9999)}.{ext}")
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            media_url = "/" + path.replace("\\", "/")

    # Lưu post vào DB
    try:
        c.execute(
            """
            INSERT INTO posts (user_id, content, media, likes, comments, shares, created_at)
            VALUES (?, ?, ?, 0, 0, 0, datetime('now'))
            """,
            (user_id, content, media_url),
        )
        conn.commit()
        post_id = c.lastrowid
        conn.close()

        return jsonify({
            "success": True,
            "message": "Post created",
            "post_id": post_id,
            "username": username or zenid[:6] + "...",
            "avatar": avatar or url_for("static", filename="default_avatar.png"),
            "content": content,
            "media": media_url,
            "likes": 0,
            "comments": 0,
            "shares": 0
        }), 201

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "message": str(e)}), 500
    
@app.route("/messages")
def messenger():
    if "zenid" not in session:
        return redirect(url_for("login"))

    zenid = session["zenid"]
    # lấy avatar + username để đồng bộ UI
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT username, avatar FROM users WHERE zenid=?", (zenid,))
    row = c.fetchone(); conn.close()

    username = row[0] if row else None
    avatar   = row[1] if row else None

    return render_template(
        "messenger.html",
        zenid=zenid,
        username=username or (zenid[:6] + "..."),
        avatar_url=avatar or url_for("static", filename="default_avatar.png"),
    )

@app.route("/notifications")
def notifications():
    if "zenid" not in session:
        return redirect(url_for("login"))

    zenid = session["zenid"]

    # Nếu muốn đồng bộ avatar/username cho sidebar (không bắt buộc nhưng nên có)
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT username, avatar FROM users WHERE zenid=?", (zenid,))
    row = c.fetchone(); conn.close()

    username = row[0] if row else None
    avatar   = row[1] if row else None

    return render_template(
        "notifications.html",
        zenid=zenid,
        username=username or (zenid[:6] + "..."),
        avatar_url=avatar or url_for("static", filename="default_avatar.png"),
    )
    
@app.route("/wallet_login", methods=["POST"])
def wallet_login():
    data = request.get_json()
    wallet = data.get("wallet")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE wallet=?", (wallet,))
    row = c.fetchone()

    if row:
        # user đã có sẵn → login
        session["zenid"] = wallet
        conn.close()
        return jsonify({"success": True})
    else:
        # tạo user mới
        c.execute("INSERT INTO users (wallet, username) VALUES (?, ?)", (wallet, f"user_{wallet[:6]}"))
        conn.commit()
        session["zenid"] = wallet
        conn.close()
        return jsonify({"success": True})

@app.route("/logout")
def logout():
    session.pop("zenid", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)