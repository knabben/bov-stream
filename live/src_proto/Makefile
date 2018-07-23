build:
	protoc -I/usr/local/include -I. -I${GOPATH}/src --go_out=plugins=grpc:. data.proto
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. data.proto
