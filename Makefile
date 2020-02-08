company-fixture:
	cd scrapper; python main.py fetch-companies

stream-quotes:
	cd scrapper; python main.py fetch-price-tickers

web:
	cd scrapper; iex -S mix phx.server

