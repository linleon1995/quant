from src.eval.evaluator import Evaluator
from src.wallet import TradeRequest, BaseWallet, Coin


def test_basic_eval():
    wallet = BaseWallet()
    wallet.deposit(Coin('USDT', 10000))
    evaluator = Evaluator()

    assert evaluator.eval(wallet) is None

    trade_data = TradeRequest(action='buy', symbol='ETH', number=1.0, price=1000)
    wallet.add_trade(trade_data)
    assert evaluator.eval(wallet) is None

    trade_data = TradeRequest(action='buy', symbol='ETH', number=1.0, price=2000)
    wallet.add_trade(trade_data)
    assert evaluator.eval(wallet) is None

    trade_data = TradeRequest(action='sell', symbol='ETH', number=1.0, price=4000)
    wallet.add_trade(trade_data)
    eval_result = evaluator.eval(wallet)
    assert eval_result.avg_roi == 1500/4000
    assert eval_result.max_roi == 1500/4000
    assert eval_result.min_roi == 1500/4000
    assert eval_result.trade_times == 1
    assert eval_result.win_rate == 1.0

    trade_data = TradeRequest(action='sell', symbol='ETH', number=1.0, price=2000)
    wallet.add_trade(trade_data)
    eval_result = evaluator.eval(wallet)
    assert eval_result.avg_roi == 1000/5000
    assert eval_result.max_roi == 1500/4000
    assert eval_result.min_roi == -500/2500
    assert eval_result.trade_times == 2
    assert eval_result.win_rate == 0.5