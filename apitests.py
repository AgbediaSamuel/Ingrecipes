import requests

app_id = "f1a5dd2d"
app_key = "0dcf536829d4970fa80eb768d3421628"
url = f"https://api.edamam.com/api/recipes/v2?type=public&q=chicken&app_id={app_id}&app_key={app_key}"
response = requests.get(url)
print(response.text)