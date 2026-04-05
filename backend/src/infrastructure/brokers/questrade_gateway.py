from typing import List
# Assuming questrade_token_manager will be moved to the same directory or infra layer
from questrade_token_manager import make_api_request, QuestradeAuthError

from src.application.interfaces import BrokerGateway
from src.domain.models import Position

def _to_cad_usd(value: float, is_cad: bool, cad_usd_rate: float):
    if is_cad:
        return value, value / cad_usd_rate
    else:
        return value * cad_usd_rate, value

class QuestradeGateway(BrokerGateway):
    @property
    def broker_name(self) -> str:
        return "questrade"

    def fetch_positions(self, cad_usd_rate: float) -> List[Position]:
        try:
            accounts_resp = make_api_request('v1/accounts')
            accounts = accounts_resp.get('accounts', [])
            
            all_positions = []
            for acc in accounts:
                acc_num = acc.get('number')
                acc_type = acc.get('type', 'Unknown')
                try:
                    pos_resp = make_api_request(f'v1/accounts/{acc_num}/positions')
                    if pos_resp and 'positions' in pos_resp:
                        for position in pos_resp['positions']:
                            position['account_id'] = str(acc_num)
                            position['account_type'] = acc_type
                        all_positions.extend(pos_resp['positions'])
                except Exception as e:
                    pass
            
            if all_positions:
                try:
                    unique_sym_ids = list({str(p['symbolId']) for p in all_positions if p.get('symbolId')})
                    if unique_sym_ids:
                        meta_res = make_api_request('v1/symbols', params={'ids': ",".join(unique_sym_ids)})
                        currency_map = {
                            sym['symbolId']: sym.get('currency', 'CAD')
                            for sym in meta_res.get('symbols', [])
                        }
                        for pos in all_positions:
                            pos['currency'] = currency_map.get(pos.get('symbolId'), 'CAD')
                except Exception as e:
                    pass

            domain_positions = []
            for pos in all_positions:
                raw_symbol = pos.get("symbol", "")
                if not raw_symbol:
                    continue
                    
                symbol = raw_symbol
                qty = float(pos.get("openQuantity", 0))
                market_val = float(pos.get("currentMarketValue", 0))
                
                asset_currency = pos.get("currency", "CAD")
                is_cad = (asset_currency == "CAD")
                
                open_pnl = float(pos.get("openPnl", 0))
                day_pnl  = float(pos.get("dayPnl", 0))
                open_pnl_cad, open_pnl_usd = _to_cad_usd(open_pnl, is_cad, cad_usd_rate)
                day_pnl_cad,  day_pnl_usd  = _to_cad_usd(day_pnl,  is_cad, cad_usd_rate)

                domain_positions.append(Position(
                    broker=self.broker_name,
                    account_id=pos.get("account_id", "Unknown"),
                    account_type=pos.get("account_type", "Unknown"),
                    symbol=symbol,
                    qty=qty,
                    closed_qty=float(pos.get("closedQuantity", 0)),
                    average_buying_price=float(pos.get("averageEntryPrice", 0)),
                    day_pnl=day_pnl,
                    day_pnl_cad=day_pnl_cad,
                    day_pnl_usd=day_pnl_usd,
                    open_pnl=open_pnl,
                    open_pnl_cad=open_pnl_cad,
                    open_pnl_usd=open_pnl_usd,
                    closed_pnl=float(pos.get("closedPnl", 0)),
                    market_val=market_val,
                    market_val_usd=market_val if not is_cad else market_val / cad_usd_rate,
                    market_val_cad=market_val if is_cad else market_val * cad_usd_rate,
                    currency=asset_currency
                ))
            return domain_positions
            
        except Exception as e:
            err_str = str(e)
            if '1017' in err_str or '401' in err_str or 'Unauthorized' in err_str:
                 raise QuestradeAuthError(f"Questrade authentication failed: {e}")
            if isinstance(e, QuestradeAuthError):
                raise
            raise e
