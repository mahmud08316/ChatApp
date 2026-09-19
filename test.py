from flask import Flask, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask("ChatApp")

app.secret_key = "chatapp-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


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


STYLE = """
<style>
body {
    font-family: Arial, sans-serif;
    background: #f2f2f2;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 600px;
    margin: auto;
    background: white;
    padding: 20px;
    border-radius: 15px;
}

input {
    width: 90%;
    padding: 12px;
    margin: 5px 0;
    border: 1px solid #ccc;
    border-radius: 8px;
}

button {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    background: #007bff;
    color: white;
    cursor: pointer;
}

button:hover {
    background: #0056b3;
}

.user {
    display: block;
    padding: 15px;
    margin: 10px 0;
    background: #eeeeee;
    border-radius: 10px;
    text-decoration: none;
    color: black;
}

.message {
    background: #eeeeee;
    padding: 10px;
    margin: 8px 0;
    border-radius: 10px;
}

.me {
    background: #cce5ff;
    text-align: right;
}
</style>
"""


@app.route("/")
def home():
    username = session.get("username")

    if not username:
        return STYLE + """
        <div class="container">
            <h1>💬 ChatApp</h1>

            <h2>Login</h2>

            <form method="POST" action="/login">
                <input name="username" placeholder="Username" required>
                <br>
                <input name="password" type="password" placeholder="Password" required>
                <br>
                <button type="submit">Login</button>
            </form>

            <hr>

            <h2>Register</h2>

            <form method="POST" action="/register">
                <input name="username" placeholder="Username" required>
                <br>
                <input name="password" type="password" placeholder="Password" required>
                <br>
                <button type="submit">Register</button>
            </form>
        </div>
        """

    users = User.query.filter(User.username != username).all()

    users_html = ""

    for user in users:
        users_html += f"""
        <a class="user" href="/chat/{user.username}">
            👤 {user.username}
        </a>
        """

    return STYLE + f"""
    <div class="container">
        <h1>💬 ChatApp</h1>

        <h3>Salom, {username}! 👋</h3>

        <form method="POST" action="/logout">
            <button type="submit">Logout</button>
        </form>

        <h2>Users</h2>

        {users_html}
    </div>
    """


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "Ma'lumotlarni to‘liq kiriting."

    existing_user = User.query.filter_by(username=username).first()

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


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
[9/19/2026 3:40 PM] Nizomov: user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session["username"] = user.username
        return redirect("/")

    return """
    <h2>❌ Username yoki password noto‘g‘ri.</h2>
    <a href="/">Orqaga</a>
    """


@app.route("/chat/<receiver>")
def chat(receiver):
    username = session.get("username")

    if not username:
        return redirect("/")

    user = User.query.filter_by(username=receiver).first()

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

        <h2>💬 Chat: {receiver}</h2>

        {messages_html}

        <form method="POST" action="/send/{receiver}">
            <input name="message" placeholder="Xabar yozing..." required>
            <button type="submit">Send</button>
        </form>

        <br>

        <a href="/">⬅ Orqaga</a>

    </div>
    """


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


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect("/")


if name == "main":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
