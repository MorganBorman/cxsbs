from bottle import route, run
import cube2crypto
import time

authdir =   {
                'chasm': '-b78d0f0bac4ea687e9231fdec4dc198d8cab4add287afd86',
                'fd.chasm@gmail.com': '-4d8cd6fc6fe8077650c21d0d8c932441922257d3185a219a',
            }

answers = []

@route('/auth/:name')
def auth(name=None):
    pubkey = authdir[name]
    challenge, answer = cube2crypto.genchallenge(pubkey, str(time.time()))
    answers.append(answer)
    return challenge
    
@route('/challenge/:answer')
def auth(answer=None):
    if answer in answers:
        answers.remove(answer)
        return 'verified'
    else:
        return 'unverified'
        
@route('/')
def index():
    f = open('index.html', 'r')
    data = f.read()
    f.close()
    return data

@route('/cube2crypto.o.js')
def index():
    f = open('cube2crypto.o.js', 'r')
    data = f.read()
    f.close()
    return data

@route('/cube2crypto.h.js')
def index():
    f = open('cube2crypto.h.js', 'r')
    data = f.read()
    f.close()
    return data
    
run(host='localhost', port=8080)