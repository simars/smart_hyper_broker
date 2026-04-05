import os
from typing import List
from futu import SecurityFirm, TrdMarket, TrdEnv, OpenSecTradeContext, RET_OK
from src.application.interfaces import BrokerGateway
from src.domain.models import Position

# It's cleaner to keep the module-level FX mapping hidden or inject a general FX utils service
def _to_cad_usd(value: float, is_cad: bool, cad_usd_rate: float):
    if is_cad:
        return value, value / cad_usd_rate
    else:
        return value * cad_usd_rate, value

class MoomooGateway(BrokerGateway):
    def __init__(self, host: str = '127.0.0.1', port: int = 11111):
        self.host = host
        self.port = port

    @property
    def broker_name(self) -> str:
        return "moomoo"

    def fetch_positions(self, cad_usd_rate: float) -> List[Position]:
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
                    ctx = OpenSecTradeContext(filter_trdmarket=market, host=self.host, port=self.port, security_firm=firm)
                    if password:
                        ctx.unlock_trade(password=password)
                        
                    for env in envs:
                        ret_acc, acc_data = ctx.get_acc_list()
                        if ret_acc == RET_OK and not acc_data.empty:
                            for _, acc_row in acc_data.iterrows():
                                acc_id = acc_row.get('acc_id')
                                acc_type = acc_row.get('acc_type', 'Unknown')
                                
                                ret, pos_data = ctx.position_list_query(trd_env=env, acc_id=acc_id)
                                if ret == RET_OK and not pos_data.empty:
                                    records = pos_data.to_dict('records')
                                    for record in records:
                                        record['account_id'] = str(acc_id)
                                        record['account_type'] = acc_type
                                    all_positions.extend(records)
                except Exception as e:
                    pass
                finally:
                    if ctx:
                        ctx.close()
                        
        unique_positions = { (p['code'], p.get('account_id'), p.get('position_market')): p for p in all_positions }
        
        domain_positions = []
        for pos in unique_positions.values():
            raw_symbol = pos.get("code", "")
            if not raw_symbol:
                continue
                
            symbol = raw_symbol[3:] if raw_symbol.startswith("US.") else raw_symbol
            market_val = float(pos.get("market_val", 0))
            asset_currency = pos.get("currency", "USD")
            is_cad = (asset_currency == "CAD")
            
            open_pnl = float(pos.get("unrealized_pl", 0))
            day_pnl  = float(pos.get("today_pl_val", 0))
            open_pnl_cad, open_pnl_usd = _to_cad_usd(open_pnl, is_cad, cad_usd_rate)
            day_pnl_cad,  day_pnl_usd  = _to_cad_usd(day_pnl,  is_cad, cad_usd_rate)

            domain_positions.append(Position(
                broker=self.broker_name,
                account_id=pos.get("account_id", "Unknown"),
                account_type=pos.get("account_type", "Unknown"),
                symbol=symbol,
                qty=float(pos.get("qty", 0)),
                closed_qty=float(pos.get("today_sell_qty", 0)),
                average_buying_price=float(pos.get("average_cost", 0)),
                day_pnl=day_pnl,
                day_pnl_cad=day_pnl_cad,
                day_pnl_usd=day_pnl_usd,
                open_pnl=open_pnl,
                open_pnl_cad=open_pnl_cad,
                open_pnl_usd=open_pnl_usd,
                closed_pnl=float(pos.get("realized_pl", 0)),
                market_val=market_val,
                market_val_usd=market_val if not is_cad else market_val / cad_usd_rate,
                market_val_cad=market_val if is_cad else market_val * cad_usd_rate,
                currency=asset_currency
            ))
            
        return domain_positions
