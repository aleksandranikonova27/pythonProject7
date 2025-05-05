from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

class MyHomeView(BaseView):
    @expose('/')
    # def index(self):
    #     arg1 = 'Hello'
    #     return self.render('admin/myhome.html', arg1=arg1)