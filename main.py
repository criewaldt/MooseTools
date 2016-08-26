from flask import Flask, render_template, request, flash
import json
import datetime
from checkout import Checkout, CheckoutTest, q_round

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
    
    data['s1_food'] = float(request.form['s1_food'])
    data['s1_liquor']  = float(request.form['s1_liquor'])
    data['s1_beer'] = float(request.form['s1_beer'])
    data['s1_wine'] = float(request.form['s1_wine'])
    data['s1_nabev'] = request.form['s1_nabev']
    data['s1_comps'] = float(request.form['s1_comps'])
    data['s1_netsales'] = float(request.form['s1_netsales'])
    data['s1_deposit'] = float(request.form['s1_deposit'])

    data['s2_food'] = float(request.form['s2_food'])
    data['s2_liquor'] = float(request.form['s2_liquor'])
    data['s2_beer'] = float(request.form['s2_beer'])
    data['s2_wine'] = float(request.form['s2_wine'])
    data['s2_nabev'] = request.form['s2_nabev']
    data['s2_comps'] = float(request.form['s2_comps'])
    data['s2_netsales'] = float(request.form['s2_netsales'])
    data['s2_deposit'] = float(request.form['s2_deposit'])

    net_food = s1_food + s2_food
    net_alcohol = (s1_liquor + s1_beer + s1_wine)+(s2_liquor + s2_beer + s2_wine)
    #net_nabev = s1_nabev + s2_nabev
    net_sales = s1_netsales + s2_netsales
    net_deposit = round(s1_deposit + s2_deposit)
    net_comps = int(s1_comps + s2_comps)
    
    bar_tip = round(net_alcohol*.1)
    
    choices = json.loads(request.form['choices'])

    print(json.dumps(choices, indent=4, sort_keys=True))
    
    support = {}
    servers = {}
    
    for choice in choices:
        if choice['type'] == 'server':
            servers[choice['name']] = {'hours':choice['hours']}
        else:
            support[choice['name']] = {
                'hours':choice['hours'],
                'type':choice['type']}

    total_serve_hours = 0
    for server in servers:
        total_serve_hours += q_round(servers[server]['hours'])
    print("Total server hours: {}".format(total_serve_hours))

    total_support_hours = 0
    for sup in support:
        total_support_hours += q_round(support[sup]['hours'])
    support_tipout = total_support_hours * 5
    print("Support staff tipout: {}".format(support_tipout))

    #cash minus deposit
    OH_cash = cash - net_deposit
    #cash minus bar tipout
    OH_cash = OH_cash - bar_tip
    #cash minus support tipout
    OH_cash = OH_cash - support_tipout

    gross_hourly = (OH_cash/total_serve_hours)
    print('Server Gross Hourly Rate:', gross_hourly)

    #IF OVER $24/hour
    if gross_hourly >= 24:
        if total_support_hours > 0:
            print(net_sales, net_sales*.01)
            extra_support_tipout = round(net_sales*.01)
            #cash minus extra support tipout
            OH_cash = OH_cash - extra_support_tipout
            print('** $24/h reached. The support staff will share an extra 1% (${}) of the net sales from this shift'.format(extra_support_tipout))

            n_hourly = (OH_cash/total_serve_hours)
            print("Server Net Hourly Rate: ${}".format(n_hourly))
        else:
            n_hourly = g_hourly
    else:
        n_hourly = g_hourly
    
    print('Servers:')
    for server in servers:
        print(' {} @ {} hours'.format(server, servers[server]['hours']))
    print('Support Staff:')
    if len(support) == 0:
        print(' n/a')
    else:
        for sup in support:
            print(' {} @ {} hours'.format(sup, support[sup]['hours']))
        
    print(bar_tip, "on {} in liquor sales".format(net_alcohol))

    data = {
        'comps':net_comps,
        'food': net_food,
        'alcohol': net_alcohol,
        'sales': net_sales,
        'deposit': net_deposit,
        'bartip': bar_tip,
        'hourly_rate':{'gross':g_hourly,
                       'net':n_hourly
                       },
        'employeeData':{'wait':'',
                         'support':{'host':hosts,
                                 'swing':swings,
                                 'other':other_emp},
                         },
        }

    print(data)
    
    return render_template('report.html', data=data)


@app.route('/test', methods=['GET'])
def test():
    net_comps = 1
    net_food = 700
    net_alcohol = 300
    net_sales = 1000
    w1_deposit = 100
    w2_deposit = -100
    net_deposit = w1_deposit + w2_deposit
    deposit = {'wait1':w1_deposit,
               'wait2':w2_deposit,
               'net':net_deposit}
    bar_tip = 30
    g_hourly = 20
    n_hourly = 20
    
    servers = [{'name':'Rachael',
                'hours':5},
               {'name':'Cole',
                'hours':5},
               ]
    
    hosts = [{'name':'Shay',
                'hours':5},
             {'name':'Someone',
                'hours':5},
             ]
    
    swings = [{'name':'Chris',
                'hours':5},
              ]
    
    other_emp = [{'name':'Tony',
                'hours':5,
                'jobType':'food runner'},
                 ]

    
    data = {
        'date':datetime.datetime.now(),
        'shiftType':'PM',
        'comps':net_comps,
        'food': net_food,
        'alcohol': net_alcohol,
        'sales': net_sales,
        'deposit': deposit,
        'bartip': bar_tip,
        'hourlyRate':{'gross':g_hourly,
                       'net':n_hourly,
                      'flag':True
                       },
        'employeeData':{'serve':servers,
                        'host':hosts,
                        'swing':swings,
                        'otherEmp':other_emp,
                         },
        }
    return render_template('report2.html', data=data)

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
