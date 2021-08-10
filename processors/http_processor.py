import requests
def processor(url, method, status_code):
    if method=="GET":
        try:
            data = requests.get(url)
        except:
            return False
        if data.status_code in status_code:
            return True
        else:
            return False

    if method=="POST":
        return True # Not implementing Why? Generally healthchecks are get only

