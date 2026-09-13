from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask("ChatApp")

app.secret_key = "chatapp-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    username = session.get("username")

    if not username:
        return """
        <h1>ChatApp 💬</h1>
        <form action="/login" method="post">
            <input name="username" placeholder="Ismingiz">
            <button type="submit">Kirish</button>
        </form>
        """

    messages = Message.query.all()

    xabarlar_html = ""

    for message in messages:
        xabarlar_html += f"<p>💬 <b>{message.username}:</b> {message.text}</p>"

    return f"""
    <h1>ChatApp 💬</h1>
    <p>Salom, <b>{username}</b>!</p>

    {xabarlar_html}

    <form action="/send" method="post">
        <input name="message" placeholder="Xabar yozing">
        <button type="submit">Yuborish</button>
    </form>
    """


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")

    if username:
        session["username"] = username

    return home()


@app.route("/send", methods=["POST"])
def send():
    username = session.get("username")
    message = request.form.get("message")

    if username and message:
        yangi_xabar = Message(username=username, text=message)
        db.session.add(yangi_xabar)
        db.session.commit()

    return home()


app.run(host="0.0.0.0", port=5000)
