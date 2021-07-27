from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func

from project import db
from project.models import User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    players = []
    sort_by = None
    if current_user.is_admin:
        sort_by = request.args.get("sort_by")
        if sort_by == 'registration_time':
            players = db.session.query(User).order_by(User.created_at.desc())
        else:
            players = db.session.query(User).order_by(User.score.desc())

    return render_template('dashboard.html', user=current_user, players=players)


@main.route('/ajax/get_top_score')
def ajax_get_top_score():
    result = db.session.query(func.max(User.score).label('max_score')).one()
    return jsonify(result=result.max_score)


@main.route('/ajax/ajax_get_total_number_of_players')
def ajax_get_total_number_of_players():
    rows = db.session.query(User).count()
    return jsonify(result=rows)


@main.route('/ajax/ajax_get_total_number_of_online_players')
def ajax_get_total_number_online_players():
    rows = db.session.query(User).filter(User.is_online == True).count()
    return jsonify(result=rows)


@main.route('/ajax/ajax_set_player_top_score', methods=['POST'])
def ajax_set_player_top_score():
    score = int(request.form.get('score'))
    username = request.form.get('username')
    user = User.query.order_by(User.username == username).first()
    if user.score < score:
        user.score = score
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)
