from enums.timeframe import Timeframe
from indicators.ma import MAIndicator
from models.candlestick import CandlestickModel
from models.tick import TickModel
from services.candle import CandleService
from services.logging import LoggingService
from services.strategy import StrategyService


class EMA5BreakoutStrategy(StrategyService):
    _enabled = True
    _name = "EMA5Breakout"

    def __init__(self) -> None:
        super().__init__()

        self._log = LoggingService()
        self._log.setup("ema5_breakout_strategy")

        self._candles = {
            Timeframe.ONE_HOUR: CandleService(
                timeframe=Timeframe.ONE_HOUR, on_close=self._on_close_1h_candle
            )
        }

        self._indicators = {
            "ema5": MAIndicator(
                period=5,
                price_to_use="close_price",
                exponential=True,
                candles=self._candles[Timeframe.ONE_HOUR].candles,
            ),
        }

    def on_tick(self, tick: TickModel) -> None:
        super().on_tick(tick)

    def _on_close_1h_candle(self, candle: CandlestickModel) -> None:
        ema5 = self._indicators["ema5"]
        if len(ema5.values) > 0:
            ema5_value = ema5.values[-1]
            ema5_date = ema5_value.date
            ema5_value = ema5_value.value

            self._log.info(f"EMA5: ({ema5_date}) {ema5_value}")
