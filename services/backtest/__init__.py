import datetime
from multiprocessing import Queue
from typing import Optional

from configs.timezone import TIMEZONE
from interfaces.asset import AssetInterface
from models.tick import TickModel
from services.backtest.handlers.session import SessionHandler
from services.backtest.handlers.tick import TickHandler
from services.backtest.helpers.get_duration import get_duration
from services.logging import LoggingService


class BacktestService:
    # ───────────────────────────────────────────────────────────
    # PROPERTIES
    # ───────────────────────────────────────────────────────────
    _tick: TickHandler
    _session: SessionHandler

    # ───────────────────────────────────────────────────────────
    # CONSTRUCTOR
    # ───────────────────────────────────────────────────────────
    def __init__(
        self,
        asset: AssetInterface,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
        restore_data: bool = False,
        db_commands_queue: Optional[Queue] = None,
        db_events_queue: Optional[Queue] = None,
    ) -> None:
        self._start_at = datetime.datetime.now(tz=TIMEZONE)
        self._from_date = from_date
        self._to_date = to_date
        self._restore_data = restore_data

        self._log = LoggingService()
        self._log.setup("backtest")
        self._log.info("Backtesting service started")

        self._asset = asset()
        self._session = SessionHandler()
        self._tick = TickHandler()

        tick_setup = {
            "from_date": from_date,
            "to_date": to_date,
            "restore_data": restore_data,
        }

        instances = {
            "session": self._session,
            "tick": self._tick,
            "asset": self._asset,
        }

        queues = {
            "db_commands_queue": db_commands_queue,
            "db_events_queue": db_events_queue,
        }

        self._session.setup(
            **instances,
            **queues,
        )

        self._tick.setup(
            **instances,
            **tick_setup,
        )

        self._asset.setup(
            backtest=True,
            **instances,
            **queues,
        )

    # ───────────────────────────────────────────────────────────
    # PUBLIC METHODS
    # ───────────────────────────────────────────────────────────
    def run(self) -> None:
        start_timestamp = int(self._from_date.timestamp())
        end_timestamp = int(self._to_date.timestamp())
        expected_tick = int((end_timestamp - start_timestamp) / 60)
        ticks = self._tick.ticks
        enabled_strategies = len(self._asset.strategies)

        self._log.info(f"Total ticks: {ticks.height}")
        self._log.info(f"Expected ticks: {expected_tick}")

        if ticks.height == 0:
            self._log.error("No ticks found")
            return

        if enabled_strategies == 0:
            self._log.error("No enabled strategies found")
            return

        for tick in ticks.iter_rows(named=True):
            tick_model = TickModel()
            tick_model.date = datetime.datetime.fromtimestamp(tick["id"], tz=TIMEZONE)
            tick_model.price = tick["price"]
            self._asset.on_tick(tick_model)

        self._on_end()

    # ───────────────────────────────────────────────────────────
    # PRIVATE METHODS
    # ───────────────────────────────────────────────────────────
    def _on_end(self) -> None:
        start_timestamp = int(self._from_date.timestamp())
        end_timestamp = int(self._to_date.timestamp())
        expected_tick = int((end_timestamp - start_timestamp) / 60)

        self._asset.on_end()

        end_at = datetime.datetime.now(TIMEZONE)
        quality = (self._tick.ticks.height / expected_tick) * 100
        duration = get_duration(self._start_at, end_at)

        self._log.info(
            f"Backtest completed in: {duration} | "
            f"Quality: {quality:.2f}% | "
            f"Session ID: {self._session.id}"
        )
