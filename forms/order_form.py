from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Regexp


class OrderForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    phone = StringField('Укажите номер телефона для связи с вами:',
                             validators=[DataRequired(), Length(min=10, max=11)]) #Regexp(regex='[+-]?[0-9]$'
    events = SelectField("Мероприятие", choices=[], validators=[DataRequired()])

    city = StringField('Укажите город, в котором планируется мероприятие:', validators=[DataRequired()])
    count_of_goest = IntegerField('Укажите количество гостей:', validators=[DataRequired()])
    need_date = DateField("Когда планируется мероприятие?", validators=[DataRequired()])
    wishes = TextAreaField('Расскажите подробнее о своих пожеланиях:', validators=[DataRequired()])
    submit = SubmitField('Отправить заявку')