from flask import render_template, request, redirect, url_for, flash, current_app
from database import get_db_connection
from mysql.connector import Error


def index_page():
    connection = get_db_connection()
    if connection is None:
        flash("Couldn't connect to the database!", category="danger")
        return render_template('index.html', anime_information=[])

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM anime_information")
        anime_information = cursor.fetchall()
    except Error as e:
        flash(f"Query failed: {e}", category="danger")
        anime_information = []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('index.html', anime_information=anime_information)


def add_anime_page():
    if request.method == "POST":
        name = request.form.get("name")
        english_name = request.form.get("english_name")
        other_name = request.form.get("other_name")
        synopsis = request.form.get("synopsis")
        type = request.form.get("type")

        # Form validation
        if not name or not synopsis:
            flash("Name and Synopsis are necessary.", "warning")
            return render_template("add_anime.html")

        connection = get_db_connection()
        if connection is None:
            flash("Couldn't connect to the database!", "danger")
            return render_template("add_anime.html")

        # Adding animes to the database
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO anime_information (name, english_name, other_name, synopsis, type) VALUES (%s, %s, %s, %s, %s)",
                (name, english_name, other_name, synopsis, type),
            )
            connection.commit()
            flash("Anime added successfully!", "success")
            return redirect(url_for("index_page"))  # Correct endpoint name here
        except Error as e:
            flash(f"An exception occurred while adding the anime: {e}", "danger")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template("add_anime.html")
