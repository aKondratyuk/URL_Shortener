from flask import Blueprint, render_template, request, redirect
from datetime import datetime, timedelta

from .extension import db
from .models import Link
from .authorization import requires_auth

short = Blueprint('short', __name__)


@short.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    if datetime.now() > link.expiration_date:
        db.session.delete(link)
        db.session.commit()
        return "Your link has been expired :("
    else:
        link.visits = link.visits + 1
        db.session.commit()

    return redirect(link.original_url)


@short.route('/')
@requires_auth
def index():
    return render_template('index.html')


@short.route('/add_link', methods=['POST'])
@requires_auth
def add_link():
    original_url = request.form['original_url']
    days = request.form['lifetime']
    if days:
        lifetime = datetime.now() + timedelta(days=int(days))
    else:
        lifetime = datetime.now() + timedelta(days=90)
        
    link = Link(original_url=original_url, expiration_date=lifetime)
    db.session.add(link)
    db.session.commit()

    return render_template('link_added.html', new_link=link.short_url, original_url=link.original_url)


@short.route('/stats')
@requires_auth
def stats():
    links = Link.query.all()

    return render_template('stats.html', links=links)


@short.errorhandler(404)
def page_not_found(e):
    return '', 404
