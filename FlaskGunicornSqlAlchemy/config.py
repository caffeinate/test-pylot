class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mypass@localhost/flask_gunicorn"
    SQLALCHEMY_ECHO=False


class TestConfig(object):
    DEBUG = True
    TESTING = True
    DB_IN_MEMORY = True
    DB_FILE = None # changed to a temp file before use
    DB_FD = None
    SQLALCHEMY_DATABASE_URI = None
    
    def __init__(self):
        
        if self.DB_IN_MEMORY:
            self.SQLALCHEMY_DATABASE_URI = "sqlite://"
        else:
            self.DB_FD, self.DB_FILE = tempfile.mkstemp()
            self.SQLALCHEMY_DATABASE_URI = "sqlite:///%s" % self.DB_FILE
        #print "using db [%s]" % self.SQLALCHEMY_DATABASE_URI

    def drop_db(self):
        if not self.DB_IN_MEMORY and self.DB_FILE:
            os.close(self.DB_FD)
            #print "deleting %s" % self.DB_FILE
            os.unlink(self.DB_FILE)