from app import app
import re

app.config['TESTING'] = True
app.config['DEBUG'] = True

client = app.test_client()

for path in ['/login', '/register', '/dashboard', '/setup-2fa']:
    try:
        resp = client.get(path)
        print(path, resp.status_code)
    except Exception:
        import traceback
        print('Exception on GET', path)
        traceback.print_exc()

print('\n-- Register POST --')
resp = client.get('/register')
html = resp.data.decode('utf-8')
print('register GET csrf', 'csrf_token' in html)
m = re.search(r'name="csrf_token" value="([^"]+)"', html)
print('csrf match', bool(m))
token = m.group(1) if m else ''
try:
    resp2 = client.post('/register', data={
        'username': 'tempuser',
        'email': 'tempuser@example.com',
        'password': 'Test@1234',
        'confirm_password': 'Test@1234',
        'csrf_token': token,
    })
    print('register POST', resp2.status_code)
    print(resp2.data.decode('utf-8')[:2000])
except Exception:
    import traceback
    traceback.print_exc()

print('\n-- Login POST --')
resp = client.get('/login')
html = resp.data.decode('utf-8')
m = re.search(r'name="csrf_token" value="([^"]+)"', html)
token = m.group(1) if m else ''
try:
    resp3 = client.post('/login', data={
        'username': 'tempuser',
        'password': 'Test@1234',
        'csrf_token': token,
    }, follow_redirects=True)
    print('login POST', resp3.status_code)
    print('login final path', resp3.request.path)
    print(resp3.data.decode('utf-8')[:2000])
    try:
        resp4 = client.get('/dashboard')
        print('/dashboard', resp4.status_code)
        print(resp4.data.decode('utf-8')[:2000])
    except Exception:
        import traceback
        print('Exception on /dashboard')
        traceback.print_exc()
    try:
        resp5 = client.get('/setup-2fa')
        print('/setup-2fa', resp5.status_code)
        print(resp5.data.decode('utf-8')[:2000])
    except Exception:
        import traceback
        print('Exception on /setup-2fa')
        traceback.print_exc()
except Exception:
    import traceback
    traceback.print_exc()
