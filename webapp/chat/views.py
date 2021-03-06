from flask import Response, request, render_template, url_for, redirect, flash, jsonify
from socketio import socketio_manage
from sqlalchemy import and_
from datetime import timedelta

import flask.ext.login as flask_login
import json

from chat import app, db, login_manager
from .models import Family, Sensor, SensorValue, User, UserType, Message
from .namespaces import ChatNamespace
from .utils import get_object_or_404, get_or_create, get_current_time
from .forms import LoginForm


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.email.data, form.password.data)
        if user and authenticated:
            if user.status_code == 0:
                flash(u'Please activate your email address.', 'warning')
                return render_template('login.html', form=form)
            if flask_login.login_user(user, remember=True):
                # flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
        else:
            flash(u'Your email or password is incorrect.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    # flash('Logged out.', 'info')
    return redirect(url_for('index'))


# test controller: not used
@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + str(flask_login.current_user.id)


@app.route('/')
def index():
    """
    Universal Homepage.
    """
    if not flask_login.current_user.is_authenticated:
        return render_template('landing.html')
    # todo: if group_id is None redirect to create group page
    user = User.query.get(flask_login.current_user.id)
    family = Family.query.get(user.family_id)
    ms = User.query.filter_by(family_id=family.id)
    members = []
    for m in ms:
        members.append((m.id, UserType.query.get(m.type_id).typename))
    app.logger.debug("members length: {}".format(len(members)))
    msgs = Message.query.filter_by(family_id=family.id)
    context = {"family": family, "user": user, "members": members, "messages": msgs}
    return render_template('room.html', **context)


# todo: not used now
@app.route('/create', methods=['POST'])
def create():
    """
    Handles post from the "Add room" form on the homepage, and
    redirects to the new room.
    """
    name = request.form.get("name")
    if name:
        room, created = get_or_create(Family, name=name)
        return redirect(url_for('room', slug=room.slug))
    return redirect(url_for('rooms'))


@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()


@app.route('/api/sensor_value', methods=['POST'])
def api_sensor_value():
    """
    Handles post from the sensors.
    """
    app.logger.debug("sensor_value request: {}".format(unicode(request.form)))

    sensor_id = request.form.get("sensor_id")
    value = request.form.get("value")
    if sensor_id and value:
        sensor = get_object_or_404(Sensor, id=int(sensor_id))
        sv = SensorValue(value=value, timestamp=get_current_time(), sensor_id=sensor.id)
        db.session.add(sv)
        db.session.commit()
        # todo send to sockets
    return ('OK', 200)


@app.route('/api/sensor_history', methods=['GET'])
def api_sensor_history():
    """
    Returns sensor data
    """
    sensor_id = request.args.get('sensor_id')
    span_mins = request.args.get('span_mins')

    if sensor_id and span_mins:
        sensor = get_object_or_404(Sensor, id=int(sensor_id))
        start_time = get_current_time() - timedelta(minutes=int(span_mins))
        svs = SensorValue.query.filter(and_(SensorValue.sensor_id==sensor.id, SensorValue.timestamp>start_time))
        data = jsonify({'data': [ record.serialize for record in svs.all() ]})
        resp = data
        resp.status_code = 200
        return resp

    return ({'data': []} , 200)
