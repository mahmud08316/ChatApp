from flask import Flask, request

app = Flask("ChatApp")

@app.route("/")
def home():
    return """
    <h1>ChatApp 💬</h1>

    <form action="/send" method="post">
        <input name="message" placeholder="Xabar yozing">
        <button type="submit">Yuborish</button>
    </form>
    """

@app.route("/send", methods=["POST"])
def send():
    message = request.form.get("message")
    return f"<h1>Siz yozdingiz:</h1><p>{message}</p>"

app.run(host="0.0.0.0", port=5000)
