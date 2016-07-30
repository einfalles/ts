def algo_search(request):
    print("start: search algo for: " + session['credentials']['id_token']['email'])
    sys.stdout.flush()
    data = {}
    t_init = int(request.form['time'])
    origin = (float(request.form['lat']),float(request.form['lon']))
    t_minus = t_init-10000
    t_plus = t_init+10000
    t_results = fbdb.child('bumps').order_by_child('time').start_at(t_minus).end_at(t_plus).get()
    for r in t_results.each():
        location = (r.val()['lat'],r.val()['lon'])
        distance = vincenty(origin,location).ft
        if distance < 500:
            half_life = (t_init + r.val()['time'])/2
            # data = {'half':half_life,'uone': request.form,'uone_email':request.form['email'],'utwo':r.val(),'utwo_email':r.val()['email']}
            data = {'half':half_life,'uone_email':request.form['email'],'utwo_email':r.val()['email']}
            if request.form['email'] != r.val()['email']:
                fbdb.child('matches').push(data)
                session['matches'] = json.dumps(data)
        else:
            return True
    session['matches'] = "dick"
    print("end: search algo for "+ session['credentials']['id_token']['email'])
    sys.stdout.flush()
    return True