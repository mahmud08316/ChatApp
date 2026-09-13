from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask("ChatApp")
app.secret_key = "chatapp-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)


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
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>ChatApp</title>
        </head>
        <body style="font-family: Arial; text-align: center; padding: 40px;">
            <h1>💬 ChatApp</h1>

            <form action="/login" method="post">
                <input name="username"
                       placeholder="Ismingiz"
                       style="padding: 12px; font-size: 16px;">
                <br><br>
                <button style="padding: 12px 25px; font-size: 16px;">
                    Kirish
                </button>
            </form>
        </body>
        </html>
        """

    messages = Message.query.all()

    xabarlar_html = ""

    for message in messages:
        xabarlar_html += f"""
        <div style="
            background: white;
            padding: 10px;
            margin: 8px 0;
            border-radius: 10px;
            text-align: left;
        ">
            <b>👤 {message.username}</b>
            <br>
            {message.text}
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>ChatApp</title>

        <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    </head>

    <body style="
        margin: 0;
        font-family: Arial;
        background: #eeeeee;
    ">

        <div style="
            background: #333333;
            color: white;
            padding: 15px;
            text-align: center;
        ">
            <h2>💬 ChatApp</h2>
            <div>Salom, {username}!</div>
        </div>

        <div id="messages" style="
            padding: 15px;
            padding-bottom: 80px;
        ">
            {xabarlar_html}
        </div>

        <form id="messageForm" style="
            position: fixed;
            bottom: 0;
            width: 100%;
            background: white;
            padding: 10px;
            box-sizing: border-box;
        ">
            <input id="messageInput"
                   placeholder="Xabar yozing..."
                   style="
                       width: 75%;
                       padding: 12px;
                       box-sizing: border-box;
                   ">

            <button style="
                width: 23%;
                padding: 12px;
            ">
                Yuborish
            </button>
        </form>

        <script>
            const socket = io();

            const form = document.getElementById("messageForm");
            const input = document.getElementById("messageInput");
            const messages = document.getElementById("messages");

            form.addEventListener("submit", function(event) {
                event.preventDefault();

                const text = input.value.trim();

                if (text) {
                    socket.emit("send_message", {
                        text: text
                    });

                    input.value = "";
                }
            });

            socket.on("new_message", function(data) {
                const message = document.createElement("div");

                message.style.background = "white";
                message.style.padding = "10px";
                message.style.margin = "8px 0";
[9/13/2026 3:09 PM] Nizomov: message.style.borderRadius = "10px";

                message.innerHTML =
                    "<b>👤 " + data.username + "</b><br>" +
                    data.text;

                messages.appendChild(message);

                window.scrollTo(0, document.body.scrollHeight);
            });
        </script>

    </body>
    </html>
    """


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")

    if username:
        session["username"] = username

    return home()


@socketio.on("send_message")
def handle_message(data):
    username = session.get("username")
    text = data.get("text")

    if username and text:
        yangi_xabar = Message(
            username=username,
            text=text
        )

        db.session.add(yangi_xabar)
        db.session.commit()

        emit(
            "new_message",
            {
                "username": username,
                "text": text
            },
            broadcast=True
        )


if name == "main":
    socketio.run(app, host="0.0.0.0", port=5000)
