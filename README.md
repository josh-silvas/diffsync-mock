# DiffSync Mock

This library is used to mock data and profile the performance of the diffsync libarary.

## Install the requirements

to use this example you must have some dependencies installed, please make sure to run 
```
poetry install
```

## Try the example

To properly mock data, be sure to load the mock data into a local .json file and for remote data for 
the DiffSync library to interact with, load data into a local Redis instance to mock remote data. (i.e. something
we can interact with programatically.)

To load local data, run `invoke` with the `load-local` option. You can specify here the number of 
records to mockup, the default will be 20,000 records
```
invoke load-local --records 20000
```
To load remote data, run `invoke` with the `load-redis` option. You can specify here the number of 
records to mockup, the default will be 20,000 records
```
invoke load-redis --records 20000
```
> NOTE: This will spin up a vanilla Redis docker container on port `7379` in one is not already running. 


Now that both local and remote data is loaded, you can run the filprofiler testing by either running `main.py`
directly, or using the `invoke run --redis` command. If you would like to run test using the local data source
and model as both local and remote (i.e. testing all data loaded into memory) then you can run the invoke command
without the `--redis` flag. `invoke run`

