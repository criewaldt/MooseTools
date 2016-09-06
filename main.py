from flask import Flask, render_template, request, flash, Response
from functools import wraps
import json
import datetime
from checkout import Checkout, q_round
import traceback

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'itsasecret'


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    '''Ah ah ah, you didn't say the magic word...''', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Define a route for the default URL, which loads the form
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/server', methods=['POST', 'GET'])
def server():
    if request.method == "GET":
        return render_template('serve3.html')
    else:
            

        data = {}

        data['cash'] = request.form['cash']
        data['s1_food'] = request.form['s1_food']
        data['s1_liquor']  = request.form['s1_liquor']
        data['s1_beer'] = request.form['s1_beer']
        data['s1_wine'] = request.form['s1_wine']
        #data['s1_nabev'] = request.form['s1_nabev']
        #data['s1_comps'] = request.form['s1_comps']
        data['s1_sales'] = request.form['s1_netsales']
        data['s1_deposit'] = request.form['s1_deposit']

        data['s2_food'] = request.form['s2_food']
        data['s2_liquor'] = request.form['s2_liquor']
        data['s2_beer'] = request.form['s2_beer']
        data['s2_wine'] = request.form['s2_wine']
        #data['s2_nabev'] = request.form['s2_nabev']
        #data['s2_comps'] = request.form['s2_comps']
        data['s2_sales'] = request.form['s2_netsales']
        data['s2_deposit'] = request.form['s2_deposit']

        for key in data:
            data[key] = float(data[key])

        data['name'] = request.form['name']
        
        staffObj = json.loads(request.form['choices'])
        servers = {}
        hosts = {}
        swings = {}
        for choice in staffObj:
            if choice['type'] == 'server':
                servers[choice['name']] = {'hours':q_round(choice['hours'])}
            elif choice['type'] == 'host':
                hosts[choice['name']] = {'hours':q_round(choice['hours'])}
            else:
                swings[choice['name']] = {'hours':q_round(choice['hours'])}
        staff = {'serve':servers,
                 'host':hosts,
                 'swing':swings}
        data['staff'] = staff

        try:
            report = Checkout(data)
            #print(json.dumps(report, indent=4, sort_keys=True))
            return render_template('report2.html', data=report)
        except Exception as error:
            
            flash('Something went wrong! {}'.format(error))
            print(error)
            return render_template('index.html')

@app.route('/archive')
@requires_auth
def archive():
    return 'Test'
        
@app.errorhandler(404)
def page_not_found(e):
    return "template not found"

@app.errorhandler(500)
def oops(e):
    flash('You did not fill out the form correctly, there are empty fields or invalid entries.')
    return render_template('index.html')

# Run the app :)
if __name__ == '__main__':
    app.run() 
    #app.run(host='0.0.0.0')
