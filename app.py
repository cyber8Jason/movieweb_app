from flask import Flask, request, jsonify, render_template, redirect, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.models import db
from services.omdb_service import OMDBService
from dotenv import load_dotenv
import os
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__, instance_relative_config=True)

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "movieweb.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and data manager
db.init_app(app)
data_manager = SQLiteDataManager()

with app.app_context():
    try:
        db.create_all()
        data_manager.init_app(app)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

# Initialize OMDB service
try:
    omdb_service = OMDBService.create_from_env()
    print("OMDB service initialized successfully!")
except Exception as e:
    print(f"Error initializing OMDB service: {str(e)}")

# Error Handler
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html',
                         code=404,
                         message="Page Not Found",
                         description="The requested page could not be found."), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback on database errors
    return render_template('error.html',
                         code=500,
                         message="Internal Server Error",
                         description="An unexpected error has occurred."), 500

@app.errorhandler(HTTPException)
def handle_http_error(error):
    return render_template('error.html',
                         code=error.code,
                         message=error.name,
                         description=error.description), error.code

@app.errorhandler(SQLAlchemyError)
def handle_db_error(error):
    db.session.rollback()  # Rollback on database errors
    app.logger.error(f"Database error: {str(error)}")
    return render_template('error.html',
                         code=500,
                         message="Database Error",
                         description="An error occurred during the database operation."), 500

@app.route('/')
def home():
    """Homepage/Dashboard with overview of app features"""
    return render_template('index.html')

@app.route('/users')
def users_list():
    """Display list of all users"""
    users = data_manager.get_all_users()
    return render_template('users_list.html', users=users)

@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """Display a specific user's movie list"""
    user = data_manager.get_user(user_id)
    if not user:
        return render_template('error.html', message="User not found"), 404
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add a new user"""
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            user_id = data_manager.add_user(name)
            return redirect(url_for('users_list'))
        return render_template('add_user.html', error="Username is required")
    return render_template('add_user.html')

@app.route('/api/search_movie')
def search_movie():
    """Search for a movie using OMDB API"""
    try:
        title = request.args.get('title')
        if not title:
            return jsonify({"error": "Movie title is required"}), 400

        movie_data = omdb_service.search_movie(title)
        if movie_data:
            return jsonify(movie_data)
        return jsonify({"error": "Movie not found"}), 404
    except Exception as e:
        app.logger.error(f"OMDB API error: {str(e)}")
        return jsonify({"error": "An error occurred while searching for the movie"}), 500

@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_user_movie(user_id):
    """Add a movie to user's list"""
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return render_template('error.html',
                                code=404,
                                message="User not found",
                                description="The requested user does not exist."), 404

        if request.method == 'POST':
            try:
                # Create the movie first
                movie_id = data_manager.add_movie(
                    name=request.form['name'],
                    director=request.form['director'],
                    year=int(request.form['year']),
                    rating=float(request.form['rating']),
                    poster=request.form.get('poster', '')  # Save the poster URL
                )

                # Add the movie to user's list
                if data_manager.add_user_movie(user_id, movie_id):
                    return redirect(url_for('user_movies', user_id=user_id))

                # If adding fails, delete the movie
                data_manager.delete_movie(movie_id)
                raise ValueError("Could not add movie to user's list")

            except (KeyError, ValueError) as e:
                return render_template('add_movie.html',
                                    user=user,
                                    error="All fields must be filled correctly")

        return render_template('add_movie.html', user=user)
    except Exception as e:
        app.logger.error(f"Error adding movie: {str(e)}")
        return render_template('error.html',
                            code=500,
                            message="Error Adding Movie",
                            description="The movie could not be added."), 500

@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_user_movie(user_id, movie_id):
    """Update a movie in user's list"""
    user = data_manager.get_user(user_id)
    movie = data_manager.get_movie(movie_id)

    if not user or not movie:
        return render_template('error.html', message="User or movie not found"), 404

    if request.method == 'POST':
        try:
            success = data_manager.update_movie(
                movie_id=movie_id,
                name=request.form['name'],
                director=request.form['director'],
                year=int(request.form['year']),
                rating=float(request.form['rating']),
                poster=request.form.get('poster', movie.get('poster', ''))  # Keep existing poster if not updated
            )
            if success:
                return redirect(url_for('user_movies', user_id=user_id))
            return render_template('error.html', message="Update failed"), 400
        except (KeyError, ValueError):
            return render_template('update_movie.html', user=user, movie=movie,
                                error="All fields must be filled correctly")

    return render_template('update_movie.html', user=user, movie=movie)

@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_user_movie(user_id, movie_id):
    """Remove a movie from user's list"""
    if data_manager.remove_user_movie(user_id, movie_id):
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('error.html', message="Could not remove movie"), 400

@app.route('/movie_collections')
def movie_collections():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of movies per page
    search_query = request.args.get('search', '')

    try:
        if search_query:
            # Search with pagination
            movies = data_manager.search_movies(search_query)
        else:
            # All movies with pagination
            movies = data_manager.get_all_movies()

        if not movies and search_query:
            return render_template('movie_collections.html',
                                movies=[],
                                page=1,
                                total_pages=1,
                                search_query=search_query,
                                error=f'No movies found for "{search_query}"')

        # Pagination of results
        total = len(movies)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        movies_page = movies[start_idx:end_idx]
        total_pages = (total + per_page - 1) // per_page

        return render_template('movie_collections.html',
                             movies=movies_page,
                             page=page,
                             total_pages=total_pages,
                             search_query=search_query)

    except Exception as e:
        app.logger.error(f"Error during movie search: {str(e)}")
        return render_template('movie_collections.html',
                             movies=[],
                             page=1,
                             total_pages=1,
                             search_query=search_query,
                             error="An error occurred during the search. Please try again later.")

# API routes for JSON responses
@app.route('/api/movies', methods=['GET'])
def api_get_movies():
    movies = data_manager.get_all_movies()
    return jsonify(movies)

@app.route('/api/users/<int:user_id>/movies', methods=['GET'])
def api_get_user_movies(user_id):
    movies = data_manager.get_user_movies(user_id)
    return jsonify(movies)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
