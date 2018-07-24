build:
	dep ensure
	go build -o bov live/main.go


run-api:
	cd scrapper; iex -S mix phx.server


run-web:
	cd web-client; yarn start
