import datetime
from typing import Optional

from enums.order_side import OrderSide
from enums.order_type import OrderType
from enums.timeframe import Timeframe
from indicators.ma import MAIndicator
from models.order import OrderModel
from models.tick import TickModel
from services.candle import CandleService
from services.logging import LoggingService
from services.strategy import StrategyService


class EMA5BreakoutStrategy(StrategyService):
    _enabled = True
    _name = "EMA5Breakout"

    _do_we_have_open_positions: bool = False
    _previous_day_ema5_max: Optional[float] = None

    def __init__(self) -> None:
        super().__init__()

        self._log = LoggingService()
        self._log.setup("ema5_breakout_strategy")

        self._candles = {
            Timeframe.ONE_HOUR: CandleService(
                timeframe=Timeframe.ONE_HOUR,
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

    def on_new_hour(self, tick: TickModel) -> None:
        self._check_breakout(tick)

    def on_new_day(self, tick: TickModel) -> None:
        self._calculate_previous_day_ema5_max(tick)

    def on_transaction(self, order: OrderModel) -> None:
        self._log.info("Transaction:")
        self._log.debug(order.to_json())

    def _check_breakout(self, tick: TickModel) -> None:
        if not self._previous_day_ema5_max:
            return

        if self._do_we_have_open_positions:
            return

        if tick.price > self._previous_day_ema5_max:
            self._log.info(
                f"Breakout: {tick.date} | "
                f"Opening price: {tick.price} | "
                f"Previous day EMA5 max: {self._previous_day_ema5_max}"
            )

            order = OrderModel()
            order.symbol = self.asset.symbol
            order.gateway = self.asset.gateway.name
            order.side = OrderSide.BUY
            order.price = tick.price
            order.volume = 0.01

            self.orderbook.push(order)
            self._do_we_have_open_positions = True

    def _calculate_previous_day_ema5_max(self, tick: TickModel) -> None:
        today = tick.date
        yesterday = today - datetime.timedelta(days=1)
        self._previous_day_ema5_max = max(
            [
                ema5.value
                for ema5 in self._indicators["ema5"].values
                if ema5.date >= yesterday and ema5.date < today
            ]
        )
