import urllib.request
try:
    html = urllib.request.urlopen('http://127.0.0.1:8000/2/').read().decode('utf-8')
    print('Length:', len(html))
    print('<main> in html:', '<main>' in html)
    print('.card in html:', 'class=\"card\"' in html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main')
    if main:
        card = main.find('div', class_='card')
        if card:
            print('Found card inside main!')
        else:
            print('NO card inside main')
            print('Main content:', str(main)[:500])
except Exception as e:
    print('Error:', e)
