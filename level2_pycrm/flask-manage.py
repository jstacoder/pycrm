import sys
import Ipython

#_app = sys.argv[1]
#app = _app
#app = __import__(_app,globals(),locals(),fromlist=[''])
#for itm in dir(app):
#    locals()[itm] = getattr(app, itm)
app.testing = True
test_client = app.test_client()

welcome_msg = """Welcome to the flask cli environment
the following variables are avialable to use:
app             ->  your flask.app
test_client     ->  your flask.app.test_client()
"""

Ipython.embed(header=welcome_msg)