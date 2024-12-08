from flask import Flask
import views

def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")

    # Explicitly add endpoint names for each route
    app.add_url_rule("/", view_func=views.index_page, endpoint="index_page")
    app.add_url_rule("/add", view_func=views.add_anime_page, methods=["GET", "POST"], endpoint="add_anime")
    app.add_url_rule("/studios", view_func=views.studios_page, endpoint="studios_page")
    app.add_url_rule("/studios/<int:studio_id>", view_func=views.studio_animes_page, endpoint="studio_animes_page")
    app.add_url_rule("/anime/<int:anime_id>", view_func=views.anime_page, endpoint="anime_page")
    app.add_url_rule("/top100", view_func=views.top_100_page, endpoint="top_100_page")

    return app

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
