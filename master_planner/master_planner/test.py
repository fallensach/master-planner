import requests
# http://localhost:8000/api/get_courses/DAIM/7
import json
data = json.dumps({"scheduler_id": 100})

r = requests.delete("http://127.0.0.1:8000/api/account/choice", data=data)

print(r.json())
