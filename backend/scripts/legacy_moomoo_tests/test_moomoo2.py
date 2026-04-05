import sys
from futu import *

sys.stdout.reconfigure(line_buffering=True)
import logging
logging.getLogger('futu').setLevel(logging.ERROR)

def test_accounts():
    host = '127.0.0.1'
    port = 11111
    
    # Try FUTUCA
    try:
        print("Trying FUTUCA...")
        ctx = OpenSecTradeContext(host=host, port=port, security_firm=SecurityFirm.FUTUCA)
        ret, data = ctx.get_acc_list()
        ctx.close()
        if ret == RET_OK:
            print("FUTUCA Accounts:", data.to_dict('records'))
        else:
            print("FUTUCA get_acc_list failed:", data)
    except Exception as e:
        print("FUTUCA exception:", e)

    # Try FUTUSECURITIES
    try:
        print("Trying FUTUSECURITIES...")
        ctx = OpenSecTradeContext(host=host, port=port, security_firm=SecurityFirm.FUTUSECURITIES)
        ret, data = ctx.get_acc_list()
        ctx.close()
        if ret == RET_OK:
            print("FUTUSECURITIES Accounts:", data.to_dict('records'))
        else:
            print("FUTUSECURITIES get_acc_list failed:", data)
    except Exception as e:
        print("FUTUSECURITIES exception:", e)
        
    # Try FUTUINC
    try:
        print("Trying FUTUINC...")
        ctx = OpenSecTradeContext(host=host, port=port, security_firm=SecurityFirm.FUTUINC)
        ret, data = ctx.get_acc_list()
        ctx.close()
        if ret == RET_OK:
            print("FUTUINC Accounts:", data.to_dict('records'))
        else:
            print("FUTUINC get_acc_list failed:", data)
    except Exception as e:
        print("FUTUINC exception:", e)

if __name__ == "__main__":
    test_accounts()
