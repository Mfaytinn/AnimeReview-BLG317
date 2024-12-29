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
    app.add_url_rule("/logout", view_func=views.logout, endpoint="logout")
    
    app.add_url_rule("/profile", view_func=views.profile_page, endpoint="profile_page")
    app.add_url_rule("/profile/update", view_func=views.update_profile, methods=["POST"], endpoint="update_profile")
    app.add_url_rule("/profile/delete", view_func=views.delete_account, methods=["POST"], endpoint="delete_account")
    app.add_url_rule("/profile/change_password", view_func=views.change_password, methods=["POST"], endpoint="change_password")

    app.add_url_rule("/edit_review/<int:score_id>", view_func=views.edit_review, methods=["GET", "POST"], endpoint="edit_review")
    app.add_url_rule("/dislike_review/<int:score_id>", view_func=views.dislike_review, methods=["POST"], endpoint="dislike_review")
    app.add_url_rule("/like_review/<int:score_id>", view_func=views.like_review, methods=["POST"], endpoint="like_review")
    app.add_url_rule("/delete_review/<int:score_id>", view_func=views.delete_review, methods=["POST"], endpoint="delete_review")
    
    app.add_url_rule("/anime/<int:anime_id>/add_to_watchlist", view_func=views.add_to_watchlist, methods=["POST"], endpoint="add_to_watchlist")
    app.add_url_rule("/my_list", view_func=views.my_list, methods=["GET","POST"], endpoint="my_list")
    app.add_url_rule("/my_list/remove/<int:anime_id>", view_func=views.remove_from_watchlist, methods=["POST"], endpoint="remove_from_watchlist")
    app.add_url_rule("/my_list/update_status/<int:anime_id>", view_func=views.update_watchlist_status, methods=["POST"], endpoint="update_watchlist_status")
    
    # Admin Dashboard Route
    app.add_url_rule(
        "/admin/dashboard",
        view_func=views.admin_dashboard,
        methods=["GET"],
        endpoint="admin_dashboard"
    )

    # Add Anime Route
    app.add_url_rule(
        "/admin/anime/add",
        view_func=views.admin_add_anime,
        methods=["GET", "POST"],
        endpoint="admin_add_anime"
    )

    # Update Anime Route
    app.add_url_rule(
        "/admin/anime/update/<int:anime_id>",
        view_func=views.admin_update_anime,
        methods=["GET", "POST"],
        endpoint="admin_update_anime"
    )

    # Delete Anime Route
    app.add_url_rule(
        "/admin/anime/delete/<int:anime_id>",
        view_func=views.admin_delete_anime,
        methods=["POST"],
        endpoint="admin_delete_anime"
    )
    # Manage Animes Route
    app.add_url_rule(
        "/admin/anime/manage",
        view_func=views.admin_manage_animes,
        methods=["GET"],
        endpoint="admin_manage_animes"
    )

    app.add_url_rule(
    "/admin/users/manage",
    view_func=views.admin_manage_users,
    methods=["GET", "POST"],
    endpoint="admin_manage_users"
    )

    # Update User Role Route
    app.add_url_rule(
        "/admin/users/update_role/<int:user_id>",
        view_func=views.admin_update_user_role,
        methods=["POST"],
        endpoint="admin_update_user_role"
    )

    app.add_url_rule(
        "/admin/users/delete/<int:user_id>",
        view_func=views.admin_delete_user,
        methods=["POST"],
        endpoint="admin_delete_user"
    )




    return app

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
