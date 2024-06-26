from src.eval.evaluator import Evaluator
from src.wallet import TradeRequest

def test_basic_eval():
    evaluator = Evaluator()
    # evaluator.eval()
    # assert evaluator.metrics.avg_roi is None
    # assert evaluator.metrics.win_rate is None

    mock_buy_trade_data = TradeRequest(symbol='ETH', price=3000, 
                                    bridgecoin_name='USDT', bridgecoin_price=1, 
                                    action='buy', number=1.0)
    mock_buy_trade_data2 = TradeRequest(symbol='ETH', price=3400, 
                                    bridgecoin_name='USDT', bridgecoin_price=1, 
                                    action='buy', number=1.0)

    # evaluator.get_full_report()
    evaluator.add_trade(mock_buy_trade_data)
    evaluator.add_trade(mock_buy_trade_data2)
    assert evaluator.stocks['ETH'].avg_cost == 3200
    assert evaluator.stocks['ETH'].number == 2.0

    mock_sell_trade_data = TradeRequest(symbol='ETH', price=4500, 
                                     bridgecoin_name='USDT', bridgecoin_price=1, 
                                     action='sell', number=1.0)
    evaluator.add_trade(mock_sell_trade_data)

    assert evaluator.stocks['ETH'].avg_cost == 3200
    assert evaluator.stocks['ETH'].number == 1.0
    pass
    

    # assert evaluator.metrics.avg_roi == 50.0
    # assert evaluator.metrics.win_rate == 1.0

    # evaluator.add_trade(mock_buy_trade_data)
    # evaluator.add_trade(mock_sell_trade_data)
