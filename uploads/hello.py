# python hello.py --port-8000

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import pymongo
import random
import os

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

DB_URL = os.getenv("MONGO_DB_URL")
GOOGLE_AUTH_KEY = os.getenv("GOOGLE_AUTH_KEY")
GOOGLE_AUTH_SECRET = os.getenv("GOOGLE_AUTH_SECRET")
COOKIE_SECRET = os.getenv("COOKIE_SECRET")

settings = {
    "cookie_secret": COOKIE_SECRET,
    "google_oauth": {"key": GOOGLE_AUTH_KEY, "secret": GOOGLE_AUTH_SECRET}
}

# random data set for FE scatter plot
numDataPoints = 50


def randomNum():
    return random.randint(1, 1000)


def randomDataSet():
    return [[randomNum(), randomNum()] for i in range(numDataPoints)]


# Application Class
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/list", ListHandler),
                    (r"/login", LoginHandler),
                    # (r"/logout", LogoutHandler)
                    ]
        conn = pymongo.MongoClient(DB_URL)
        self.db = conn["mir_app"]
        tornado.web.Application.__init__(
            self, handlers, debug=True, **settings)


# Request Handlers
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")


class LoginHandler(BaseHandler):
    def get(self):
        self.write({'login': True})

    def post(self):
        self.set_secure_cookie("username", self.get_argument("username"))

# do we need to do this if we are using React?

# class LogoutHandler(BaseHandler):
#     def get(self):
        # if (self.get_argument("logout", None)):
        # self.clear_cookie("username")
        # self.redirect("/")


class ListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        list = {"numbers": randomDataSet()}
        self.write(list)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
