import sys
from futu import *

sys.stdout.reconfigure(line_buffering=True)
import logging
logging.getLogger('futu').setLevel(logging.ERROR)

def test_all_firms():
    host = '127.0.0.1'
    port = 11111
    
    firms = [getattr(SecurityFirm, f) for f in dir(SecurityFirm) if not f.startswith('_') and isinstance(getattr(SecurityFirm, f), str)]
    
    for firm in firms:
        try:
            ctx = OpenSecTradeContext(host=host, port=port, security_firm=firm)
            ret, data = ctx.get_acc_list()
            ctx.close()
            if ret == RET_OK and len(data) > 0:
                print(f"Firm '{firm}' has accounts: {data.to_dict('records')}")
        except Exception as e:
            pass

if __name__ == "__main__":
    test_all_firms()
