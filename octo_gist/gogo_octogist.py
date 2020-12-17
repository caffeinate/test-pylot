'''
Use the Github API to get the most recent Gist for a list of users

Created on 5 Nov 2019

@author: si
'''
from datetime import datetime
import sys

import requests

class OctoGist:
    def __init__(self):
        self.base_url = 'https://api.github.com'
        self.items_per_page = 100
        self.gist_path = (f'{self.base_url}/users/'
                          '{username}'
                          f'/gists?per_page={self.items_per_page}'
                          )

        # support 1.1 keep alive
        self.requests_session = requests.Session()
        #self.get_headers = {'Content-type': 'application/json'}
        self.get_headers = {'Accept': 'application/vnd.github.v3+json'}


    def go(self, usernames):
        """
        :param: usernames (str) comma separated list of user names
        """
        # sort order doesn't exist on the per user gist endpoint. Only on /search/
        # so find latest entry by iterating through all docs.
        target_field = 'created_at'  # or could be 'updated_at'
        target_users = usernames.split(',')
        latest_gist = {}
        for username in target_users:
            for gist_doc in self.gist_documents(username):
                if username not in latest_gist \
                or gist_doc[target_field] > latest_gist[username][target_field]:
                    latest_gist[username] = gist_doc

        # overall sort for all users
        one_gist_per_user = [(username, gist) for username, gist in latest_gist.items()]
        one_gist_per_user.sort(key=lambda g: g[1][target_field], reverse=True)
        for username, gist in one_gist_per_user:
            # description is optional            
            gist_desc = f"said something about {gist['description']}" \
                if gist['description'] else "wrote a gist"

            self.log(f"{username} @ {gist[target_field]} {gist_desc}")
        
        for username in target_users:
            if username not in latest_gist:
                self.log(f"{username} hasn't ever written a public gist")

    def gist_documents(self, username, max_docs=None):
        """
        Generator yielding (dict) as returned from github API

        :param: username (str)
        :param: max_docs (int or None) None for no limit
        """
        r = self.requests_session.get(self.gist_path.format(username=username))
        if r.status_code != 200:
            self.log(f"Couldn't get gists for {username}", "ERROR")
            return

        docs_fetched = 0
        for d in r.json():

            docs_fetched += 1
            yield d
            
            if docs_fetched >= self.items_per_page:
                # this will only print once                
                # TODO pagination
                msg = (f"TODO pagination not enabled so gists by user:{username} might have be "
                       f"skipped as they have written more than {self.items_per_page} gists."
                       )
                self.log(msg, "WARNING")

            if max_docs is not None and docs_fetched > max_docs:
                return


    def log(self, msg, level="INFO"):
        """
        Dependency injection ready logger.
        :param: msg (str)
        :param: level (str) , DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        if level in ['ERROR', 'CRITICAL']:
            outfunc = sys.stderr.write
        else:
            outfunc = print

        # TODO stderr for level = "ERROR"
        log_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        level_just = level.ljust(10)
        msg = f"{log_time} {level_just}{msg}"
        outfunc(msg)


if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        msg = "usage: python gogo_octogist.py <comma separated github usernames>\n"
        sys.stderr.write(msg)
        sys.exit(1)

    o = OctoGist()
    o.go(sys.argv[1])
