# DiffSync Mock

This library is used to mock data and profile the performance of the diffsync libarary.

This example is the same as Example 3 except the Nautobot adapter and models are not leverating the internal datastore and all requests are made directly to Nautobot.

The comparison and synchronization of dataset is done between a local JSON file and the [public instance of Nautobot](https://demo.nautobot.com).

## Install the requirements

to use this example you must have some dependencies installed, please make sure to run 
```
pip install -r requirements.txt
```

## Try the example

The first time a lot of changes should be reported between Nautobot and the local data because by default the demo instance doesn't have the subregion define.
After the first sync, the diff should show no difference. 
At this point, Diffsync will be able to identify and fix all changes in Nautobot. You can try to add/update or delete any country in Nautobot and DiffSync will automatically catch it and it will fix it with running in sync mode.

```
### DIFF Compare the data between Nautobot and the local JSON file.
main.py --diff

### SYNC Update the list of country in Nautobot.
main.py --sync
```

