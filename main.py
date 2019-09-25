"""AlayaNotes

Usage:
  main.py [run]
  main.py initdb
  main.py migrate

"""
from docopt import docopt
import subprocess
import os

from alayatodo import app


def _run_sql(filename):
    try:
        subprocess.check_output(
            "sqlite3 %s < %s" % (app.config['DATABASE_PATH'], filename),
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError, ex:
        print ex.output
        exit(1)


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        _run_sql('resources/database.sql')
        print "AlayaTodo: Database initialized."
    elif args['migrate']:
        for file in os.listdir("resources/migrations"):
            _run_sql('resources/migrations/%s' % file)
    else:
        app.run(use_reloader=True)
