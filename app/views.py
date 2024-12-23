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
    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return render_template('anime_page.html', anime_info={}, anime_metadata={}, studio_id=None)

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT ai.anime_name, ai.english_name, ai.other_name, ai.synopsis, ai.type_anime, ai.genres,
                   am.episodes, am.aired, am.premiered, am.source,
                   ap.studio_id
            FROM Anime_Information ai
            JOIN Anime_Metadata am ON ai.anime_id = am.anime_id
            LEFT JOIN Anime_Production ap ON ai.anime_id = ap.anime_id
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
            studio_id = result['studio_id']  # This is the studio ID related to the anime
            
            cursor.execute("""
            SELECT u.username, u.user_id, scores.anime_id, scores.score, scores.comment
            FROM Anime_Scores AS scores
            LEFT JOIN Users AS u ON scores.user_id = u.user_id
            WHERE scores.anime_id = %s
            LIMIT 5
            """, (anime_id,))

            review_result = cursor.fetchall()
        else:
            anime_info = {}
            anime_metadata = {}
            studio_id = None
            review_result = []
    except Error as e:
        flash(f"Query failed: {e}", category="danger")
        anime_info = {}
        anime_metadata = {}
        studio_id = None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('anime_page.html', anime_info=anime_info, anime_metadata=anime_metadata, studio_id=studio_id
                           , reviews=review_result)


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
            cursor.execute("SELECT * FROM Accounts WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
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
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        connection = get_db_connection()
        if connection is None:
            flash("Database connection failed!", "danger")
            return render_template("signup.html")

        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Accounts (username, password) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            flash("Signup successful! Please signin.", "success")
            return redirect(url_for("signin_page"))
        except Error as e:
            flash(f"Signup failed: {e}", "danger")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template("signup.html")