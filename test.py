from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask("ChatApp")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    messages = Message.query.all()

    xabarlar_html = ""

    for message in messages:
        xabarlar_html += f"<p>💬 {message.text}</p>"

    return f"""
    <h1>ChatApp 💬</h1>

    {xabarlar_html}

    <form action="/send" method="post">
        <input name="message" placeholder="Xabar yozing">
        <button type="submit">Yuborish</button>
    </form>
    """


@app.route("/send", methods=["POST"])
def send():
    message = request.form.get("message")

    if message:
        yangi_xabar = Message(text=message)
        db.session.add(yangi_xabar)
        db.session.commit()

    return home()


app.run(host="0.0.0.0", port=5000)
