from flask import request, jsonify, render_template, redirect, url_for
from app import app, db
from models import Movie
import secrets
import csv
import docx
from io import StringIO
from sqlalchemy import or_, func, asc

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        year = int(request.form['year'])
        format = request.form['format']
        actors = request.form['actors']
        
        
        code = secrets.token_hex(5)
        
        if not Movie.query.filter_by(code=code).first():
            new_movie = Movie(code=code, title=title, year=year, format=format, actors=actors)
            db.session.add(new_movie)
            db.session.commit()
            print(f"Додано новий фільм: {title}")
        else:
            print(f"Пропуск фільму з існуючим кодом: {code}")
        
        return redirect(url_for('index'))

    movies = Movie.query.order_by(asc(func.lower(Movie.title))).all()
    print(f"Кількість фільмів у базі даних: {len(movies)}")
    return render_template('index.html', movies=movies)

@app.route('/sort', methods=['GET'])
def sort_movies():
    movies = Movie.query.all()
    sorted_movies = []

    for movie in movies:
        sorted_movies.append(movie)

    sorted_movies.sort(key=lambda x: x.title.lower())

    return render_template('index.html', movies=sorted_movies)

@app.route('/delete/<string:code>', methods=['GET'])
def delete(code):
    movie = Movie.query.filter_by(code=code).first()
    if movie:
        db.session.delete(movie)
        db.session.commit()
        print(f"Видалено фільм: {movie.title}")
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query'].lower()
        print(f"Пошуковий запит: {query}")

        movies = Movie.query.all()
        search_results = []

        for movie in movies:
            if query in movie.title.lower() or query in movie.actors.lower():
                search_results.append(movie)

        print(f"Знайдено {len(search_results)} фільмів")

        return render_template('search.html', movies=search_results)

    return render_template('search.html')

@app.route('/import', methods=['GET', 'POST'])
def import_movies():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            if file.filename.endswith('.csv'):
                movies = import_from_csv(file)
            elif file.filename.endswith('.doc') or file.filename.endswith('.docx'):
                movies = import_from_doc(file)
            elif file.filename.endswith('.txt'):
                movies = import_from_txt(file)
            else:
                return 'Будь ласка, завантажте файл у форматі CSV, DOC/DOCX або TXT', 400

            unique_movies = []
            for movie in movies:
                existing_movie = Movie.query.filter_by(title=movie.title).first()
                if not existing_movie:
                    unique_movies.append(movie)
                else:
                    print(f"Пропуск фільму з існуючою назвою: {movie.title}")

            if unique_movies:
                db.session.add_all(unique_movies)
                db.session.commit()
                print(f"Імпортовано {len(unique_movies)} фільмів")
                return redirect(url_for('index'))
            else:
                print("Фільми не додані")
                return "Не вдалося імпортувати фільми", 400
        else:
            return "Файл не завантажено", 400

    return render_template('import.html')

@app.route('/movies/<string:code>', methods=['GET'])
def get_movie(code):
    movie = Movie.query.filter_by(code=code).first()
    if movie:
        return render_template('movie.html', movie=movie)
    return jsonify({'message': 'Movie not found'}), 404

def import_from_csv(file):
    movies = []
    try:
        file_contents = file.read().decode('utf-8')
        reader = csv.DictReader(StringIO(file_contents))
        for row in reader:
            code = secrets.token_hex(5)
            
            
            existing_movie = Movie.query.filter_by(title=row['Назва']).first()
            if not existing_movie:
                movie = Movie(
                    code=code,
                    title=row['Назва'],
                    year=int(row['Рік']),
                    format=row['Формат'],
                    actors=row['Актори']
                )
                movies.append(movie)
                print(f"Додано новий фільм: {row['Назва']}")
            else:
                print(f"Пропуск фільму з існуючою назвою: {row['Назва']}")
    except (ValueError, KeyError, UnicodeDecodeError) as e:
        print(f'Помилка під час завантаження CSV-файлу: {e}')
        return []
    return movies

def parse_line(line):
    delimiters = ['|', ',', ' ', ';', ]
    for delimiter in delimiters:
        if delimiter in line:
            return line.split(delimiter)
    return [line]

def import_from_doc(file):
    movies = []
    try:
        doc = docx.Document(file)
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                fields = parse_line(paragraph.text.strip())
                if len(fields) == 4:
                    title, year, format, actors = fields
                    code = secrets.token_hex(5)
                    existing_movie = Movie.query.filter_by(title=title.strip()).first()
                    if not existing_movie:
                        movie = Movie(
                            code=code,
                            title=title.strip(),
                            year=int(year.strip()),
                            format=format.strip(),
                            actors=actors.strip()
                        )
                        movies.append(movie)
                        print(f"Додано новий фільм: {title.strip()}")
                    else:
                        print(f"Пропуск фільму з існуючою назвою: {title.strip()}")
    except Exception as e:
        print(f'Помилка під час завантаження DOC/DOCX-файлу: {e}')
        return []
    return movies

def import_from_txt(file):
    movies = []
    try:
        file_contents = file.read().decode('utf-8')
        for line in file_contents.splitlines():
            if line.strip():
                fields = parse_line(line.strip())
                if len(fields) == 4:
                    title, year, format, actors = fields
                    code = secrets.token_hex(5)
                    existing_movie = Movie.query.filter_by(title=title.strip()).first()
                    if not existing_movie:
                        movie = Movie(
                            code=code,
                            title=title.strip(),
                            year=int(year.strip()),
                            format=format.strip(),
                            actors=actors.strip()
                        )
                        movies.append(movie)
                        print(f"Додано новий фільм: {title.strip()}")
                    else:
                        print(f"Пропуск фільму з існуючою назвою: {title.strip()}")
    except Exception as e:
        print(f'Помилка під час завантаження TXT-файлу: {e}')
        return []
    return movies