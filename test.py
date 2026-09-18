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
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>ChatApp</title>
        </head>

        <body style="font-family:Arial; text-align:center; padding:40px;">

            <h1>💬 ChatApp</h1>

            <form action="/login" method="post">

                <input
                    name="username"
                    placeholder="Ismingiz"
                    style="padding:12px; font-size:16px;"
                >

                <br><br>

                <button
                    style="padding:12px 25px; font-size:16px;"
                >
                    Kirish
                </button>

            </form>

        </body>
        </html>
        """

    messages = Message.query.all()

    xabarlar = ""

    for message in messages:
        xabarlar += f"""
        <div style="
            background:white;
            padding:12px;
            margin:8px 0;
            border-radius:10px;
        ">

            <b>👤 {message.username}</b>

            <br>

            {message.text}

        </div>
        """

    return f"""
    <html>

    <head>

        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <title>ChatApp</title>

    </head>

    <body style="
        margin:0;
        font-family:Arial;
        background:#eeeeee;
    ">

        <div style="
            background:#333;
            color:white;
            padding:20px;
            text-align:center;
        ">

            <h2>💬 ChatApp</h2>

            <div>Salom, {username}!</div>

        </div>


        <div style="
            padding:15px;
            padding-bottom:100px;
        ">

            {xabarlar}

        </div>


        <form
            action="/send"
            method="post"
            style="
                position:fixed;
                bottom:0;
                width:100%;
                background:white;
                padding:10px;
                box-sizing:border-box;
            "
        >

            <input
                name="message"
                placeholder="Xabar yozing..."
                style="
                    width:75%;
                    padding:12px;
                    box-sizing:border-box;
                "
            >

            <button
                style="
                    width:23%;
                    padding:12px;
                "
            >
                Yuborish
            </button>

        </form>

    </body>

    </html>
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
    text = request.form.get("message")

    if username and text:

        message = Message(
            username=username,
            text=text
        )

        db.session.add(message)
        db.session.commit()

    return home()


if __name__ == "main":
    app.run(
        host="0.0.0.0",
        port=5000
    )
