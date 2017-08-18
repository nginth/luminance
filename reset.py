from luminance.database import reset_db
from traceback import print_exc
try:
    yn = input('Are you sure you want to reset? y/n')
    if input == 'n'
        print('okay, database unchanged')
        return
    print('resetting database...')
    reset_db()
    print('done.')
except:
    print_exc()