OBJC_DISABLE_INITIALIZE_FORK_SAFETY := YES

run-producer:
	go run producer/main.go stream

run-consumer:
	pipenv run python consumer/manage.py kafka_consumer

run-web:
	cd scrapper; iex -S mix phx.server
