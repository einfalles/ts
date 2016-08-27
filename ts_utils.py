def array_to_csv(history,user_email):
    fl_name = str(user_email) +'_history.csv'
    fl = open(fl_name, 'w')
    writer = csv.writer(fl)
    writer.writerow(['artist', 'track']) #if needed
    for values in history:
        writer.writerow(values)
    fl.close()

def csv_to_array(user):
    filename = str(user)+'_history.csv'
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        your_list= list(reader)
    return your_list


def sp_add_spid(history):
    for song in history:
        try:
            artist = song[0]
            title = song[1]
            results = SP.search(q='artist:'+ artist +' AND '+'track:'+ title,type='track')
            items = results['tracks']['items']
            if len(items)>0:
                for i in items:
                    song.append(str(i['id']))
        except:
            print(song)
            history.remove(song)
    return history
