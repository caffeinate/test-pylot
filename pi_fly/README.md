# Pi Fly

Flask + shared memory to asynchronously connect a load of Rasberry Pi sensors and outputs to a web front end.

## Overview

Some sensors take a few seconds to return a reading, others can be polled faster. Create a load of polling loops at different speeds and use these to write to shared memory (see [scoreboard.py](scoreboard.py)).

Actionals read from the scoreboard; make decisions and switch relays.

This runs the solar thermal hot water heating in my house. 


## Unit test and getting started

```python
pipenv shell
pipenv install
python test/test_all.py 
```

## Run it

For now use screen

```shell
sudo python main.py live
```

where `live_config.py` is the name of the settings file in `/settings/`


### Old Pi issues

I tried this... but didn't work as pipenv reported no errors but didn't install them. But worth trying again with something more modern than python 3.4
```shell
pi@raspberrypi:~/test-pylot_pi_fly_combined $ pipenv --python 3.4
pi@raspberrypi:~/test-pylot_pi_fly_combined $ pipenv shell
(test-pylot_pi_fly_combined) pi@raspberrypi:~/test-pylot_pi_fly_combined $ cd pi_fly/
(test-pylot_pi_fly_combined) pi@raspberrypi:~/test-pylot_pi_fly_combined/pi_fly $ pipenv install
```

so I did this-
```shell
pip3 install gunicorn
pip3 install flask
pip3 install flask-sqlalchemy
```

Runs like this-
```shell
root@raspberrypi:/home/pi/test-pylot_pi_fly_combined/pi_fly# export PYTHONPATH="/home/pi/test-pylot_pi_fly_combined"
root@raspberrypi:/home/pi/test-pylot_pi_fly_combined/pi_fly# python3 main.py live
```

## Random Notes

* Nothing prevents multiple output devices claiming the same GPIO output pin or other resources. This could be a problem when the subclass of `AbstractOutput` limits the number of switches per time period.
