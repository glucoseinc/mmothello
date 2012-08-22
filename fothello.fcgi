#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from fothello import app

if __name__ == '__main__':
   WSGIServer(app, bindAdress='127.0.0.1:8080').run()
