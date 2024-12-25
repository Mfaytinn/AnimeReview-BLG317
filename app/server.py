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
    app.add_url_rule("/search", view_func=views.search, methods=["GET"], endpoint="search")
    app.add_url_rule("/signin", view_func=views.signin_page, methods=["GET", "POST"], endpoint="signin_page")
    app.add_url_rule("/signup", view_func=views.signup_page, methods=["GET", "POST"], endpoint="signup_page")
    app.add_url_rule("/anime/<int:anime_id>/add_review", view_func=views.add_review, methods=["POST"], endpoint="add_review")
    app.add_url_rule("/profile", view_func=views.profile_page, endpoint="profile_page")
    app.add_url_rule("/logout", view_func=views.logout, endpoint="logout")
    return app

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
