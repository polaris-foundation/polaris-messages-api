# dhos-messages-api Integration Tests
This folder contains service-level integration tests for the dhos-messages-api.

## Running the tests
```
# run tests
$ make test-local

# inspect test logs
$ docker logs dhos-messages-integration-tests

# cleanup
$ docker-compose down
```