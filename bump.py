import pyrebase
from geopy.distance import vincenty

config = {"apiKey":"AIzaSyBKX1xmfY8JuhIbgOxhO2APg6f4VcCZWXI","authDomain":"luminous-inferno-9831.firebaseapp.com","databaseURL":"https://luminous-inferno-9831.firebaseio.com","storageBucket":"luminous-inferno-9831.appspot.com"}

def start():
    fb = pyrebase.initialize_app(config)
    db = fb.database()
    mys = db.child('bumps').stream(stream_handler)

def stream_handler(post):
    data = post['data']
    k = data.keys()[0]
    t_init = data[k]['time']
    geo_origin = (data[k]['lat'],data[k]['lon'])
    t_minus = t_init-10000
    t_plus = t_init+10000
    t_results = db.child("bumps").order_by_child("time").start_at(t_minus).end_at(t_plus).get()
    for r in t_results.each():
        location = (r.val()['lat'],r.val()['lon'])
        distance = vincenty(geo_origin,location).ft
        if distance < 100:
            data = {'uone': {data[k]},'uone_name':data[k]['name'],'utwo':{r},'utwo_name':r['name']}
            db.child("matches").push(data)
    print(t_results)
