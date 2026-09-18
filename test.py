from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask("ChatApp")
app.secret_key = "chatapp-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# USER MODEL
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# =========================
# MESSAGE MODEL
# =========================

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)


with app.app_context():
    db.create_all()


# =========================
# HOME
# =========================

@app.route("/")
def home():
    username = session.get("username")

    if not username:
        return """
        <h1>ChatApp 💬</h1>

        <h2>Login</h2>

        <form action="/login" method="post">
            <input name="username" placeholder="Username" required>
            <br><br>
            <input type="password" name="password" placeholder="Parol" required>
            <br><br>
            <button type="submit">Kirish</button>
        </form>

        <br>

        <a href="/register">
            Ro'yxatdan o'tish
        </a>
        """

    messages = Message.query.all()

    xabarlar_html = ""

    for message in messages:
        xabarlar_html += f"""
        <p>
            💬 <b>{message.username}:</b> {message.text}
        </p>
        """

    return f"""
    <h1>ChatApp 💬</h1>

    <p>Salom, <b>{username}</b>! 👋</p>

    <hr>

    {xabarlar_html}

    <hr>

    <form action="/send" method="post">
        <input
            name="message"
            placeholder="Xabar yozing"
            required
        >
        <button type="submit">Yuborish</button>
    </form>

    <br>

    <form action="/logout" method="post">
        <button type="submit">Chiqish 🚪</button>
    </form>
    """


# =========================
# REGISTER PAGE
# =========================

@app.route("/register")
def register_page():
    return """
    <h1>ChatApp 💬</h1>

    <h2>Ro'yxatdan o'tish</h2>

    <form action="/register" method="post">

        <input
            name="username"
            placeholder="Username"
            required
        >

        <br><br>

        <input
            type="password"
            name="password"
            placeholder="Parol"
            required
        >

        <br><br>

        <button type="submit">
            Ro'yxatdan o'tish
        </button>

    </form>

    <br>

    <a href="/">
        Login sahifasiga qaytish
    </a>
    """


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "Username va parolni kiriting!"

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:
        return """
        <h2>Bu username allaqachon mavjud! ❌</h2>
        <a href="/register">Qaytish</a>
        """

    hashed_password = generate_password_hash(password)

    yangi_user = User(
        username=username,
        password=hashed_password
    )

    db.session.add(yangi_user)
    db.session.commit()

    return """
    <h2>Ro'yxatdan o'tish muvaffaqiyatli! ✅</h2>

    <a href="/">
        Login qilish
    </a>
    """


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(
        username=username
    ).first()
[9/18/2026 3:55 PM] Nizomov: if not user:
        return """
        <h2>Username yoki parol noto'g'ri! ❌</h2>
        <a href="/">Qaytish</a>
        """

    if not check_password_hash(user.password, password):
        return """
        <h2>Username yoki parol noto'g'ri! ❌</h2>
        <a href="/">Qaytish</a>
        """

    session["username"] = user.username

    return home()


# =========================
# SEND MESSAGE
# =========================

@app.route("/send", methods=["POST"])
def send():

    username = session.get("username")
    message = request.form.get("message")

    if not username:
        return """
        <h2>Avval login qiling! 🔐</h2>
        <a href="/">Login</a>
        """

    if message:

        yangi_xabar = Message(
            username=username,
            text=message
        )

        db.session.add(yangi_xabar)
        db.session.commit()

    return home()


# =========================
# LOGOUT
# =========================

@app.route("/logout", methods=["POST"])
def logout():

    session.pop("username", None)

    return home()


# =========================
# START APP
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
