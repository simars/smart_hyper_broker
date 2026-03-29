from futu import *
import os
from dotenv import load_dotenv

load_dotenv()

HOST = '127.0.0.1'
PORT = 11111

def fetch_positions():
    password = os.getenv("MOOMOO_UNLOCK_PASSWORD")
    if password == 'your_trade_password_here':
        password = None
        
    all_positions = []
    
    firms = [SecurityFirm.FUTUCA, SecurityFirm.FUTUSECURITIES, SecurityFirm.FUTUINC]
    markets = [TrdMarket.US, TrdMarket.CA, TrdMarket.HK]
    envs = [TrdEnv.REAL, TrdEnv.SIMULATE]
    
    for firm in firms:
        for market in markets:
            ctx = None
            try:
                ctx = OpenSecTradeContext(filter_trdmarket=market, host=HOST, port=PORT, security_firm=firm)
                if password:
                    ctx.unlock_trade(password=password)
                    
                for env in envs:
                    ret_acc, acc_data = ctx.get_acc_list()
                    if ret_acc == RET_OK and not acc_data.empty:
                        for _, acc_row in acc_data.iterrows():
                            # Extract explicit account boundaries
                            acc_id = acc_row.get('acc_id')
                            acc_type = acc_row.get('acc_type', 'Unknown')
                            
                            ret, pos_data = ctx.position_list_query(trd_env=env, acc_id=acc_id)
                            if ret == RET_OK and not pos_data.empty:
                                records = pos_data.to_dict('records')
                                # Statically bind the explicit identity mappings to each position payload natively
                                for record in records:
                                    record['account_id'] = str(acc_id)
                                    record['account_type'] = acc_type
                                all_positions.extend(records)
            except Exception as e:
                pass
            finally:
                if ctx:
                    ctx.close()
                    
    # The normalization logic will clean up duplicates if any overlapping contexts existed.
    # We must explicitly deduplicate because 'get_acc_list' might return identical accounts across parallel 'markets' sweeps.
    unique_positions = { (p['code'], p.get('account_id'), p.get('position_market')): p for p in all_positions }
    return list(unique_positions.values())
