import requests 

def get_location()->str: 
    """
    Get location using https://ipinfo.io/json
    :param: 
        location:str - location information from request (default: 0.0, 0.0)
    :return: 
        location
    """
    location = "0.0, 0.0" 
    try:
        r = requests.get("https://ipinfo.io/json")
    except Exception as e:
        pass
    else:
        if r.status_code == 200:
            try:
                location = r.json()['loc']
            except Exception as e:
                pass
    return location

