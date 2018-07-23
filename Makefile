build:
	dep ensure
	go build -o bov live/main.go

run-web:
	cd scrapper; iex -S mix phx.server
