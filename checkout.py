import json
import sqlite3
import datetime

#helper functions
def q_round(x):
    return round(x*4)/4


def Checkout(data):

    now = datetime.datetime.now()
    
    report = {}

    report['name'] = data['name']
    report['cash'] = data['cash']
    
    report['food'] = data['s1_food'] + data['s2_food']
                      
    
    report['alcohol'] = data['s1_liquor'] + data['s1_wine'] + data['s1_beer']\
                            + data['s2_liquor'] + data['s2_wine'] + data['s2_beer']
    report['sales'] = data['s1_sales'] + data['s2_sales']
    report['deposit'] = {'net': round(data['s1_deposit'] + data['s2_deposit']),
                         'w1': data['s1_deposit'],
                         'w2': data['s2_deposit'],}
    #report['comps'] = int(data['s1_comps'] + data['s2_comps'])

    report['barTip'] = round(report['alcohol'] * 0.1)

    report['staff'] = data['staff']
    
    #remove support pay
    #swing
    sup_staff = False
    for employee in report['staff']['swing']:
        pay = round(report['staff']['swing'][employee]['hours'] * 5)
        report['staff']['swing'][employee]['pay'] = pay
        report['cash'] -= pay
        sup_staff = True

    #host
    for employee in report['staff']['host']:
        pay = round(report['staff']['host'][employee]['hours'] * 5)
        report['staff']['host'][employee]['pay'] = pay
        report['cash'] -= pay
        sup_staff = True

    #remove bartip
    report['cash'] -= report['barTip']
        
    #remove deposit
    report['cash'] -= report['deposit']['net']

    #calc hourly
    serve_hours = 0
    for employee in report['staff']['serve']:
        serve_hours += report['staff']['serve'][employee]['hours']


    #gross hourly
    gross_hourly = round((report['cash'] / serve_hours), 2)

    #if above 24:
    if gross_hourly >= 24 and sup_staff == True:
        #remove 1%
        support_bonus = round(report['sales'] * 0.01)
        report['supportBonus'] = support_bonus
        report['cash'] -= support_bonus
        #calc net hourly
        net_hourly = round((report['cash'] / serve_hours), 2)
    else:
        net_hourly = gross_hourly
        report['supportBonus'] = 'n/a'
    
    report['hourlyRate'] = {'gross':gross_hourly,
                            'net':net_hourly}
    #assign pay
    for employee in report['staff']['serve']:
        report['staff']['serve'][employee]['pay'] = round(net_hourly * report['staff']['serve'][employee]['hours'])
        report['cash'] -= report['staff']['serve'][employee]['pay']

    #deal with leftover cash due to rounding
    # we need to figure out who the closer is
    # we'll just find the highest paid server
    # and they will either eat/benefit the difference
    cname = ''
    cpay = 0
    #print(assert report['staff']['serve'][employee]['pay'] != cpay)
    for employee in report['staff']['serve']:
        tpay = report['staff']['serve'][employee]['pay']
        if tpay > cpay:
            cpay = report['staff']['serve'][employee]['pay']
            cname = employee

    report['staff']['serve'][cname]['pay'] += int(report['cash'])
    del report['cash']

    """
    #SAVE ALL INFO TO DATABASE
    conn = sqlite3.connect('/home/pi/ShiftCheckout/db/db.sqlite')
    c = conn.cursor()

    report['date'] = now.strftime("%Y-%m-%d %H:%M")
    
    c.execute("INSERT INTO report VALUES ('{}','{}','{}','{}')".format(data['name'], now.strftime("%Y-%m-%d %H:%M"), json.dumps(data), json.dumps(report)))
    conn.commit()
    conn.close()
    """
    return report
