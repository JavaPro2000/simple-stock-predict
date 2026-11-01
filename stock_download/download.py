from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

CSV_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
DEFAULT_OUTPUT_DIR = Path("data")


def download_ticker_to_csv(
    ticker: str,
    start: date,
    end: date,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> Path:
    """Download daily OHLCV for ticker from start through end (inclusive) and write CSV."""
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("ticker must be non-empty")
    if start > end:
        raise ValueError(f"start ({start.isoformat()}) must be on or before end ({end.isoformat()})")

    frame = yf.download(
        tickers=symbol,
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
        group_by="column",
    )
    if frame is None or frame.empty:
        raise ValueError(
            f"no data for {symbol} between {start.isoformat()} and {end.isoformat()}"
        )

    csv_frame = _to_csv_frame(frame, symbol)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{symbol}_{start.isoformat()}_{end.isoformat()}.csv"
    csv_frame.to_csv(path, index=False)
    return path


def _to_csv_frame(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    flat = _flatten_columns(frame, symbol)
    indexed = flat.rename_axis("Date").reset_index()
    indexed["Date"] = pd.to_datetime(indexed["Date"]).dt.strftime("%Y-%m-%d")

    missing = [column for column in CSV_COLUMNS if column not in indexed.columns]
    if missing:
        raise ValueError(f"download missing columns {missing} for {symbol}")
    return indexed.loc[:, CSV_COLUMNS]


def _flatten_columns(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if not isinstance(frame.columns, pd.MultiIndex):
        return frame

    for level in range(frame.columns.nlevels):
        labels = [str(value) for value in frame.columns.get_level_values(level)]
        if symbol in labels:
            return frame.xs(symbol, axis=1, level=level)

    return frame.droplevel(-1, axis=1)


def _parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download Yahoo Finance daily prices and save them as CSV."
    )
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    parser.add_argument(
        "--start",
        required=True,
        type=_parse_iso_date,
        help="Inclusive start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        required=True,
        type=_parse_iso_date,
        help="Inclusive end date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for CSV files (default: data)",
    )
    args = parser.parse_args(argv)
    path = download_ticker_to_csv(args.ticker, args.start, args.end, args.output_dir)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
