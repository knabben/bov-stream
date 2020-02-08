company-fixture:
	cd scrapper; python main.py fetch-companies

stream-quotes:
	cd scrapper; python main.py fetch-price-tickers

run-web:
	cd web; iex -S mix phx.server
