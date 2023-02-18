import requests

URL = 'http://localhost:8000/signup'

email: str = input('Enter email: ')
password: str = input('Enter password: ')
channel_name: str = input('Enter channel name: ')

data = {'email': email,
        'password': password, 'channel_name': channel_name}

files = {'file': open('assets/maharaj.jpg', 'rb')}

print('started')
response = requests.post(URL, params=data, files=files)
print(response.text)
