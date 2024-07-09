from app import db

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(10), nullable=False)
    actors = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'