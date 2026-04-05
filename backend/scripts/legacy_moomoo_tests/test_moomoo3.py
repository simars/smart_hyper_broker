import sys
from futu import *

sys.stdout.reconfigure(line_buffering=True)
import logging
logging.getLogger('futu').setLevel(logging.ERROR)

def test_accounts():
    host = '127.0.0.1'
    port = 11111
    
    # Try different combinations
    for env in [TrdEnv.REAL, TrdEnv.SIMULATE]:
        print(f"Testing env: {'REAL' if env == TrdEnv.REAL else 'SIMULATE'}")
        try:
            ctx = OpenSecTradeContext(host=host, port=port)
            # get_acc_list doesn't take params but getting context with different params might help
            # but wait, get_acc_list gets all accounts for the firm.
            # actually we don't need OpenSecTradeContext to get accounts. OpenD can just use OpenQuoteContext?
            # No, OpenSecTradeContext is fine.
            ret, data = ctx.get_acc_list()
            ctx.close()
            if ret == RET_OK:
                print(f"Accounts:", data.to_dict('records'))
            else:
                print(f"Failed:", data)
        except Exception as e:
            print("Exception:", e)

if __name__ == "__main__":
    test_accounts()
