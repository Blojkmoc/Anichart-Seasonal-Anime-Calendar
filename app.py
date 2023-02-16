from flask import Flask, render_template
import requests
import json
import datetime

app = Flask(__name__)

# Define the list of anime events to be displayed in the calendar
events = []
month_dict = {**dict.fromkeys(['01', '02', '03'], '0930'), **dict.fromkeys(['04','05','06'], '1231'),**dict.fromkeys(['07','08','09'], '0331'),**dict.fromkeys(['10','11','12'], '0630')}

@app.route('/')
def index():
    return render_template('calendar.html', events=events)

@app.route('/events')
def get_anime():
    global events
    global month_dict
    events = []
    # Fetch the anime data from AniChart
    url = 'https://graphql.anilist.co'
    query = '''
    query($page: Int, $startDate: FuzzyDateInt ) {
        Page(page: $page, perPage: 50) {
            media(startDate_greater: $startDate, status:RELEASING, format_in:[TV]) {
                id
                title {
                    romaji
                }
                nextAiringEpisode {
                    airingAt
                    episode
                }
            }
        }
    }
    '''
    #anime = []
    time_now = datetime.datetime.now().strftime("%Y-%m-%d")
    year, month, day = time_now.split('-')
    if int(month)<=6:
        year = str(int(year) - 1)
    
    if month in month_dict:
        month = month_dict[month]
    date = int(year+month)
    for i in range(1,3):
        variables = {'page': i, 'startDate': date}
        response = requests.post(url, json={'query': query, 'variables': variables})
        print(response)
        # Extract the anime titles and air dates from the response
        data = response.json()['data']['Page']['media']
        
        for d in data:
            title = d['title']['romaji']
            try:
                episode = d['nextAiringEpisode']['episode']
            except TypeError:
                episode = 0
            try:
                air_date = datetime.datetime.fromtimestamp(d['nextAiringEpisode']['airingAt'])
                air_date = air_date.strftime('%Y-%m-%d %H:%M:%S')
            except TypeError:
                air_date = '2023-01-01 00:00:00'
            #anime.append({'title': title, 'episode': episode, 'air_date': air_date})
            events.append({'title': f'{title}: Ep {episode}','start': air_date})
    #print(len(anime))

    # Return the anime data as a JSON response
    return json.dumps(events)

if __name__ == '__main__':
    app.run(debug=True)