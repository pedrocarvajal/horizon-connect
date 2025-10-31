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
            ),
            Timeframe.ONE_DAY: CandleService(
                timeframe=Timeframe.ONE_DAY, on_close=self._on_close_1d_candle
            ),
        }

        self._indicators = {
            "ema5": MAIndicator(
                period=5,
                exponential=True,
                candles=self._candles[Timeframe.ONE_HOUR].candles,
            ),
        }

    def on_tick(self, tick: TickModel) -> None:
        super().on_tick(tick)

    def _is_ready(self) -> bool:
        return (
            len(self._candles[Timeframe.ONE_HOUR].get(0)) > 0
            and len(self._candles[Timeframe.ONE_DAY].get(0)) > 0
        )

    def _on_close_1h_candle(self, candle: CandlestickModel) -> None:
        self._indicators["ema5"].refresh()
        open_time = candle.kline_open_time
        open_price = candle.open_price
        close_time = candle.kline_close_time
        close_price = candle.close_price
        high_price = candle.high_price
        low_price = candle.low_price

        if len(self._indicators["ema5"].values) > 0:
            ema5 = self._indicators["ema5"].values[-1]
            ema5_date = ema5.date
            ema5_value = ema5.value

            self._log.info(
                f"Open time: {open_time} | "
                f"Open price: {open_price} | "
                f"Close time: {close_time} | "
                f"Close price: {close_price} | "
                f"High price: {high_price} | "
                f"Low price: {low_price} | "
                f"EMA5: ({ema5_date}) {ema5_value}"
            )

    def _on_close_1d_candle(self, candle: CandlestickModel) -> None:
        pass
