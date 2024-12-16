import requests
from datetime import datetime,timezone, timedelta

forecast_url = 'https://api.weather.gov/gridpoints/ILN/80,84/forecast/hourly'
ride_length_hours = 2
start_time = datetime(2024, 12, 16, 0, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
end_time = datetime(2024, 12, 16, 23, 59, 59, tzinfo=timezone(timedelta(hours=-5)))

# Weights
rain = 0.7
cold = 0.9
windy = 0.5
dark = 0.4

# Scoring functions
def score_hour(conditions):
    score = 0.0

    temp = conditions['temperature']
    if temp >= 70:
        score += 1 * cold
    elif temp < 50:
        score -= 1 * cold

    wind_speed = float(conditions['windSpeed'].replace(" mph", ""))
    if wind_speed <= 10:
        score += 1 * windy
    elif wind_speed >= 13:
        score -= 1 * windy

    rain_percent = conditions['probabilityOfPrecipitation']['value']
    if rain_percent <= 10:
        score += 1 * rain
    elif rain_percent >= 40:
        score -= 1 * rain
    
    if conditions['isDaytime']:
        score += 1 * dark
    else:
        score -= 1 * dark

    print("\t\twind: %f\n\t\ttemp: %f\n\t\train: %f" % (wind_speed, temp, rain_percent))
    
    return score



print('Getting optimal ride contions for a %d hour(s) ride' % (ride_length_hours))

resp = requests.get(url=forecast_url)
weather_data = resp.json()
scores = []

for condition in weather_data['properties']['periods']:
    period = datetime.fromisoformat(condition["startTime"])
    if period < start_time or period > end_time:
        continue
    print("%s" % (period))
    score = score_hour(condition)
    print("\tscore: %f" % (score))

    scores.append([score, period])

highest_index = 0
highest_score = 0

for e, period in enumerate(scores):
    score = 0
    if (e + ride_length_hours) > len(scores):
        break
    for i in range(0, ride_length_hours):
        score += scores[e + i][0]
    if score > highest_score:
        highest_score = score
        highest_index = e

print("Based on available NOAA weather data, you should roll at %s" % (scores[highest_index][1]))