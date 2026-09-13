from flask import Flask, request

app = Flask("ChatApp")

xabarlar = []

@app.route("/")
def home():
    xabarlar_html = ""

    for xabar in xabarlar:
        xabarlar_html += f"<p>💬 {xabar}</p>"

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
        xabarlar.append(message)

    return home()

app.run(host="0.0.0.0", port=5000)
