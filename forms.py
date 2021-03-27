from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from models import TgUser, TgAuth, EmmetTemplates
from flask_login import current_user
import emmet

class LoginForm(FlaskForm):
    tgauth_id = StringField('session', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField("Войти")

class TplForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    template = StringField('Шаблон', validators=[DataRequired()])
    submit = SubmitField("Сохранить")

    def validate_template(self, template):
        try:
            emmet.expand(template.data)
        except:
            raise ValidationError(f"Не удалось разобрать шаблон")

    def validate_title(self, title):
        tpl = EmmetTemplates.query.filter(EmmetTemplates.tgUser_tg_id==current_user.tg_id,
                                    EmmetTemplates.title == title.data.strip()).first()
        if tpl is not None:
            raise ValidationError(f"Такое имя шаблона уже занято")

class ConfirmForm(FlaskForm):
    confirm = RadioField('Уверены, что хотите удалить шаблон', choices=[(1,'Да, я хочу удалить шаблон'),
                                                                        (0,'Нет, я передумал')], default=0, coerce=int)
    submit = SubmitField('Применить')