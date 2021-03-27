from flask import request, flash, redirect, url_for
from flask import render_template
from app import app, db
from forms import LoginForm, TplForm, ConfirmForm
from flask_login import current_user, login_user, logout_user, login_required
from models import TgUser, TgAuth, EmmetTemplates
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
import emmet

@app.route('/index')
@app.route('/')
@login_required
def index():
    templates = EmmetTemplates.query.filter_by(tgUser_tg_id = current_user.tg_id).all()
    print(templates)
    return render_template('index.html', title='Шаблоны', templates=templates)\


@app.route('/add_tpl', methods=['GET', 'POST'])
@login_required
def add_tpl():
    form = TplForm()
    if form.validate_on_submit():
        em_tpl = EmmetTemplates(tgUser_tg_id=current_user.tg_id, title=form.title.data,
                                template=form.template.data)
        db.session.add(em_tpl)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_tpl.html', title='Новый шаблон', form=form)


@app.route('/del_tpl/<int:tpl_id>', methods=['GET', 'POST'])
@login_required
def del_tpl(tpl_id):
    form = ConfirmForm()
    if form.validate_on_submit():
        if form.confirm.data == 1:
            em_tpl = EmmetTemplates.query.filter(EmmetTemplates.tgUser_tg_id == current_user.tg_id) \
                .filter(EmmetTemplates.id == tpl_id).delete()
            db.session.commit()
            if em_tpl > 0:
                flash(f'Шаблон удален')
            else:
                flash('Шаблон не найден')
        else:
            flash('Вы сами передумали удалять')
        return redirect(url_for('index'))
    return render_template('del_tpl.html', title='Удаление шаблона', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        auth = TgAuth.query.filter(TgAuth.id==form.tgauth_id.data)\
            .filter(TgAuth.pass_timestamp > datetime.utcnow()-timedelta(minutes=1)).first()
        if auth is None or not auth.check_password(form.password.data):
            flash('ID/Пароль не верны или просрочены')
            return redirect(url_for('login'))
        auth.success_auth()
        user = TgUser.query.filter_by(tg_id=auth.tgUser_id).first()
        print(f"Login user {user.username} ({user.id})")
        if user is not None:
            login_user(user, remember=False)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('Пользователь не найден')
            return redirect(url_for('login'))
    return render_template('login.html', title='Войти', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
