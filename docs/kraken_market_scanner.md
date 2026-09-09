# Kraken market scanner
Run from repository root: `python scripts/kraken_market_scanner.py`.
Defaults: report `data/kraken_market_scan.json`, top 20 OHLC lookups, maximum 3 concurrent workers.
Options: `--top-n 0..200 --workers 1..3 --output PATH`.
No credentials, account calls, orders, margin, futures, or automatic trade selection.
The dynamic universe is currently online USD-quoted Kraken spot pairs returned by AssetPairs.
Other quotes, non-online status, dark-pool suffix, and explicit non-currency asset classes are excluded with reasons.
Default Kraken asset class excludes tokenized stocks. Public listing does not establish account or regional eligibility.
This is not every cryptocurrency worldwide. Newly listed pairs enter automatically when discoverable and online.
One bulk Ticker call scores every eligible pair with valid ticker data. Coverage records missing/invalid data.
Ranking is descending price change since midnight UTC, with estimated USD turnover as tie breaker.
Ticker opening price is today's UTC opening, NOT a rolling 24-hour reference.
Turnover is 24-hour base volume multiplied by 24-hour VWAP; spread uses (ask-bid)/midpoint.
Top N receive hourly OHLC enrichment. The final unfinished candle is always discarded.
Closed 1/4/24-hour returns use exact timestamp matches; missing history is null.
Volume ratio compares latest closed hour to mean of up to 24 preceding available hours.
These are descriptive measurements, not calibrated probabilities, predictions, net returns, or profitability claims.
HTTP timeout is 12 seconds per attempt; retries are bounded at three with exponential delay.
OHLC failures remain in each candidate and the report errors; ticker coverage and OHLC coverage are separate.
Report status complete means requested coverage succeeded, not that all coins received OHLC analysis.
Fatal discovery/bulk ticker failure writes a failed report and exits 1; partial enrichment writes partial report.
Output is replaced atomically; inspect timestamp and status before using any report.
Mock tests: `python -m unittest discover -s tests -p test_kraken_market_scanner.py`.
Official references:
- https://docs.kraken.com/api-reference/market-data/get-tradable-asset-pairs
- https://docs.kraken.com/api-reference/market-data/get-ticker-information
- https://docs.kraken.com/api-reference/market-data/get-ohlc-data
