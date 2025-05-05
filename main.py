from os import path, remove
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, login_manager
from datetime import datetime
from PIL import Image
from data import db_session
from forms import order_form
from data.media import Media
from data.admins import Admins
from data.orders import Order
from data.type_of_events import TypeOfEvents
from forms.media_form import MediaEditForm, MediaAddForm, MediaDelForm
from forms.user import RegisterForm, LoginForm, UserEditForm, ChangePasswordForm, UserSortForm
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = '7bafb7a4fc07dnn5848ii753118eco64eda'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(Admins, user_id)


@app.route('/')
@app.route('/index')
def index():
    year = datetime.now().year
    return render_template('index.html', title='Ярослав Никонов', year=year)


@app.route('/order', methods=['GET', 'POST'])
def order_e():
    form = order_form.OrderForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        new_id = 1
        ordr = db_sess.query(Order).order_by(Order.id.desc()).first()
        if ordr:
            new_id = ordr.id + 1
        order = Order(id=new_id, name=form.name.data, phone=form.phone.data, count_of_goest=form.count_of_goest.data,
                      need_date=form.need_date.data, wishes=form.wishes.data)
        db_sess.add(order)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('order.html', title='Заявка на мероприятие', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Admins).filter(Admins.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        admin = Admins(name=form.name.data, email=form.email.data, stutus=1)
        admin.set_password(form.password.data)
        db_sess.add(admin)
        db_sess.commit()
        db_sess.close()
        return redirect('/admin')
    return render_template('register.html', title='Регистрация администратора', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Admins).filter(Admins.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/admin")
        # db_sess.close()
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# @app.route('/picview/<int:med_id>', methods=['GET', 'POST'])
# def picview(med_id=0):
#     db_sess = db_session.create_session()
#     med = db_sess.query(Media).filter(med_id == Media.id).first()
#     if med:
#         form_med_edit = MediaEditForm()
#         form_med_del = MediaDelForm()
#         if request.method == "GET":
#             form_med_edit.title.data = med.title
#             form_med_edit.descr.data = med.content
#         if form_med_edit.validate_on_submit() and form_med_edit.title.data:
#             med.title = form_med_edit.title.data
#             med.descr = form_med_edit.descr.data
#             db_sess.commit()
#         if form_med_del.validate_on_submit() and form_med_del.pic_id.data:
#             db_sess.delete(med)
#             db_sess.commit()
#             remove(f"static//photos//{med.filename}")
#             remove(f"static//thumb//{med.filename}")
#             return redirect(f"/index/{current_user.id}")
#         return render_template('picview.html', pic=med,
#                                form_pic_del=form_med_del, form_pic_edit=form_med_edit)
#     db_sess.close()
#     abort(404)

@app.route('/picture_add', methods=['GET', 'POST'])
def picture_add():
    form = MediaAddForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        new_id = 1
        med = db_sess.query(Media).order_by(Media.id.desc()).first()
        if med:
            new_id = med.id + 1
        file = form.upload.data
        media = Media(
            id=new_id,
            fname=f"f{new_id:08d}{path.splitext(file.filename)[1]}",
            title=form.title.data,
            content=form.descr.data,
            admin_id=current_user.id
        )
        file.save(f"static//img//{media.fname}")
        image = Image.open(f"static//img//{media.fname}")
        image.thumbnail((300, 300))
        image.save(f"static//thumb//{media.fname}")
        db_sess.add(media)
        db_sess.commit()
        db_sess.close()
        return redirect('/admin')
    return render_template('picture_add.html', form=form)


if __name__ == '__main__':
    db_session.global_init("db/visitka.db")
    db_sess = db_session.create_session()
    admin = Admin(app, name='Админка', template_mode='bootstrap3')
    admin.add_view(ModelView(Admins, db_sess, name='Админы'))
    admin.add_view(ModelView(Media, db_sess, name='Управления медиа'))
    admin.add_view(ModelView(Order, db_sess, name='Заявки'))
    app.run(port=8080, host='127.0.0.1')
