from math import sin, cos, sqrt, atan2, radians
from django.conf import settings
from twilio.rest import Client
from user.models import Responder


client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)


def nearby_responder(report):
    try:
        responder_list = Responder.objects.filter(station=report.emergency) 
        report_responder = []
        look_up_radius = 500.0 

        while len(report_responder) == 0:
            for responder in responder_list:
                responder_lat = responder.latitude
                responder_lng = responder.longitude

                distance = calculate_distance(report.latitude, report.longitude, responder_lat, responder_lng) 

                if distance <= look_up_radius:
                    report_responder.append(responder) 

            look_up_radius = look_up_radius + 100.0 

        for responder in report_responder:
            construct_and_send_sms(report, responder)
        
        return True
    except:
        return False
    

def construct_and_send_sms(report, responder):
    """A FUNCTION CONSTRUCT AND SEND SMS NOTIFICATION"""

    client.messages.create(
        to      = responder.phone_number,
        from_   = settings.TWILIO_PHONE_NUMBER,
        body    = 'Responder : %s \nReport # : %s \nReporter : %s \nAddress : %s' % (responder.user.username, report.id, report.reporter, report.address)
    ) # Send SMS Notification to nearby responder


def calculate_distance(report_lat, report_lng, responder_lat, responder_lng):
    """A FUNCTION THAT COMPUTES THE DISTANCE BETWEEN THE REPORT AND RESPONDER"""

    R = 6371000.0 # approximate radius of earth in meters

    # Report Latitude and Longitude
    lat_1 = radians(float(report_lat))
    lon_1 = radians(float(report_lng))
    # Responder Latitude and Longitude
    lat_2 = radians(float(responder_lat))
    lon_2 = radians(float(responder_lng))

    # Report and Responder difference
    d_lon = lon_2 - lon_1
    d_lat = lat_2 - lat_1

    # This is where the magic happens!
    a = sin(d_lat / 2)**2 + cos(lat_1) * cos(lat_2) * sin(d_lon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c # Distance between Report and Responder

    return distance # Return distance