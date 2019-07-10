from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime

"""
Module to calcualate the moon next ingress and
voc
"""

# Assign a minute in Julian Calendar
MINUTE = const.MINUTE
# List of house distances
DIST = [0, 2, 3, 4, 6, 8, 9, 10]

# Mean Moon motion in deg/s
MEAN_MOTION_MOON_S = const.MEAN_MOTION_MOON / 86400

def next_moon_ingress(chart):
    """
    Calculates datetime of the next Moon ingress
    """
    #TODO Need solution for calculating ingress to Aries
    # Define the sign angles
    angles = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]

    # Initate local variables
    # The next sign angle from the current moon position
    angle = 0.0
    # Distance between the current Moon position and the next sign
    dist = 0.0
    # Intiate iteration counter for statistical purposes
    i = 0

    # Load the current Moon position
    p_moon = chart.get(const.MOON)

    # Find the next sign angle
    for ang in angles:
        if p_moon.lon < ang:
            angle = ang
            dist = ang - p_moon.lon
            break

    # Evalute a mean time in days before the next Moon ingress
    dti = (dist / const.MEAN_MOTION_MOON)

    # Add the 'dti' into the the current Moon position
    tme = Datetime.fromJD(chart.date.jd + dti,0)

    # Run the loop for calculating the ingress time
    while True:
        # Recalculate chart for the corrected time
        p_chart = Chart(tme,chart.pos)
        # Get Moon object
        p_moon = p_chart.get(const.MOON)
        # Correct value of the moon's longtitude if ingress
        # to Aries
        if angle == 360 and p_moon.sign == const.ARIES:
            p_moon_lon = p_moon.lon + 360.0
        else:
            p_moon_lon = p_moon.lon

        # Calculate position differential
        a_diff = angle - p_moon_lon
        # Calculate time increment factor based
        # on the value of the differential
        inc_factor = 100.0 * abs(a_diff)

        if p_moon_lon > (angle + MEAN_MOTION_MOON_S * 0.01):
            tme = Datetime.fromJD(tme.jd - (MINUTE * inc_factor),0)
        if p_moon_lon < angle:
            tme = Datetime.fromJD(tme.jd + (MINUTE * inc_factor),0)
        if p_moon_lon > angle and p_moon_lon < (angle + MEAN_MOTION_MOON_S * 0.01):
            break
        i += 1
    return {'Date':tme, 'Sign':p_moon.sign} 


def next_ca(chart):
    """
    Is canceling aspect present?
    """
    IDate = NextMoonIngress(chart)
    p_chart = Chart(IDate['Date'],chart.pos)
    moon = chart.get(const.MOON)
    obj = 0
    obj_lon = 0
    asp_type = 0

    for ob in p_chart.objects:
        if ob.id in const.LIST_ASP_PLANETS:
            dist = abs(const.LIST_SIGNS.index(moon.sign) - const.LIST_SIGNS.index(ob.sign))
            if dist in DIST:
                if ob.signlon > obj_lon:
                    obj_lon = ob.signlon
                    obj = ob
                    if dist == 0:
                        if obj.id in [const.SUN,
                                const.MERCURY,
                                const.VENUS,
                                const.JUPITER,
                                const.NEPTUNE]:    #Conjunction
                            asp_type = 1
                        else:
                            asp_type = 0
                    if dist == 2 or dist == 10: #Sextile
                        asp_type = 1
                    if dist == 3 or dist == 9:  #Square
                        asp_type = 0
                    if dist == 4 or dist == 8:  #Trine
                        asp_type = 1
                    if dist == 6:               #Opposition
                        asp_type = 0

  
    return {'Last obj':obj.id,'Lon':obj.signlon,'POS':asp_type,'NI':IDate['Date']}
