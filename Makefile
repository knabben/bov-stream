
run-producer:
	go run producer/main.go stream

run-consumer:
	export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
	cd consumer; pipenv run python manage.py kafka_consumer

run-web:

	cd scrapper; iex -S mix phx.server

company-fixture:
	cd consumer; pipenv run python manage.py fetch_basic_companies
