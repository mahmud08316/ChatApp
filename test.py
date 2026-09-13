from flask import Flask

app = Flask("ChatApp")

@app.route("/")
def home():
    return "ChatApp server ishlayapti!"

app.run(host="0.0.0.0", port=5000)
