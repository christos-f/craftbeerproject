from craft_app.app import db, import_beers,import_reviews

# db.drop_all()
db.create_all()
import_beers()
import_reviews()
