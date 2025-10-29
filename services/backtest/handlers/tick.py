import datetime
import tempfile
from pathlib import Path
from typing import Any

import polars

from helpers.get_progress_between_dates import get_progress_between_dates
from models.candlestick import CandlestickModel
from services.logging import LoggingService


class TickHandler:
    _ticks_folder: Path = Path(tempfile.gettempdir()) / "horizon-connect" / "ticks"
    _from_date: datetime.datetime
    _to_date: datetime.datetime
    _restore_data: bool

    def __init__(self) -> None:
        self._log = LoggingService()
        self._log.setup("ticks_handler")

    def setup(self, **kwargs: Any) -> None:
        self._asset = kwargs.get("asset")
        self._db = kwargs.get("db")
        self._from_date = kwargs.get("from_date")
        self._to_date = kwargs.get("to_date")
        self._restore_data = kwargs.get("restore_data")

        if self._asset is None:
            raise ValueError("Asset is required")

        if self._db is None:
            raise ValueError("DB is required")

        if self._from_date is None:
            raise ValueError("From date is required")

        if self._to_date is None:
            raise ValueError("To date is required")

        if self._restore_data is None:
            raise ValueError("Restore data is required")

        self._download()

    def _download(self) -> None:
        if not self._restore_data:
            return

        self._log.info(f"Downloading data for {self._asset.symbol}")
        self._log.info(f"From date: {self._from_date}")
        self._log.info(f"To date: {self._to_date}")

        current_date = None
        start_timestamp = int(self._from_date.timestamp())
        end_timestamp = int(self._to_date.timestamp())
        candlesticks = []

        def _process_klines(klines: list[CandlestickModel]) -> None:
            nonlocal current_date
            nonlocal candlesticks
            candlesticks.extend([kline.to_dict() for kline in klines])
            current_date = candlesticks[-1]["kline_close_time"]

            progress = (
                get_progress_between_dates(
                    start_date_in_timestamp=start_timestamp,
                    end_date_in_timestamp=end_timestamp,
                    current_date_in_timestamp=int(current_date.timestamp()),
                )
                * 100
            )

            current_date_formatted = current_date.strftime("%Y-%m-%d %H:%M:%S")
            end_date_formatted = self._to_date.strftime("%Y-%m-%d %H:%M:%S")
            start_date_formatted = self._from_date.strftime("%Y-%m-%d %H:%M:%S")

            self._log.info(
                f"Downloading symbol: {self._asset.symbol}"
                f" | Starting time: {start_date_formatted}"
                f" | Current time: {current_date_formatted}"
                f" | Ending time: {end_date_formatted}"
                f" | Progress: {progress:.2f}%"
            )

        self._asset.gateway.get_klines(
            symbol=self._asset.symbol,
            timeframe="1m",
            from_date=self._from_date,
            to_date=self._to_date,
            callback=_process_klines,
        )

        ticks_folder = self._ticks_folder / self._asset.symbol
        ticks_folder.mkdir(parents=True, exist_ok=True)
        candlesticks = polars.DataFrame(candlesticks)
        ticks = candlesticks.select(
            [
                polars.col("kline_open_time")
                .dt.epoch("s")
                .cast(polars.Int64)
                .alias("id"),
                polars.col("close_price").alias("price"),
            ]
        )

        ticks.write_parquet(ticks_folder / "ticks.parquet")
        self._log.info(f"Data saved to {ticks_folder / 'ticks.parquet'}")
        self._log.info(f"Total ticks: {ticks.height}")

    @property
    def folder(self) -> Path:
        return self._ticks_folder

    @property
    def ticks(self) -> polars.DataFrame:
        ticks_folder = self.folder / self._asset.symbol
        ticks = polars.scan_parquet(ticks_folder / "ticks.parquet")

        return (
            ticks.filter(
                (polars.col("id") >= self._from_date.timestamp())
                & (polars.col("id") <= self._to_date.timestamp())
            )
            .sort("id")
            .collect(engine="streaming")
        )
