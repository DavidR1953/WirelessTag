"""
Used for testing wirelessTagProxy.py

Prints out what it is sent.

"""

from bottle import put, run, request


@put("/rest/items/<item>/state")
def puts(item):
    print(f"Put: {item}")
    print(request.body.getvalue())


run(host="localhost", port=8080, debug=True)
