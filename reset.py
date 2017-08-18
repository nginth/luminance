from luminance.database import reset_db
from traceback import print_exc

def reset():
    try:
        yn = input('Are you sure you want to reset the database? This will delete all data and tables. y/n ')
        if yn == 'n':
            print('Okay, database unchanged.')
            return
        print('Resetting database...')
        reset_db()
        print('Done.')
    except:
        print_exc()

reset()