import sys
from futu import *
sys.stdout.reconfigure(line_buffering=True)
try:
    ctx = OpenSecTradeContext(host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUCA)
    ret, data = ctx.get_acc_list()
    print("FUTUCA Accounts:", data.to_dict('records') if ret == RET_OK else "Failed")
    ctx.close()
except Exception as e:
    print("Error:", e)
