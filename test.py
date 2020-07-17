from mbta import * 
import unittest
import json
import warnings
warnings.filterwarnings('ignore')

class SimpleTestCase(unittest.TestCase):
    #TODO in the future check for exact data matches
    def test_arr_dep_hybrid(self):
        """testing when dep == arr"""
        _json = json.load(open('providence.json')) #todo explicity close
        
        sched = pd.DataFrame(pd.io.json.json_normalize(_json['included']))
        preds = pd.DataFrame(pd.io.json.json_normalize(_json['data']))

        departure_board = load_board(sched,preds)

        arr,dep = arrivals_departures(departure_board)

        assert len(arr) == 1 and len(dep)  == 1
  
    def test_south_station(self):
        """testing for exact matches of counts"""
        _json = json.load(open('south_station.json')) #todo explicit close
        
        sched = pd.DataFrame(pd.io.json.json_normalize(_json['included']))
        preds = pd.DataFrame(pd.io.json.json_normalize(_json['data']))

        departure_board = load_board(sched,preds)

        arr,dep = arrivals_departures(departure_board)

        assert len(arr) == 16 and len(dep)  == 9
    
    

if __name__ == '__main__':
    unittest.main()