from flask import Flask, render_template, request, flash
import json
import datetime
from checkout import Checkout
import traceback

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'sdfsklkj987923nk4jh23'

# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('index.html')

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is 
# accepting: POST requests in this case
@app.route('/submit', methods=['POST'])
def generate_report():

    data = {}

    
    
    data['cash'] = request.form['cash']
    data['s1_food'] = request.form['s1_food']
    data['s1_liquor']  = request.form['s1_liquor']
    data['s1_beer'] = request.form['s1_beer']
    data['s1_wine'] = request.form['s1_wine']
    data['s1_nabev'] = request.form['s1_nabev']
    data['s1_comps'] = request.form['s1_comps']
    data['s1_sales'] = request.form['s1_netsales']
    data['s1_deposit'] = request.form['s1_deposit']

    data['s2_food'] = request.form['s2_food']
    data['s2_liquor'] = request.form['s2_liquor']
    data['s2_beer'] = request.form['s2_beer']
    data['s2_wine'] = request.form['s2_wine']
    data['s2_nabev'] = request.form['s2_nabev']
    data['s2_comps'] = request.form['s2_comps']
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
            servers[choice['name']] = {'hours':choice['hours']}
        elif choice['type'] == 'host':
            hosts[choice['name']] = {'hours':choice['hours']}
        else:
            swings[choice['name']] = {'hours':choice['hours']}
    staff = {'serve':servers,
             'host':hosts,
             'swing':swings}
    data['staff'] = staff

    try:
        report = Checkout(data)
        #print(json.dumps(report, indent=4, sort_keys=True))
        return render_template('report.html', data=report)
    except Exception as error:
        
        flash('Something went wrong! {}'.format(error))
        return render_template('index.html')

        
@app.errorhandler(404)
def page_not_found(e):
    return "template not found"

@app.errorhandler(500)
def oops(e):
    flash('You did not fill out the form correctly, there are empty fields or invalid entries.')
    return render_template('oops.html')

# Run the app :)
if __name__ == '__main__':
    #app.run() 
    app.run(host='0.0.0.0')
