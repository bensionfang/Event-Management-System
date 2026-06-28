import urllib.request
from urllib.error import HTTPError
try:
    urllib.request.urlopen('http://127.0.0.1:8000/2/')
except HTTPError as e:
    html = e.read().decode('utf-8')
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Django traceback is usually in <textarea id="traceback_area"> or just print text
    print('Error code:', e.code)
    print(soup.text[:2000].replace('\n\n', '\n'))
