from app import db, login
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return TgUser.query.get(int(id))


class TgUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    tg_id = db.Column(db.Integer, index=True, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64))
    chat_id = db.Column(db.Integer, index=True)
    start_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # sessions = db.relationship('TgSessions', backref='visitor', lazy='dynamic')

    def __repr__(self):
        return '<TgUser {}>'.format(self.first_name)


class TgAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tgUser_id = db.Column(db.Integer, db.ForeignKey(TgUser.tg_id))
    temp_password = db.Column(db.String(128))
    pass_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.temp_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.temp_password, password)

    def success_auth(self):
        self.success = True
        db.session.commit()

    def __repr__(self):
        return '<TgAuth {}:{}>'.format(self.tgUser_id, self.pass_timestamp)


class TgSessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tgUser_tg_id = db.Column(db.Integer, db.ForeignKey(TgUser.tg_id))
    start_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<TgSession {}>'.format(self.id)

    def get_session(tg_user_id):
        session = TgSessions.query.filter(TgSessions.tgUser_tg_id == tg_user_id) \
            .filter(TgSessions.start_time > datetime.utcnow() - timedelta(minutes=15)).first()
        if session is None:
            session = TgSessions(tgUser_tg_id=tg_user_id)
            db.session.add(session)
            db.session.commit()
            print(f'Start new session {session.id} for user {tg_user_id}')
            session_id = session.id
        else:
            session.start_time = datetime.utcnow()
            db.session.commit()
        session_id = session.id
        return session_id


class EmmetTemplates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tgUser_tg_id = db.Column(db.Integer, db.ForeignKey(TgUser.tg_id))
    title = db.Column(db.String(32), index=True)
    template = db.Column(db.Text, default="")
