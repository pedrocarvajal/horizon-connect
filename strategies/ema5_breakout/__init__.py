from enums.timeframe import Timeframe
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

    def on_tick(self, tick: TickModel) -> None:
        super().on_tick(tick)

    def _on_close_1h_candle(self, candle: CandlestickModel) -> None:
        # open = candle.open_price
        # high = candle.high_price
        # low = candle.low_price
        # close = candle.close_price
        # open_time = candle.kline_open_time
        # close_time = candle.kline_close_time

        # self._log.info(
        #     f"[1H Candle Closed] "
        #     f"Time: {open_time:%Y-%m-%d %H:%M} → {close_time:%Y-%m-%d %H:%M} | "
        #     f"O: {open:.2f} H: {high:.2f} L: {low:.2f} C: {close:.2f}"
        # )

        pass

    def _on_close_1d_candle(self, candle: CandlestickModel) -> None:
        # open = candle.open_price
        # high = candle.high_price
        # low = candle.low_price
        # close = candle.close_price
        # open_time = candle.kline_open_time
        # close_time = candle.kline_close_time

        # self._log.info(
        #     f"[1D Candle Closed] "
        #     f"Time: {open_time:%Y-%m-%d %H:%M} → {close_time:%Y-%m-%d %H:%M} | "
        #     f"O: {open:.2f} H: {high:.2f} L: {low:.2f} C: {close:.2f}"
        # )

        pass
