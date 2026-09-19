from flask import Flask, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask("ChatApp")
app.secret_key = "chatapp-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# DATABASE

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)


with app.app_context():
    db.create_all()


# STYLE

STYLE = """
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #e9f1f7;
    color: #222;
}

.container {
    max-width: 500px;
    margin: 40px auto;
    background: white;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.header {
    background: #229ed9;
    color: white;
    padding: 20px;
    font-size: 23px;
    font-weight: bold;
}

.content {
    padding: 20px;
}

input {
    width: 100%;
    padding: 13px;
    margin: 7px 0;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 15px;
}

button {
    width: 100%;
    padding: 13px;
    margin-top: 8px;
    border: none;
    border-radius: 10px;
    background: #229ed9;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #168ac0;
}

.user {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 13px;
    margin: 8px 0;
    background: #f1f5f8;
    border-radius: 12px;
}

.user a {
    text-decoration: none;
    color: white;
    background: #229ed9;
    padding: 8px 13px;
    border-radius: 9px;
}

.message {
    padding: 10px 13px;
    margin: 8px 0;
    border-radius: 12px;
    background: #f1f5f8;
}

.me {
    background: #d8f4ff;
    text-align: right;
}

.small {
    text-align: center;
    color: #777;
    margin-top: 15px;
}
</style>
"""


# HOME

@app.route("/")
def home():
    username = session.get("username")

    if not username:
        return STYLE + """
        <div class="container">
            <div class="header">
                💬 ChatApp
            </div>

            <div class="content">
                <h2>Kirish</h2>

                <form action="/login" method="post">
                    <input
                        name="username"
                        placeholder="Username"
                        required
                    >

                    <input
                        name="password"
                        type="password"
                        placeholder="Password"
                        required
                    >

                    <button type="submit">
                        Kirish
                    </button>
                </form>

                <hr>

                <h2>Ro‘yxatdan o‘tish</h2>

                <form action="/register" method="post">
                    <input
                        name="username"
                        placeholder="Username"
                        required
                    >

                    <input
                        name="password"
                        type="password"
                        placeholder="Password"
                        required
                    >

                    <button type="submit">
                        Register
                    </button>
                </form>
            </div>
        </div>
        """

    users = User.query.filter(
        User.username != username
    ).all()

    users_html = ""

    for user in users:
        users_html += f"""
        <div class="user">
            <span>👤 <b>{user.username}</b></span>
                     <a href="/chat/{user.username}">
                Chat
            </a>
        </div>
        """

    return STYLE + f"""
    <div class="container">

        <div class="header">
            💬 ChatApp
        </div>

        <div class="content">

            <h3>Salom, {username}! 👋</h3>

            <h2>Foydalanuvchilar 👥</h2>

            {users_html if users_html else
            "<p>Hozircha boshqa foydalanuvchi yo‘q.</p>"}

            <form action="/logout" method="post">
                <button type="submit">
                    Chiqish
                </button>
            </form>

        </div>
    </div>
    """


# REGISTER

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "Ma'lumotlarni to‘liq kiriting."

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:
        return """
        <h2>❌ Bu username band.</h2>
        <a href="/">Orqaga</a>
        """

    new_user = User(
        username=username,
        password=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    return """
    <h2>✅ Register muvaffaqiyatli!</h2>
    <a href="/">Login qilish</a>
    """


# LOGIN

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(
        username=username
    ).first()

    if user and check_password_hash(
        user.password,
        password
    ):
        session["username"] = user.username
        return redirect("/")

    return """
    <h2>❌ Username yoki password noto‘g‘ri.</h2>
    <a href="/">Orqaga</a>
    """


# CHAT

@app.route("/chat/<receiver>")
def chat(receiver):
    username = session.get("username")

    if not username:
        return redirect("/")

    user = User.query.filter_by(
        username=receiver
    ).first()

    if not user:
        return "Foydalanuvchi topilmadi."

    messages = Message.query.filter(
        (
            (Message.sender == username) &
            (Message.receiver == receiver)
        )
        |
        (
            (Message.sender == receiver) &
            (Message.receiver == username)
        )
    ).all()

    messages_html = ""

    for message in messages:

        if message.sender == username:
            messages_html += f"""
            <div class="message me">
                <b>Siz</b><br>
                {message.text}
            </div>
            """
        else:
            messages_html += f"""
            <div class="message">
                <b>{message.sender}</b><br>
                {message.text}
            </div>
            """

    return STYLE + f"""
    <div class="container">

        <div class="header">
            💬 {receiver}
        </div>

        <div class="content">

            <p>
                <a href="/">⬅️ Orqaga</a>
            </p>

            <hr>

            {messages_html if messages_html else
            "<p class='small'>Hali xabar yo‘q.</p>"}

            <form action="/send/{receiver}" method="post">

                <input
                    name="message"
                    placeholder="Xabar yozing..."
                    required
                >

                <button type="submit">
                    Yuborish ➤
                </button>

            </form>

        </div>
    </div>
    """


# SEND MESSAGE

@app.route("/send/<receiver>", methods=["POST"])
def send(receiver):
    username = session.get("username")

    if not username:
        return redirect("/")

    text = request.form.get("message")

    if text:
        message = Message(
            sender=username,
            receiver=receiver,
            text=text
        )

        db.session.add(message)
        db.session.commit()

    return redirect(f"/chat/{receiver}")


# LOGOUT
        @app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect("/")


# RUN

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
