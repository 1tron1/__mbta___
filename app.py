from flask import Flask
import mbta
from flask import render_template

app = Flask(__name__)

@app.errorhandler(500)
def no_data(e):
    return "<h1>Uh Oh, No Data Found for this Station!</h1>", 500

@app.route('/')
def index():
    return mbta.links().to_html(escape=False)

@app.route('/boards/<board>')
def boards(board):
    sched,pred = mbta.sched_pred(board)

    departure_board = mbta.load_board(sched,pred)

    arr,dep = mbta.arrivals_departures(departure_board)

    a = arr.to_html()

    d = dep.to_html()

    return "<center><h1>Arrivals</h1>"+a+"</center>" + "<hr>" + "<center><h1>Departures</h1>" + d + "</center>"

if __name__ == '__main__':
    app.run(host='0.0.0.0')