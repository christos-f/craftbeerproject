import json
from sqlalchemy import func
from flask import Flask, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import redirect
from collections import defaultdict

app = Flask(__name__)
print(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/beer_test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Beer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    brewery = db.Column(db.String(128), nullable=False)
    style = db.Column(db.String(128), nullable=False)
    abv = db.Column(db.Float(), nullable=True)
    score = db.Column(db.Float(), nullable=False)
    avg_score = db.Column(db.Float(), nullable=False)
    ratings = db.Column(db.Integer(), nullable=False)
    availability = db.Column(db.String(32), nullable=True)
    brew_state = db.Column(db.String(32), nullable=True)
    brew_city = db.Column(db.String(32), nullable=True)
    lat = db.Column(db.Float(), nullable=True)
    long = db.Column(db.Float(), nullable=True)
    reviews = db.relationship('Review', backref=db.backref('beer', lazy=True))

    def __repr__(self):
        return '<Beer %r>' % self.name


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(50), nullable=False)
    beer_id = db.Column(db.Integer, db.ForeignKey('beer.id'), nullable=False)

    def __repr__(self):
        return '<Review %r>' % self.state



def import_beers():
    with open('data/final_data.json') as f:
        data = json.load(f)
    for item in data:
        beer = Beer(name=item['beer_name'],
                    brewery=item['brewery:'],
                    style=item['style'],
                    abv=item['abv'][:-1],
                    score=int(item['score']),
                    avg_score=float(item['avg_score']),
                    ratings=int(item['ratings'].replace(',', '')),
                    availability=item['availability'],
                    brew_state=item['brew_state'],
                    brew_city=item['brew_city'],
                    lat=item['lat'],
                    long=item['long'])
        db.session.add(beer)
    db.session.commit()


def import_reviews():
    with open('data/final_data.json') as f:
        data = json.load(f)
    for item in data:
        beer = Beer.query.filter_by(name=item['beer_name']).first()
        for state in item['states']:
            review = Review(state=state, beer_id=beer.id)
            db.session.add(review)
    db.session.commit()


def build_map_data(counts):
    with open('data/data.json') as f:
        map_data = json.load(f)
    features = map_data['features']
    for location in features:
        state_name = location['properties']['name']
        location['properties']['density'] = counts.get(state_name, 0)
    return map_data


@app.route('/')
def home():
    return app.config['SQLALCHEMY_DATABASE_URI']

@app.route('/map')
def map_beers():
    review_counts = Review.query.with_entities(Review.state, func.count(Review.state)).group_by(Review.state).all()
    reviews_per_region = {review[0]: review[1] for review in review_counts}
    data = build_map_data(reviews_per_region)
    return render_template("index.html", data=json.dumps(data))



if __name__ == '__main__':
    db.create()
    import_beers()
    import_reviews()
    app.run()
