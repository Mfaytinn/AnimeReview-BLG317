from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from mysql.connector import Error

def index_page():
    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return render_template('index.html', anime_information=[], current_page=1, has_next=False)

    try:
        # Get the current page from query parameters (default to 1)
        current_page = int(request.args.get('page', 1))
        per_page = 12  # Number of records per page
        offset = (current_page - 1) * per_page

        cursor = connection.cursor(dictionary=True)
        # Fetch only the current page's results
        cursor.execute("SELECT * FROM Anime_Information LIMIT %s OFFSET %s", (per_page, offset))
        anime_information = cursor.fetchall()

        # Check if there's a next page
        cursor.execute("SELECT COUNT(*) AS total FROM Anime_Information")
        total_records = cursor.fetchone()['total']
        has_next = (current_page * per_page) < total_records

    except Error as e:
        flash(f"Query failed: {e}", category="danger")
        anime_information = []
        current_page = 1
        has_next = False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template(
        'index.html',
        anime_information=anime_information,
        current_page=current_page,
        has_next=has_next
    )

def add_anime_page():
    if request.method == "POST":
        anime_name = request.form.get("anime_name")
        english_name = request.form.get("english_name")
        other_name = request.form.get("other_name")
        synopsis = request.form.get("synopsis")
        type_anime = request.form.get("type_anime")
        genres = request.form.get("genres")

        # Form validation
        if not anime_name or not synopsis:
            flash("Anime Name and Synopsis are necessary.", "warning")
            return render_template("add_anime.html")

        connection = get_db_connection()
        if connection is None:
            flash("Couldn't connect to the database!", "danger")
            return render_template("add_anime.html")

        # Adding anime to the database
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO Anime_Information (anime_name, english_name, other_name, synopsis, type_anime, genres) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (anime_name, english_name, other_name, synopsis, type_anime, genres),
            )
            connection.commit()
            flash("Anime added successfully!", "success")
            return redirect(url_for("index_page"))
        except Error as e:
            flash(f"An exception occurred while adding the anime: {e}", "danger")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template("add_anime.html")

def studios_page():
    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return render_template('studios.html', studios=[], current_page=1, has_next=False)

    try:
        # Get the current page from query parameters (default to 1)
        current_page = int(request.args.get('page', 1))
        per_page = 12  # Number of records per page
        offset = (current_page - 1) * per_page

        cursor = connection.cursor(dictionary=True)
        # Fetch only the current page's results
        cursor.execute("SELECT * FROM Studios LIMIT %s OFFSET %s", (per_page, offset))
        studios = cursor.fetchall()

        # Check if there's a next page
        cursor.execute("SELECT COUNT(*) AS total FROM Studios")
        total_records = cursor.fetchone()['total']
        has_next = (current_page * per_page) < total_records

    except Error as e:
        flash(f"Query failed: {e}", category="danger")
        studios = []
        current_page = 1
        has_next = False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template(
        'studios.html',
        studios=studios,
        current_page=current_page,
        has_next=has_next
    )

def studio_animes_page(studio_id):
    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return render_template('studio_animes.html', animes=[])

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT ai.anime_id, ai.anime_name, ai.english_name, ai.other_name, ai.synopsis, ai.type_anime 
            FROM Anime_Information ai
            JOIN Anime_Production ap ON ai.anime_id = ap.anime_id
            WHERE ap.studio_id = %s
        """, (studio_id,))
        animes = cursor.fetchall()

    except Error as e:
        flash(f"Query failed: {e}", category="danger")
        animes = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('studio_animes.html', animes=animes)

def anime_page(anime_id):
    user_id = session.get('user_id', None)  # Get the logged-in user's ID, if any

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return render_template(
            'anime_page.html', anime_info={}, anime_metadata={}, reviews=[], anime_id=anime_id, user_id=user_id
        )

    try:
        cursor = connection.cursor(dictionary=True)

        # Fetch anime information and metadata
        cursor.execute("""
            SELECT ai.anime_name, ai.english_name, ai.other_name, ai.synopsis, ai.type_anime, ai.genres,
                   am.episodes, am.aired, am.premiered, am.source
            FROM Anime_Information ai
            JOIN Anime_Metadata am ON ai.anime_id = am.anime_id
            WHERE ai.anime_id = %s
        """, (anime_id,))
        result = cursor.fetchone()

        if result:
            anime_info = {
                'anime_name': result['anime_name'],
                'english_name': result['english_name'],
                'other_name': result['other_name'],
                'synopsis': result['synopsis'],
                'type_anime': result['type_anime'],
                'genres': result['genres']
            }
            anime_metadata = {
                'episodes': result['episodes'],
                'aired': result['aired'],
                'premiered': result['premiered'],
                'source': result['source']
            }
        else:
            flash("Anime not found!", category="danger")
            return redirect(url_for('home'))

        # Fetch all reviews with likes, dislikes, and user's interaction status
        cursor.execute("""
            SELECT scores.score_id, u.username, scores.score, scores.comment, scores.likes, scores.dislikes,
                   CASE WHEN scores.user_id = %s THEN 1 ELSE 0 END AS is_user_review,
                   (SELECT action FROM Review_Interactions
                    WHERE user_id = %s AND score_id = scores.score_id) AS user_action
            FROM Anime_Scores AS scores
            LEFT JOIN Users u ON scores.user_id = u.user_id
            WHERE scores.anime_id = %s
            ORDER BY is_user_review DESC, scores.score_id DESC
            LIMIT 20
        """, (user_id, user_id, anime_id))
        reviews = cursor.fetchall()

        cursor.execute("""
            SELECT status FROM Watchlist
            WHERE user_id = %s AND anime_id = %s
        """, (user_id, anime_id))
        watchlist_status = cursor.fetchone()
        watchlist_status = watchlist_status['status'] if watchlist_status else None

    except Error as e:
        flash(f"Database error: {e}", category="danger")
        anime_info = {}
        anime_metadata = {}
        reviews = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template(
        'anime_page.html',
        anime_info=anime_info,
        anime_metadata=anime_metadata,
        reviews=reviews,
        user_id=user_id,
        watchlist_status=watchlist_status,
        anime_id=anime_id
    )


def add_review(anime_id):
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("You must be signed in to submit a review.", category="warning")
        return redirect(url_for('signin_page'))

    # Get review data from the form
    score = request.form.get('score')
    comment = request.form.get('comment')

    # Get the user_id from the session
    user_id = session.get('user_id')

    # Validate form data
    if not score or not comment:
        flash("Score and comment are required!", category="danger")
        return redirect(url_for('anime_page', anime_id=anime_id))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('anime_page', anime_id=anime_id))

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Anime_Scores (user_id, anime_id, score, comment)
            VALUES (%s, %s, %s, %s)
        """, (user_id, anime_id, score, comment))
        connection.commit()
        flash("Your review has been submitted!", category="success")
    except Error as e:
        flash(f"Failed to submit review: {e}", category="danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('anime_page', anime_id=anime_id))

def delete_review(score_id):
    user_id = session.get('user_id', None)
    if not user_id:
        flash("You must be signed in to delete a review.", category="warning")
        return redirect(url_for('signin_page'))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('anime_page', anime_id=request.form.get('anime_id')))

    try:
        cursor = connection.cursor(dictionary=True)

        # Check if the review belongs to the logged-in user
        cursor.execute("""
            SELECT user_id FROM Anime_Scores
            WHERE score_id = %s
        """, (score_id,))
        review = cursor.fetchone()

        if not review or review['user_id'] != user_id:
            flash("You are not authorized to delete this review.", category="danger")
            return redirect(url_for('anime_page', anime_id=request.form.get('anime_id')))

        # Delete the review
        cursor.execute("""
            DELETE FROM Anime_Scores
            WHERE score_id = %s AND user_id = %s
        """, (score_id, user_id))
        connection.commit()

        flash("Review deleted successfully!", category="success")
    except Error as e:
        flash(f"Failed to delete review: {e}", category="danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('anime_page', anime_id=request.form.get('anime_id')))

def edit_review(score_id):
    user_id = session.get('user_id', None)
    if not user_id:
        flash("You must be signed in to edit your review.", category="warning")
        return redirect(url_for('signin_page'))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('anime_page', anime_id=request.form.get('anime_id')))

    try:
        cursor = connection.cursor(dictionary=True)

        if request.method == 'POST':
            # Update the review in the database
            new_score = request.form.get('score')
            new_comment = request.form.get('comment')
            anime_id = request.form.get('anime_id')

            if not new_score or not new_comment:
                flash("Both score and comment are required.", category="danger")
                return redirect(url_for('anime_page', anime_id=anime_id))

            cursor.execute("""
                UPDATE Anime_Scores
                SET score = %s, comment = %s
                WHERE score_id = %s AND user_id = %s
            """, (new_score, new_comment, score_id, user_id))
            connection.commit()

            flash("Review updated successfully!", category="success")
            return redirect(url_for('anime_page', anime_id=anime_id))
        else:
            # Fetch the review to edit
            cursor.execute("""
                SELECT scores.score_id, scores.score, scores.comment, scores.anime_id
                FROM Anime_Scores AS scores
                WHERE scores.score_id = %s AND scores.user_id = %s
            """, (score_id, user_id))
            review = cursor.fetchone()

            if not review:
                flash("Review not found or you do not have permission to edit it.", category="danger")
                return redirect(url_for('anime_page', anime_id=request.args.get('anime_id')))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('edit_review.html', review=review)

def like_review(score_id):
    user_id = session.get('user_id', None)
    if not user_id:
        flash("You must be signed in to like a review.", category="warning")
        return redirect(url_for('signin_page'))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('anime_page', anime_id=request.form.get('anime_id')))

    try:
        cursor = connection.cursor(dictionary=True)
        anime_id = request.form.get('anime_id')

        # Check if the user has already interacted with this review
        cursor.execute("""
            SELECT action FROM Review_Interactions
            WHERE user_id = %s AND score_id = %s
        """, (user_id, score_id))
        interaction = cursor.fetchone()

        if interaction:
            if interaction['action'] == 'like':
                flash("You have already liked this review.", category="info")
            else:
                # Update interaction from dislike to like
                cursor.execute("""
                    UPDATE Review_Interactions
                    SET action = 'like'
                    WHERE user_id = %s AND score_id = %s
                """, (user_id, score_id))
                cursor.execute("""
                    UPDATE Anime_Scores
                    SET likes = likes + 1, dislikes = dislikes - 1
                    WHERE score_id = %s
                """, (score_id,))
                connection.commit()
                flash("Your reaction has been updated to like.", category="success")
        else:
            # Insert a new like interaction
            cursor.execute("""
                INSERT INTO Review_Interactions (user_id, score_id, action)
                VALUES (%s, %s, 'like')
            """, (user_id, score_id))
            cursor.execute("""
                UPDATE Anime_Scores
                SET likes = likes + 1
                WHERE score_id = %s
            """, (score_id,))
            connection.commit()
            flash("You liked the review!", category="success")

    except Error as e:
        flash(f"Failed to like the review: {e}", category="danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('anime_page', anime_id=anime_id))

def dislike_review(score_id):
    user_id = session.get('user_id', None)
    if not user_id:
        flash("You must be signed in to dislike a review.", category="warning")
        return redirect(url_for('signin_page'))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('anime_page', anime_id=request.form.get('anime_id')))

    try:
        cursor = connection.cursor(dictionary=True)
        anime_id = request.form.get('anime_id')

        # Check if the user has already interacted with this review
        cursor.execute("""
            SELECT action FROM Review_Interactions
            WHERE user_id = %s AND score_id = %s
        """, (user_id, score_id))
        interaction = cursor.fetchone()

        if interaction:
            if interaction['action'] == 'dislike':
                flash("You have already disliked this review.", category="info")
            else:
                # Update interaction from like to dislike
                cursor.execute("""
                    UPDATE Review_Interactions
                    SET action = 'dislike'
                    WHERE user_id = %s AND score_id = %s
                """, (user_id, score_id))
                cursor.execute("""
                    UPDATE Anime_Scores
                    SET dislikes = dislikes + 1, likes = likes - 1
                    WHERE score_id = %s
                """, (score_id,))
                connection.commit()
                flash("Your reaction has been updated to dislike.", category="success")
        else:
            # Insert a new dislike interaction
            cursor.execute("""
                INSERT INTO Review_Interactions (user_id, score_id, action)
                VALUES (%s, %s, 'dislike')
            """, (user_id, score_id))
            cursor.execute("""
                UPDATE Anime_Scores
                SET dislikes = dislikes + 1
                WHERE score_id = %s
            """, (score_id,))
            connection.commit()
            flash("You disliked the review!", category="success")

    except Error as e:
        flash(f"Failed to dislike the review: {e}", category="danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('anime_page', anime_id=anime_id))

def top_100_page():
    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return render_template('top_100.html', top_animes=[])

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT ai.anime_id, ai.anime_name, ai.type_anime, ai.synopsis, 
                   AVG(ascore.score) as avg_score
            FROM Anime_Information ai
            JOIN Anime_Scores ascore ON ai.anime_id = ascore.anime_id
            GROUP BY ai.anime_id
            ORDER BY avg_score DESC
            LIMIT 100
        """)
        top_animes = cursor.fetchall()
    except Error as e:
        flash(f"Query failed: {e}", category="danger")
        top_animes = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('top_100.html', top_animes=top_animes)


def search():
    search_query = request.args.get('query')

    # If the search term is empty
    if not search_query:
        flash("Please enter an anime name to search.", category="warning")
        return redirect(url_for('index_page'))


    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('index_page'))

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT ai.anime_id, ai.anime_name, ai.english_name
            FROM Anime_Information ai
            WHERE LOWER(ai.anime_name) LIKE LOWER(CONCAT('%', %s, '%'))
            ORDER BY LENGTH(ai.anime_name)
        """, (search_query,))

        results = cursor.fetchall()

        if results:
            return render_template('search_results.html', results=results, query=search_query)
        else:
            # No anime found
            flash(f"No anime found with the name '{search_query}'", category="warning")
            return redirect(url_for('index_page'))

    except Error as e:
        flash(f"Query failed: {e}", category="danger")
        return redirect(url_for('index_page'))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def signin_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        connection = get_db_connection()
        if connection is None:
            flash("Database connection failed!", "danger")
            return render_template("signin.html")

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                session["logged_in"] = True
                flash("Signin successful!", "success")
                return redirect(url_for("index_page"))
            else:
                flash("Invalid username or password.", "danger")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template("signin.html")

def signup_page():
    if request.method == "POST":
        # Collect form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        gender = request.form.get("gender")
        birthday = request.form.get("birthday") or None
        place = request.form.get("place") or None

        # Validate password confirmation
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")

        # Connect to the database
        connection = get_db_connection()
        if connection is None:
            flash("Database connection failed!", "danger")
            return render_template("signup.html")

        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if the username already exists
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash("Username already exists. Please choose a different one.", "danger")
                return render_template("signup.html")

            # Hash the password
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

            # Insert new user into the database
            cursor.execute("""
                INSERT INTO Users (username, password, gender, birthday, place, days_watched)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, hashed_password, gender, birthday, place, 0))  # Default days_watched to 0
            connection.commit()
            flash("Signup successful! Please sign in.", "success")
            return redirect(url_for("signin_page"))
        except Error as e:
            flash(f"Signup failed: {e}", "danger")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template("signup.html")


def profile_page():
    if 'user_id' not in session:
        flash("You need to log in to view your profile.", "warning")
        return redirect(url_for("signin_page"))

    connection = get_db_connection()
    if connection is None:
        flash("Database connection failed!", "danger")
        return redirect(url_for("index_page"))

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", (session['user_id'],))
        user = cursor.fetchone()

        if user:
            return render_template("profile.html", user=user)
        else:
            flash("User not found.", "danger")
            return redirect(url_for("index_page"))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_profile():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("You must be logged in to update your profile.", "warning")
        return redirect(url_for('signin_page'))

    # Get form data
    username = request.form.get('username')
    gender = request.form.get('gender')
    birthday = request.form.get('birthday') or None  # Handle empty birthday
    place = request.form.get('place') or None        # Handle empty place

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check if the new username already exists (excluding the current user)
        cursor.execute("""
            SELECT * FROM Users 
            WHERE username = %s AND user_id != %s
        """, (username, session['user_id']))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("This username is already taken. Please choose a different one.", "danger")
            return redirect(url_for('profile_page'))

        # Update user data in the database
        cursor.execute("""
            UPDATE Users
            SET username = %s, gender = %s, birthday = %s, place = %s
            WHERE user_id = %s
        """, (username, gender, birthday, place, session['user_id']))
        connection.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile_page'))
    except Error as e:
        flash(f"An error occurred while updating the profile: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('profile_page'))

def change_password():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("You must be logged in to change your password.", "warning")
        return redirect(url_for('signin_page'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if new_password != confirm_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('profile_page'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT password FROM Users WHERE user_id = %s", (session['user_id'],))
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password'], current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('profile_page'))

        hashed_password = generate_password_hash(new_password, method="pbkdf2:sha256")
        cursor.execute("UPDATE Users SET password = %s WHERE user_id = %s", (hashed_password, session['user_id']))
        connection.commit()

        flash("Password changed successfully!", "success")
        return redirect(url_for('profile_page'))
    except Error as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def delete_account():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("You must be logged in to delete your account.", "warning")
        return redirect(url_for('signin_page'))

    # Delete user from the database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Users WHERE user_id = %s", (session['user_id'],))
    connection.commit()
    cursor.close()
    connection.close()

    # Clear session and redirect
    session.clear()
    flash("Your account has been deleted.", "info")
    return redirect(url_for('signin_page'))

def logout():
    # Clear all session data
    session.clear()
    # Provide feedback to the user
    flash("You have been logged out.", "info")
    # Redirect to the home or sign-in page
    return redirect(url_for('signin_page'))


def add_to_watchlist(anime_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be signed in to add an anime to your watchlist.", category="warning")
        return redirect(url_for('signin_page'))

    status = request.form.get('status', 'plan-to-watch')  # Default to "plan-to-watch"
    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('anime_page', anime_id=anime_id))

    try:
        cursor = connection.cursor()

        # Check if the anime is already in the user's watchlist
        cursor.execute("""
            SELECT * FROM Watchlist
            WHERE user_id = %s AND anime_id = %s
        """, (user_id, anime_id))
        existing_entry = cursor.fetchone()

        if existing_entry:
            flash("This anime is already in your watchlist.", category="info")
        else:
            # Add anime to watchlist
            cursor.execute("""
                INSERT INTO Watchlist (user_id, anime_id, status)
                VALUES (%s, %s, %s)
            """, (user_id, anime_id, status))
            connection.commit()
            flash("Anime added to your watchlist!", category="success")
    except Error as e:
        flash(f"Error adding anime to watchlist: {e}", category="danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('anime_page', anime_id=anime_id))

def my_list():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be signed in to view your watchlist.", category="warning")
        return redirect(url_for('signin_page'))

    search_query = request.form.get('search', '').strip()  # Get the search query
    filter_status = request.form.get('filter_status', '')  # Get the filter status

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('home'))

    try:
        cursor = connection.cursor(dictionary=True)

        # Fetch filtered and/or searched watchlist
        query = """
            SELECT wl.status, wl.added_date, ai.anime_id, ai.anime_name, ai.english_name, ai.genres, ai.type_anime
            FROM Watchlist wl
            JOIN Anime_Information ai ON wl.anime_id = ai.anime_id
            WHERE wl.user_id = %s
        """
        params = [user_id]

        if filter_status:
            query += " AND wl.status = %s"
            params.append(filter_status)

        if search_query:
            query += " AND (ai.anime_name LIKE %s OR ai.english_name LIKE %s)"
            params.extend([f'%{search_query}%', f'%{search_query}%'])

        query += " ORDER BY wl.added_date DESC"

        cursor.execute(query, tuple(params))
        watchlist = cursor.fetchall()
    except Error as e:
        flash(f"Failed to fetch watchlist: {e}", category="danger")
        watchlist = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('my_list.html', watchlist=watchlist, search_query=search_query, filter_status=filter_status)

def remove_from_watchlist(anime_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be signed in to manage your watchlist.", category="warning")
        return redirect(url_for('signin_page'))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('my_list'))

    try:
        cursor = connection.cursor()
        # Remove the anime from the user's watchlist
        cursor.execute("""
            DELETE FROM Watchlist
            WHERE user_id = %s AND anime_id = %s
        """, (user_id, anime_id))
        connection.commit()
        flash("Anime removed from your watchlist!", category="success")
    except Error as e:
        flash(f"Error removing anime from watchlist: {e}", category="danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('my_list'))

def update_watchlist_status(anime_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be signed in to manage your watchlist.", category="warning")
        return redirect(url_for('signin_page'))

    new_status = request.form.get('status')
    if not new_status:
        flash("Invalid status selected.", category="danger")
        return redirect(url_for('my_list'))

    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return redirect(url_for('my_list'))

    try:
        cursor = connection.cursor()
        # Update the status of the anime in the user's watchlist
        cursor.execute("""
            UPDATE Watchlist
            SET status = %s
            WHERE user_id = %s AND anime_id = %s
        """, (new_status, user_id, anime_id))
        connection.commit()
        flash("Watchlist status updated successfully!", category="success")
    except Error as e:
        flash(f"Error updating watchlist status: {e}", category="danger")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('my_list'))

