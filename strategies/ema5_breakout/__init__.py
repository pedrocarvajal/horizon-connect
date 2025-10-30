from datetime import timedelta

from models.candlestick import CandlestickModel
from models.tick import TickModel
from services.logging import LoggingService
from services.strategy import StrategyService


class EMA5BreakoutStrategy(StrategyService):
    _enabled = True
    _name = "EMA5Breakout"

    _1h_started: bool
    _1h_candles: list[CandlestickModel]

    def __init__(self) -> None:
        super().__init__()

        self._log = LoggingService()
        self._log.setup("ema5_breakout_strategy")

        # Strategy variables
        self._1h_candles = []
        self._1h_started = False

    def on_tick(self, tick: TickModel) -> None:
        self._build_1h_candle(tick)

    def _build_1h_candle(self, tick: TickModel) -> None:
        if not self._1h_started and tick.date.minute == 0:
            self._1h_started = True

        if not self._1h_started:
            return

        if len(self._1h_candles) == 0 or (
            tick.date >= self._1h_candles[-1].kline_close_time
        ):
            aligned_time = tick.date.replace(minute=0, second=0, microsecond=0)

            candle = CandlestickModel()
            candle.symbol = self.asset.symbol
            candle.source = self.asset.gateway.name
            candle.kline_open_time = aligned_time
            candle.kline_close_time = aligned_time + timedelta(hours=1)
            candle.open_price = tick.price
            candle.high_price = tick.price
            candle.low_price = tick.price
            candle.close_price = tick.price

            self._1h_candles.append(candle)

            if len(self._1h_candles) > 1:
                self._on_candle_closed(tick=tick, candle=self._1h_candles[-2])

        candle = self._1h_candles[-1]
        candle.high_price = max(candle.high_price, tick.price)
        candle.low_price = min(candle.low_price, tick.price)
        candle.close_price = tick.price

    def _on_candle_closed(self, tick: TickModel, candle: CandlestickModel) -> None:
        pass
