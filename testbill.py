import requests

url = "https://www.billplz-sandbox.com/api/v3/bills"
auth_token = "73eb57f0-7d4e-42b9-a544-aeac6e4b0f81"

data = {
    "collection_id": "j0vsf4ht",
    "description": "Parking payment fee",
    "email": "haikal2205hbk@gmail.com",
    "name": "Haikal",
    "amount": 200,
    "callback_url": "http://10.62.20.99:8501/Parking_Fee_Calculations"
}

headers = {
    "Authorization": f"Basic {auth_token}:",
}

response = requests.post(url, data=data, headers=headers)
if response.status_code == 200:
    print("Bill created successfully.")
else:
    print(f"Failed to create bill. Error: {response.text}")
