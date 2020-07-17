from mbta import * 
import unittest
import json


class SimpleTestCase(unittest.TestCase):

    def arr_dep_hybrid(self):
        """testing when dep == arr"""
        _json = json.load(open('providence.json'))
        
        sched = pd.DataFrame(pd.io.json.json_normalize(_json['included']))
        preds = pd.DataFrame(pd.io.json.json_normalize(_json['data']))

        departure_board = load_board(sched,pred)

        arr,dep = arrivals_departures(departure_board)

        assert len(arr) == 1 and len(dep)  == 1
  
    def south_station(self):
        """testing for exact matches of counts"""
        _json = json.load(open('south_station.json'))
        
        sched = pd.DataFrame(pd.io.json.json_normalize(_json['included']))
        preds = pd.DataFrame(pd.io.json.json_normalize(_json['data']))

        departure_board = load_board(sched,pred)

        arr,dep = arrivals_departures(departure_board)

        assert len(arr) == 16 and len(dep)  == 9
    
    

