import sys
from futu import *

sys.stdout.reconfigure(line_buffering=True)
import logging
logging.getLogger('futu').setLevel(logging.ERROR)

host = '127.0.0.1'
port = 11111

def find_accounts():
    for market in [TrdMarket.US, TrdMarket.CA]:
        for firm in [SecurityFirm.FUTUCA, SecurityFirm.FUTUINC, SecurityFirm.FUTUSECURITIES, SecurityFirm.MOOMOO]:
            print(f"Testing Firm: {firm}, Market: {market}")
            try:
                ctx = OpenSecTradeContext(filter_trdmarket=market, host=host, port=port, security_firm=firm)
                ret, data = ctx.get_acc_list()
                if ret == RET_OK and not data.empty:
                    print(f"  Got accounts: {data.to_dict('records')}")
                ctx.close()
            except Exception as e:
                pass

if __name__ == "__main__":
    find_accounts()
