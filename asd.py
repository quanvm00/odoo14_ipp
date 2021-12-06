import requests, json

headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'charset': 'utf-8'
}

data = {
    'login': 'admin',
    'password': '1',
    'db': 'ipp'
}
base_url = 'http://localhost:8012/api/auth/token'

req = requests.get(base_url, data=data, headers=headers)

content = json.loads(req.content.decode('utf-8'))

headers['access-token'] = content.get('access_token')  # add the access token to the header
print(headers)

####

req = requests.get('http://localhost:8012/api/sale.order/', headers=headers,
                   data={'limit': 10, 'domain': []})
# ***Pass optional parameter like this ***
{
    'limit': 10, 'domain': "[]",
    'order': 'name asc', 'offset': 10
}

print(req.content)
