import os
from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.get("/test")
    def test():
        return "test", 200

    @app.get("/ping")
    def ping():
        return jsonify({"status": "ok", "data": "pooong"}), 200

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    create_app().run(host="0.0.0.0", port=port)
