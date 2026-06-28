import urllib.request
try:
    html = urllib.request.urlopen('http://127.0.0.1:8000/1/').read().decode('utf-8')
    print('Found main:', '<main>' in html)
    print('Found card:', 'class=\"card\"' in html)
except Exception as e:
    print('Error:', e)
