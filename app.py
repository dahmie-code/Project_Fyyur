# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json

import babel
import dateutil.parser
from babel import dates
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *
import sys


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    venue_list = db.session.query(Venue).all()
    data = []

    for venue in venue_list:
        data.append({
            'city': venue.city,
            'state': venue.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name
            }]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    venue_list = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

    count = len(venue_list)
    venue_data = []
    #
    for venue in venue_list:
        venue_data.append({
            "id": venue.id,
            "name": venue.name,
        })

    response = {'count': count, 'data': venue_data}

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue_lists = Venue.query.get(venue_id)

    query_past_shows = Show.query.join(Venue).filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).all()
    query_upcoming_shows = Show.query.join(Venue).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).all()

    details = []

    past_shows = []
    for past_show in query_past_shows:
        past_shows.append({
            'artist_id': past_show.artist_id,
            'artist_name': past_show.artist.name,
            'artist_image_link': past_show.artist.image_link,
            'start_time': str(past_show.start_time)
        })

    upcoming_shows = []
    for upcoming_show in query_upcoming_shows:
        upcoming_shows.append({
            'artist_id': upcoming_show.artist_id,
            'artist_name': upcoming_show.artist.name,
            'artist_image_link': upcoming_show.artist.image_link,
            'start_time': str(upcoming_show.start_time)
        })

    details.append({
        'id': venue_lists.id,
        'name': venue_lists.name,
        'genres': venue_lists.genres,
        'address': venue_lists.address,
        'city': venue_lists.city,
        'state': venue_lists.state,
        'phone': venue_lists.phone,
        'website': venue_lists.website_link,
        'facebook_link': venue_lists.facebook_link,
        'seeking_talent': venue_lists.seeking_talent,
        'seeking_description': venue_lists.seeking_description,
        'image_link': venue_lists.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    })

    data = list(filter(lambda d: d['id'] == venue_id, details))[0]
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            phone=form.phone.data,
            state=form.state.data,
            address=form.address.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully deleted!')
    except:
        flash('Venue ' + request.form['name'] + ' deletion Unsuccessful!')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = db.session.query(Artist).all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

    count = len(artists)
    data = []

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    response = {'count': count, 'data': data}

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artists = Artist.query.get(artist_id)

    query_past_shows = Show.query.join(Artist).filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).all()
    query_upcoming_shows = Show.query.join(Artist).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).all()

    details = []

    past_shows = []
    for past_show in query_past_shows:
        past_shows.append({
            'venue_id': past_show.venue_id,
            'venue_name': past_show.venue.name,
            'venue_image_link': past_show.venue.image_link,
            'start_time': str(past_show.start_time)
        })

    upcoming_shows = []
    for upcoming_show in query_upcoming_shows:
        upcoming_shows.append({
            'venue_id': upcoming_show.venue_id,
            'venue_name': upcoming_show.venue.name,
            'venue_image_link': upcoming_show.venue.image_link,
            'start_time': str(upcoming_show.start_time)
        })

    details.append({
        "id": artists.id,
        "name": artists.name,
        "genres": artists.genres,
        "city": artists.city,
        "state": artists.state,
        "phone": artists.phone,
        "website": artists.website_link,
        "facebook_link": artists.facebook_link,
        "seeking_venue": artists.seeking_venue,
        "seeking_description": artists.seeking_description,
        "image_link": artists.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    })
    data = list(filter(lambda d: d['id'] == artist_id, details))[0]
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

    artist = {
        'id': artist.id,
        'name': artist.name,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'genres': artist.genres,
        'website_link': artist.website_link,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.looking_for_venues,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    artists = Artist.query.get(artist_id)
    try:
        artists.name = form.name.data,
        artists.city = form.city.data,
        artists.state = form.state.data,
        artists.genres = request.form.getlist('genres'),
        artists.phone = form.phone.data,
        artists.website_link = form.website_link.data,
        artists.facebook_link = form.facebook_link.data,
        artists.looking_for_venues = form.seeking_venue.data,
        artists.seeking_description = form.seeking_description.data,
        artists.image_link = form.image_link.data
        artists.update()

        db.session.commit()
        flash('Artist ' + request.form['name'] + ' updated Successfully!')

    except:
        flash('An error Occurred ' + request.form['name'] + ' updated Unsuccessful!')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    venue = {
        'id': venue.id,
        'name': venue.name,
        'phone': venue.phone,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'genres': venue.genres,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link
    }


    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    try:
        venue.name = form.name.data,
        venue.city = form.city.data,
        venue.state = form.state.data,
        venue.phone = form.phone.data,
        venue.genres = form.genres.data,
        venue.address = form.address.data,
        venue.seeking_talent = form.seeking_talent.data,
        venue.seeking_description = form.seeking_description.data,
        venue.website_link = form.website_link.data,
        venue.image_link = form.image_link.data,
        venue.facebook_link = form.facebook_link.data,
        venue.update()

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' updated Successfully!')

    except:
        flash('An error Occurred ' + request.form['name'] + ' updated Unsuccessful!')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            phone=form.phone.data,
            state=form.state.data,
            genres=request.form.getlist('genres'),
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    shows = db.session.query(Show).all()
    data = []

    for show in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time)
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
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)

    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=str(form.start_time.data),
        )
        db.session.add(show)
        db.session.commit()
        flash('Show created Successfully')
    except:
        flash('An error occurred. unable to create Show')
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
