from flask import Flask, request, session
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
            <input name="password" type="password" placeholder="Password" required>
            <br><br>
            <button type="submit">Kirish</button>
        </form>

        <hr>

        <h2>Register</h2>

        <form action="/register" method="post">
            <input name="username" placeholder="Username" required>
            <br><br>
            <input name="password" type="password" placeholder="Password" required>
            <br><br>
            <button type="submit">Register</button>
        </form>
        """

    users = User.query.filter(User.username != username).all()

    users_html = "<h2>Foydalanuvchilar 👥</h2>"

    for user in users:
        users_html += f"""
        <p>
            👤 <b>{user.username}</b>
            <a href="/chat/{user.username}">Yozish</a>
        </p>
        """

    return f"""
    <h1>ChatApp 💬</h1>

    <p>Salom, <b>{username}</b>!</p>

    {users_html}

    <br>

    <form action="/logout" method="post">
        <button type="submit">Chiqish</button>
    </form>
    """


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "Username va password kiriting."

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return "Bu username band. <a href='/'>Orqaga</a>"

    new_user = User(
        username=username,
        password=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    return "Register muvaffaqiyatli! <a href='/'>Login qilish</a>"


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session["username"] = user.username
        return home()

    return "Username yoki password noto‘g‘ri. <a href='/'>Orqaga</a>"


@app.route("/chat/<receiver>")
def chat(receiver):
    username = session.get("username")

    if not username:
        return "Avval login qiling. <a href='/'>Login</a>"

    user = User.query.filter_by(username=receiver).first()

    if not user:
        return "Bunday foydalanuvchi topilmadi."

    messages = Message.query.filter(
        ((Message.sender == username) & (Message.receiver == receiver)) |
        ((Message.sender == receiver) & (Message.receiver == username))
    ).all()

    messages_html = ""

    for message in messages:
        messages_html += f"""
        <p>
            <b>{message.sender}:</b> {message.text}
        </p>
        """

    return f"""
    <h1>💬 {receiver} bilan chat</h1>

    <a href="/">⬅️ Foydalanuvchilar</a>

    <hr>

    {messages_html}

    <form action="/send/{receiver}" method="post">
        <input name="message" placeholder="Xabar yozin
[9/18/2026 4:33 PM] Nizomov: g" required>
        <button type="submit">Yuborish</button>
    </form>
    """


@app.route("/send/<receiver>", methods=["POST"])
def send(receiver):
    username = session.get("username")
    message_text = request.form.get("message")

    if not username:
        return "Avval login qiling."

    if message_text:
        message = Message(
            sender=username,
            receiver=receiver,
            text=message_text
        )

        db.session.add(message)
        db.session.commit()

    return chat(receiver)


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return home()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
