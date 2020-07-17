import requests
import pandas as pd
from dateutil import parser
import math
import datetime
import time
import warnings
warnings.filterwarnings('ignore')

def stops():
    """
    get all the stops data as a dataframe for displaying in the index
    """
    url = "https://api-v3.mbta.com/stops?filter%5Broute_type%5D=2"

    payload = {}
    headers= {}

    response = requests.request("GET", url, headers=headers, data = payload)

    return pd.DataFrame(pd.io.json.json_normalize(response.json()['data']))

def sched_pred(stop:str):
    """
    get the sched and stops for a location
    """
    stop = stop.replace(" ","+")
    url = f"https://api-v3.mbta.com/predictions?filter[stop]={stop}&include=schedule"

    payload = {}
    headers= {}

    response = requests.request("GET", url, headers=headers, data = payload)

    _json = response.json()

    if len(_json['data']) == 0: 
        raise Exception ("No Data For Stop")

    sched = pd.DataFrame(pd.io.json.json_normalize(_json['included']))
    preds = pd.DataFrame(pd.io.json.json_normalize(_json['data']))
    return sched,preds

def load_board(sched,preds):
    """
    setup dtypes, synth an index to merge preds and scheds, and prep for splitting arrs and deps
    """
    #TODO: remove duplicated code, was developing in jupyter
    rsched = sched[['id','attributes.arrival_time',
           'attributes.departure_time',
           'relationships.route.data.id']]

    rpreds = preds[['id','attributes.arrival_time',
           'attributes.departure_time',
           'relationships.route.data.id',
           'relationships.vehicle.data.id']]

    #TODO: make this into a function called 4 times
    rpreds['attributes.arrival_time'] = pd.to_datetime(rpreds['attributes.arrival_time'],infer_datetime_format=True, utc=True)
    rpreds['attributes.departure_time'] = pd.to_datetime(rpreds['attributes.departure_time'],infer_datetime_format=True, utc=True)
    rsched['attributes.arrival_time'] = pd.to_datetime(rsched['attributes.arrival_time'],infer_datetime_format=True, utc=True)
    rsched['attributes.departure_time'] = pd.to_datetime(rsched['attributes.departure_time'],infer_datetime_format=True, utc=True)

    rsched.columns = ['id','sched.arrival_time','sched.departure_time','relationships.route.data.id']
    #TODO : rpreds.columns = ...

    # create a synth_id that has the same pk so we can merge, this could be made into a function for reuse
    rsched['synth_id'] = rsched.id.str.split('-')
    rsched.synth_id = [''.join(map(str, l[1:])) for l in rsched.synth_id]

    rpreds['synth_id'] = rpreds.id.str.split('-')
    rpreds.synth_id = [''.join(map(str, l[1:])) for l in rpreds.synth_id]

    departure_board = pd.merge(rpreds,rsched,on='synth_id')

    departure_board['attributes.departure_time'][departure_board['attributes.departure_time'].isnull()] = departure_board['sched.departure_time']

    departure_board['attributes.arrival_time'][departure_board['attributes.arrival_time'].isnull()] = departure_board['sched.arrival_time']
    
    # a row can contain a dep, an arr, or both, so we check if the col is null to determine if it is not one of the two
    departure_board['is_arrival'] = departure_board['sched.arrival_time'].notnull()

    departure_board['is_departure'] = departure_board['sched.departure_time'].notnull()
    return departure_board


def arrivals_departures(departure_board):
    """
    create the arrivals and departures boards, calculate time differential, and rename columns
    """
    def time_diff(a,b):
        """
        custom time subtractor as there were some problems doing datetime subtraction
        """
        if pd.isnull(a)or pd.isnull(b):
            return 0
        d,h,m = a.day - b.day, a.hour - b.hour, a.minute - b.minute
        if [d,h,m] == [0,0,0]:
            return 'On Time'
        return f"{d} days, {h} hrs, {m} mins"

    row_list = []
    for index,row in departure_board.iterrows():
        row['departure_diff'] = time_diff(row['sched.departure_time'],
                                         row['attributes.departure_time'])

        row['arrival_diff'] = time_diff(row['sched.arrival_time'],
                                         row['attributes.arrival_time'])
        row_list.append(row)

    res = pd.DataFrame(row_list)
    res.fillna('UNKNOWN')

    arrivals = res[res['is_arrival'] == True][[
        'attributes.arrival_time',
        'sched.arrival_time',
        'arrival_diff',
        'relationships.route.data.id_x',
        'relationships.vehicle.data.id'
    ]]

    departures = res[res['is_departure'] == True][[
        'attributes.departure_time',
        'sched.departure_time',
        'departure_diff',
        'relationships.route.data.id_x',
        'relationships.vehicle.data.id'
    ]]

    arrivals.columns = ['Predicted Time','Scheduled Time','Time Difference','Route','Train']
    departures.columns = ['Predicted Time','Scheduled Time','Time Difference','Route','Train']

    # sort on the predicted time so user does not miss by looking at scheduled
    arrivals = arrivals.sort_values('Predicted Time')
    departures = departures.sort_values('Predicted Time')
    arrivals['Train']   = arrivals['Train'].fillna('UNKNOWN')
    departures['Train'] = departures['Train'].fillna('UNKNOWN')
    return arrivals,departures

def links():
    """
    create the main index board
    """
    _stops = stops()
    _stops = _stops[['id']]
    _stops.id = _stops['id'].str.replace(" ","+")
    _stops['board'] = "<a href='/boards/"+_stops.id +"'>Board</a>"
    return _stops





