from flask import Flask, jsonify,render_template, send_from_directory, send_file
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, decode_token
from flask_mail import Mail
import os
import datetime
from flask_cors import CORS, cross_origin

import random
import string
def create_app(test_config=None):
    #create and configure
    app = Flask(__name__, instance_relative_config = True)
    #api = Api(app)
    app.config.from_mapping(
        SECRET_KEY = "602eed29ec224c29aa521ae3b38c0e86250437e531d251c9",
        MAIL_SERVER = "smtp.gmail.com",
        MAIL_PORT=465,
        MAIL_USERNAME="nickknaam@gmail.com",
        MAIL_PASSWORD="Tanganaika29;",
        MAIL_USE_TLS= False,
        MAIL_USE_SSL = True,
        #DEBUG=False,
        #TESTING=False
        #DATABASE= os.path.join(app.instance_path, 'flaskr.sqlite'),
    )


    api = Api(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    
    from backt import models
    @app.teardown_request
    def teardown_request(response_or_exc):
        models.db_session.remove()
    models.init_db()

    
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    jwt = JWTManager(app)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


    
    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return models.RevokedTokenModel.is_jti_blacklisted(jti)
    
    with app.app_context(): 

        @app.route('/')
        def index():
            return render_template('selection.html')
        @app.route('/coinspic.jpg')
        def review():
            try:
                return send_from_directory(
                    './static/style',
                    'coinspic.jpg',
                )
            except:
                return ''
        #@app.route('/flow.mp4')
        #def flow():
        #    try:
        #        return send_from_directory(
        #            './static/style',
        #            'sky.mp4',
        #        )
        #    except:
        #        return ''
        @app.route('/userverification/<token>')
        def confirm_user(token):
            decoded = decode_token(token)
            username = decoded['identity']
            times = datetime
            msg = ''
            if int(times.datetime.now().timestamp()) > decoded["exp"]:
                msg = "The verification link has expired"
            else:
                current_user_model = models.UserModel.find_by_username(username)
                current_user_model.confirmed = True
                username = current_user_model.username
                current_user_model.save_to_db()
                msg = "Your account has been verified!"
            return render_template('confirmation.html', username=username, msg=msg)
        @app.route('/resetpassword/<token>')
        def reset_password(token):
            decoded = decode_token(token)
            username = decoded['identity']
            times = datetime
            if int(times.datetime.now().timestamp()) > decoded["exp"]:
                msg = "The password reset link has expired"
                return render_template('expired.html', username=username, msg = msg)

            else:
                current_user_model = models.UserModel.find_by_username(username)
                newpass = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))
                current_user_model.password = models.UserModel.generate_hash(newpass)
                current_user_model.save_to_db()
                return render_template('passwordchanged.html', username=username, newpass=newpass)

        

        from backt import resources
        api.add_resource(resources.UserRegistration, '/registration')
        api.add_resource(resources.UserLogin, '/login')
        api.add_resource(resources.UserLogoutAccess, '/logout/access')
        api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
        api.add_resource(resources.TokenRefresh, '/token/refresh')
        #api.add_resource(resources.AllUsers, '/users')
        api.add_resource(resources.SecretResource, '/secret')
        api.add_resource(resources.Mirror, '/mirror')
        api.add_resource(resources.Portfolio, "/portfolio")
        api.add_resource(resources.PortfolioSpecific, "/portfolio/<int:id>")
        api.add_resource(resources.TestRest,'/testrest')
        api.add_resource(resources.SearchCoin, '/coin')
        api.add_resource(resources.BacktestingResource, '/backtesting')
        api.add_resource(resources.BacktestingByMarketcap, '/backtesting/marketcap')
        api.add_resource(resources.BactestingEqualyWeighted,'/backtesting/equalyweighted')
        api.add_resource(resources.UserCredentials,'/user')
        api.add_resource(resources.UserCredential,'/user/<credential>')
        api.add_resource(resources.UpdatePassword,'/changepassword')
        api.add_resource(resources.ForgottenPassword,'/forgottenpassword')
        api.add_resource(resources.AskConfirmation, '/verification')
        api.add_resource(resources.UserConfirmation, '/verification/<token>')
        return app