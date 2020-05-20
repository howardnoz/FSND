#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    venue_genres = db.relationship('VenueGenre', backref='venue', lazy=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description= db.Column(db.String(120))
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    #def __repr__(self):
    #    return f'<Venue id: {self.id}, name: {self.name}, city: {self.city}>'

class VenueGenre(db.Model):
    __tablename__ = 'VenueGenre'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(120), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description= db.Column(db.String(120))
    artist_genres = db.relationship('ArtistGenre', backref='artist', lazy=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

class ArtistGenre(db.Model):
    __tablename__ = 'ArtistGenre'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(120), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artists = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venues = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data=[]
  cities = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  for city in cities:
    venues_by_city = Venue.query.filter_by(city=city[0]).all()
    jsons=[]
    for v in venues_by_city:
      #num_shows should be aggregated based on number of upcoming shows per venue.
      upcoming_shows_query = Show.query.filter(Show.venues==v.id, Show.start_time > datetime.now())
      upcoming_shows_count = upcoming_shows_query.count()

      jsons.append({'id': v.id,'name': v.name, 'num_upcoming_shows':upcoming_shows_count})
    data.append({'city':city[0], 'state':city[1], 'venues': jsons})

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form['search_term']
  search = '%'+search+'%'
  venues_query = Venue.query.filter(Venue.name.ilike(search))
  venues = venues_query.all()
  venues_count = venues_query.count()

  data=[]
  for venue in venues:
    upcoming_shows_query = Show.query.filter(Show.venues==venue.id, Show.start_time > datetime.now())
    upcoming_shows_count = upcoming_shows_query.count()
    data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": upcoming_shows_count,
    })
  response = {"count": venues_count, "data":data}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  shows = Show.query.filter(Show.venues==venue.id).all()

  past_shows = []
  upcoming_shows = []
  for s in shows:
    artist = Artist.query.filter_by(id=s.artists).first()
    json = { 
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link":artist.image_link,
      "start_time": str(s.start_time)
    }
    if (s.start_time<datetime.now()):
      past_shows.append(json)        
    else:
      upcoming_shows.append(json)

  genres =[]
  for g in venue.venue_genres:
    genres.append(g.genre)

  data=[{
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }]
  data = list(filter(lambda d: d['id'] == venue_id, data))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # on successful db insert, flash success
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    address = request.form['address']
    image_link = request.form['image_link']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_talent = "seeking_talent" in request.form
    seeking_description= request.form['seeking_description']
    new_venue = Venue(name=name, city=city, state=state, phone=phone, address=address, website=website, image_link=image_link, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)

    genres = ['Classical', 'Country']
    for g in genres:
      new_venue_genre = VenueGenre(genre=g, venue_id=new_venue.id)
      db.session.add(new_venue_genre)

    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()

    return {'response':'success', 'redirecturl': url_for('index')}

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  results = Artist.query.all()
  data=[]
  for artist in results:
    data.append({'id':artist.id, 'name':artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form['search_term']
  search = '%'+search+'%'
  artists_query= Artist.query.filter(Artist.name.ilike(search))
  artists= artists_query.all()
  artists_count= artists_query.count()

  data=[]
  for artist in artists:
    upcoming_shows_query = Show.query.filter(Show.artists==artist.id, Show.start_time > datetime.now())
    upcoming_shows_count = upcoming_shows_query.count()
    data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": upcoming_shows_count,
    })
  response = {"count": artists_count, "data":data}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data=[]
  artists = Artist.query.filter_by(id=artist_id).all()
  shows = Show.query.filter_by(artists=artist_id).all()

  past_shows = []
  upcoming_shows = []
  for s in shows:
    venue = Venue.query.filter_by(id=s.venues).first()
    json = { 
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(s.start_time)
    }
    if (s.start_time<datetime.now()):
      past_shows.append(json)        
    else:
      upcoming_shows.append(json)

  for artist in artists:
      genres = []
      for g in artist.artist_genres:
        genres.append(g.genre)

      data.append({
        "id": artist_id,
        "name": artist.name,
        "genres": genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      })
  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist= Artist.query.filter_by(id=artist_id).first()
  data={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.artist_genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  error = False

  try:
    artist = Artist.query.filter_by(id=artist_id).first()

    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state= request.form['state']
    artist.city= request.form['city']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_description= request.form['seeking_description']
    artist.seeking_venue = "seeking_venue" in request.form
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Changes to artist ' + request.form['name'] + ' could not be saved.')
  else:
    flash('Artist' + request.form['name'] + ' changes were successfully saved!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
      Artist.query.filter_by(id=artist_id).delete()
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()

    return {'response':'success', 'redirecturl': url_for('index')}

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.filter_by(id=venue_id).first()
  genres= Venue.venue_genres
  venue={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.venue_genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  error = False

  try:
    venue = Venue.query.filter_by(id=venue_id).first()

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state= request.form['state']
    venue.city= request.form['city']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form['genres']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_description= request.form['seeking_description']
    venue.seeking_talent= "seeking_talent" in request.form
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Changes to venue ' + request.form['name'] + ' could not be saved.')
  else:
    flash('The venue for ' + request.form['name'] + ' changes were successfully saved!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # on successful db insert, flash success
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    seeking_description = request.form['seeking_description']
    seeking_venue = "seeking_venue" in request.form
    website = request.form['website']
    new_artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link, seeking_description=seeking_description, seeking_venue=seeking_venue, website=website)
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    data = []
  finally:
    db.session.close()

  data = new_artist

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.all()
  data=[]
  for show in shows:
    venue = Venue.query.filter_by(id=show.venues).first()
    artist = Artist.query.filter_by(id=show.artists).first()
    data.append({
      "venue_id": show.venues,
      "venue_name": venue.name,
      "artist_id": show.artists,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%H:%M:%S")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

  # on successful db insert, flash success
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False

  try:
    venues= request.form['venue_id']
    artists = request.form['artist_id']
    artist_name = Artist.query.filter_by(id=artists).first().name
    start_time = request.form['start_time']
    new_show = Show(venues=venues,artists=artists, start_time=start_time) 
    db.session.add(new_show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Show for ' + request.form['artist_id'] + ' could not be listed.')
  else:
    flash('Show for ' + artist_name + ' was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
