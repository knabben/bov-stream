build:
	dep ensure
	go build -o bov main.go
	sudo mv bov /usr/local/bin/
