from flask_restful import Resource, reqparse
from backt.models import UserModel, RevokedTokenModel, PortfolioModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, get_jwt_claims, decode_token)
import json
import datetime
from flask import request, Blueprint, render_template, current_app
from flask_mail import Mail, Message
from flask_cors import CORS, cross_origin
from flask_expects_json import expects_json
from functools import wraps
from backt.handlecoin import searchCoin

mail = Mail(current_app)
parser = reqparse.RequestParser()

def check_request(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if not request.is_json:
            return {"message":"Please set header Content-Type:Application/JSON"}
        if not request.get_json():
            return {"message":"Something is wrong with the json that you should've passed with your request"}       
        return func(*args, **kwargs)
    return func_wrapper
def handle_signature(func):
    @wraps(func)
    def wrapperFunction(*args, **kwargs):
        try:
            #return func(*args, **kwargs)
            return func(*args, **kwargs)
        except:
            return {"message": "Something went wrong. Your session may have expired. Please try to login again."}, 401
    return wrapperFunction

def mailTo(username, email, template):
    msg = Message('Hello', sender = 'nickknaam@gmail.com', recipients = [email])
    msg.body = "Hello Flask message sent from Flask-Mail"
    token = create_refresh_token(identity = username)
    msg.html = render_template(template, username = username, token=token)
    mail.send(msg)
    #print('me ade?')
    return "sent to {}".format(email)

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        parser.add_argument('email')
        data = parser.parse_args()
        
        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}
        if UserModel.find_by_email(data['email']):
            return {'message': 'An user with email "{}" already exists'.format(data['email'])}
        
        new_user = UserModel(
            username = data['username'],
            password = UserModel.generate_hash(data['password']),
            email = data['email']
        )
        try:
            new_user.save_to_db()
            #access_token = create_access_token(identity = data['username'])
            #refresh_token = create_refresh_token(identity = data['username'])
            mailTo(username = data['username'], email=data['email'], template= "userconfirmation.html")
            return {
                'message': 'User {} was created, please check your email for varification'.format(data['username']),
                 #'access_token': access_token,
                 #'refresh_token': refresh_token,            
                }
        except:
            return {'message': 'Something went wrong'}, 500



class UserLogin(Resource):
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @handle_signature
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @handle_signature
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        #print(current_user)
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}

class UpdatePassword(Resource):
    @handle_signature
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('password', help='This field cannot be blank',required = True)
        parser.add_argument("newpassword", help='This argument cannot be blank',required = True)
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)
        data = parser.parse_args()
        if UserModel.verify_hash(data['password'], current_user.password):
            current_user.password = UserModel.generate_hash(data['newpassword'])
            current_user.add_commit_data()
            return {'message':'Your password was updated successfully!'}
        else:
            return{"message":'Wrong password'}

class UserCredentials(Resource):
    @handle_signature
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)
        return {
            "username": current_user.username,
            "email": current_user.email,
            "firstname": current_user.firstname,
            "lastname": current_user.lastname,
            }
    
class UserCredential(Resource):
    @handle_signature
    @jwt_required
    def get(self, credential):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)
        answer = ''
        if credential=='email':
            answer = current_user.email
        elif credential=='firstname':
            answer = current_user.firstname
        elif credential=="lastname":
            answer = current_user.lastname
        if answer:
            return{credential:answer}
        else:
            return {"message":"There is no such parameter"}
    @handle_signature
    @jwt_required
    @expects_json({
        'type': 'object',
        'properties': {
            'email': {'type':'string'},
            'firstname':{'type':'string'},
            'lastname':{'type':'string'},
        },
        })
    def put(self, credential):
        username = get_jwt_identity()        
        data = request.get_json()
        current_user_model = UserModel.find_by_username(username)
        if credential=='email':
            current_user_model.email = data[credential]
            current_user_model.add_commit_data()
            return {"message":"Your {0} was changed to {1}.".format(credential, data[credential])}
        elif credential=='firstname':
            current_user_model.firstname = data[credential]
            current_user_model.add_commit_data()
            return {"message":"Your {0} was changed to {1}.".format(credential, data[credential])}
        elif credential=="lastname":
            current_user_model.lastname = data[credential]
            current_user_model.add_commit_data()
            return {"message":"Your {0} was changed to {1}.".format(credential, data[credential])}
        else:
            return {"message":"No changes were made."}


class UserConfirmation(Resource):
    def get(self, token):
        decoded = decode_token(token)
        times = datetime
        msg = ''
        if int(times.datetime.now().timestamp()) > decoded["exp"]:
            msg = "The confirmation link has expired"
        else:
            current_user_model = UserModel.find_by_username(username)
            current_user_model.confirmed = True
            username = current_user_model.username
            current_user_model.save_to_db()
            msg = "Your account has been verified!"
        return {"msg":msg}
class AskConfirmation(Resource):
    @handle_signature
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)
        if current_user.confirmed:
            return {"message":"Your account has been already verified."}
        else:
            mailTo(username=username, email=current_user.email, template="userconfirmation.html")
            return{"message":"Confirmation email sent."}

class ForgottenPassword(Resource):
    @expects_json({
       'type': 'object',
        'properties': {
            'email': {'type':'string'},
        }, 'required':['email']
    })
    def post(self):
        #parser = reqparse.RequestParser()
        #parser.add_argument('email', help = 'This field cannot be blank', required = True)
        #data = parser.parse_args()
        data = request.get_json()
        current_user = UserModel.find_by_email(data['email'])
        if not current_user:
            return {'message': 'User whit email {} doesn\'t exist'.format(data['email'])}
        else:
            mailTo(username = current_user.username,email=data['email'],template="resetmail.html")
            return{"message":"Reset password link was sent to {}".format(data['email'])}
        
        
        


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()
    
    def delete(self):
        return UserModel.delete_all()


class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }
class Mirror(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        data = parser.parse_args()
        print(data)
        return {
            'you': json.dumps(data)
        }
class Portfolio(Resource):
    @handle_signature
    @jwt_required
    @expects_json({
       'type': 'object',
    'properties': {
        'coins': {'type':'object'},
        'name':{'type':'string'},

    },
    'required': ['start', 'end','portfolio','interval','coins','name', 'roi', 'profit'] 
    })
    def post(self):
        #try:
        current_user = get_jwt_identity()
        current_user_model = UserModel.find_by_username(current_user)
        #if not current_user_model.confirmed:
        #    return {"message":"Your account is not verifyied"}
        data = request.get_json()
        name = data['name']
        if name == '':
            return {"message":"You must specify a name of Your porfolio"}
        start = data['start']
        end = data['end']
        roi = float(data['roi'])
        profit = float(data['profit'])
        portfolio = data['portfolio']
        coinSequence = data['coins']
        coinWeights = ''
        coinlist = ''
    
        for key, value in coinSequence.items():
            coinWeights += str(value) + ','
            coinlist += key + ','

        
        for por in current_user_model.portfolios:
            if (por.name == name):
                return {"message": 'Portfolio with name "{}" already exists.'.format(name)}
                break
        new_portfolio = PortfolioModel(
            name = name,
            portfolio = portfolio,
            start = start,
            end = end,
            cryptocurrencies = coinlist,
            weights = coinWeights,
            profit = profit,
            roi = roi
        )
        current_user_model.add_portfolio(new_portfolio)
        new_portfolio.add_data()
        current_user_model.add_data()
        new_portfolio.commit()
        return { "message": "{0} created {1}".format(current_user, name)}
        #except:
            #return {"message":"Something went wrong"}
    @handle_signature
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()
        current_user = get_jwt_identity()
        current_user_model= UserModel.find_by_username(current_user)
        porto = []
        for i in current_user_model.portfolios:
            porto.append({
                "name":i.name,
                "portfolio":i.portfolio,
                "profit":i.profit,
                "roi":i.roi,
                "start":i.start,
                "end":i.end,
                "coins":i.cryptocurrencies,
                "weights":i.weights,
                "saved":str(int(i.made_on.timestamp()*1000))
                })
        return {"user":current_user,"portfolios":porto}
class PortfolioSpecific(Resource):
    @handle_signature
    @jwt_required
    def get(self, id):
        current_user = get_jwt_identity()
        current_user_model= UserModel.find_by_username(current_user)
        porto = current_user_model.portfolios[id-1]
        return {"name":porto.name,"portfolio": porto.portfolio, "start":porto.start, "end":porto.end, "roi":porto.roi,"profit":porto.profit, "coins":porto.cryptocurrencies,"weights":porto.weights,"made":porto.made_on}
        #return {"portfolio":current_user_model.portfolios[id+1].name}
        #index out of range exception 
    @handle_signature
    @jwt_required
    def put(self, id):
        #parser.add_argument('portfolio', help = 'This field cannot be blank', required = True)
        #data = parser.parse_args()
        data = request.get_json(silent=True)
        new_name = data['portfolio']
        current_user = get_jwt_identity()
        current_user_model= UserModel.find_by_username(current_user)
        new_portfolio = PorfolioModel(name = new_name)
        old_name = current_user_model.portfolios[id+1].name
        current_user_model.portfolios[id+1] = new_portfolio
        current_user_model.add_data()
        new_portfolio.add_data()
        new_portfolio.commit()
        return {"message": "Portfolio {} has been changed to {}".format(old_name, new_name)}
    @handle_signature
    @jwt_required
    def delete(self, id):
        #parser.add_argument('portfolio', help = 'This field cannot be blank', required = True)
        #data = parser.parse_args()
        data = request.get_json(silent=True)
        delete_name = data['portfolio']
        current_user = get_jwt_identity()
        current_user_model= UserModel.find_by_username(current_user)
        portoId = current_user_model.portfolios[id-1].id
        print(id)
        print(portoId)
        current_user_model.delete_portfolio(current_user_model.portfolios[id-1]);

        return {"message": "{}'s Porfolio {} was deleted!".format(current_user, delete_name)}

class TestRest(Resource):
    def post(self):
        dada = request.get_json()
        print(dada)
        return {"whatvar":dada}

class SearchCoin(Resource):
    #@cross_origin
    #@jwt_required
    def get(self):
        #query = request.form['query']
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str)
        data = parser.parse_args()
        query = data['q']
        #results = {}

        return searchCoin(query)
    #@jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str)
        data = parser.parse_args()
        query = data['q']
        #results = {}        
        return searchCoin(query)
class BacktestingResource(Resource):
    #@check_request
    @expects_json({
       'type': 'object',
    'properties': {
        'coins': {'type':'object'}
    },
    'required': ['start', 'end','portfolio','interval','coins'] 
    })
    def post(self):
        data = request.get_json(silent=True)
        from backt.handlecoin import runBacktesting
        return runBacktesting(data)
class BacktestingByMarketcap(Resource):
    @expects_json()
    def post(self):
        data = request.get_json(silent=True)
        from backt.handlecoin import byMarketcap
        return byMarketcap(data)
class BactestingEqualyWeighted(Resource):
    @expects_json()
    def post(self):
        data = request.get_json(silent=True)
        from backt.handlecoin import equalyWeighted
        return equalyWeighted(data)



