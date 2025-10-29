from models.tick import TickModel
from services.logging import LoggingService
from services.strategy import StrategyService


class EMA5BreakoutStrategy(StrategyService):
    _enabled = True
    _name = "EMA5Breakout"

    def __init__(self) -> None:
        super().__init__()

        self._log = LoggingService()
        self._log.setup("ema5_breakout_strategy")
