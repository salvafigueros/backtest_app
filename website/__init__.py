from flask import Flask



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'askdjnasudnsadjnasd'

    from .views import views
    from .auth import auth
    from .views_backtesting import views_backtesting
    from .views_other import views_other

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views_backtesting, url_prefix='/')
    app.register_blueprint(views_other, url_prefix='/')

    #from . import db
    #db.init_app(app)

    return app


