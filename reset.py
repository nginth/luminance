from luminance.database import reset_db
from traceback import print_exc
try:
    reset_db()
    print('done.')
except:
    print_exc()