from requests import post,get
url= "http://0.0.0.0:8000"
post(url+"/test-my-key",json={"a":1}).json()
post(url+"/test-my-key",json={"b":2}).json()
post(url+"/test-my-key",json={"c":3}).json()

print(get(url+"/test-my-key/a").json())
