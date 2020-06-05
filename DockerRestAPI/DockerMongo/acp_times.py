"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow


CLOSE = [(1000,11.428),(600,15),(400,15),(200,15),(0,15)]
OPEN = [(1000,28),(600,30),(400,32),(200,34),(0,34)]

def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    i=0
    total_time = 0

    for i in range(len(OPEN)):
	    if control_dist_km >= OPEN[i][0]:
	        dist = control_dist_km - OPEN[i][0] 
	        time = dist / OPEN[i-1][1] 
	        total_time += time 
	        control_dist_km -= dist 	      	
    brevet_start_time = arrow.get(brevet_start_time)
    hours = int(total_time) 
    minutes = round(60*(total_time-hours))
    opening_time = brevet_start_time.shift(hours=hours,minutes=minutes) 
    return opening_time.isoformat()
    


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    i=0
    total_time = 0

    for i in range(len(CLOSE)):
	    if control_dist_km >= CLOSE[i][0]:
	        dist = control_dist_km - CLOSE[i][0] 
	        time = dist / CLOSE[i-1][1] 
	        total_time += time 
	        control_dist_km -= dist 
    brevet_start_time = arrow.get(brevet_start_time)
    hours = int(total_time)
    minutes = round(60*(total_time-hours))
    closing_time = brevet_start_time.shift(hours=hours,minutes=minutes)
    return closing_time.isoformat()

