import sys
from futu import *
sys.stdout.reconfigure(line_buffering=True)
import logging
logging.getLogger('futu').setLevel(logging.ERROR)

host = '127.0.0.1'
port = 11111

for firm in [SecurityFirm.FUTUCA, SecurityFirm.FUTUSECURITIES, SecurityFirm.FUTUINC]:
    print(f"Testing Firm: {firm}")
    try:
        ctx = OpenSecTradeContext(host=host, port=port, security_firm=firm)
        for trd_env in [TrdEnv.REAL, TrdEnv.SIMULATE]:
            ret, data = ctx.position_list_query(trd_env=trd_env)
            if ret == RET_OK and not data.empty:
                print(f"  Got {len(data)} positions in {trd_env} env!")
            else:
                print(f"  No positions or error in {trd_env} env: {data}")
        ctx.close()
    except Exception as e:
        print(f"Exception: {e}")
