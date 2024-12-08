from flask import Flask
import views

def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    # Explicitly add endpoint names for each route
    app.add_url_rule("/", view_func=views.index_page, endpoint="index_page")
    app.add_url_rule("/add", view_func=views.add_anime_page, methods=["GET", "POST"], endpoint="add_anime")
    return app

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
