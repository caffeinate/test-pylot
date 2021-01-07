# Pi Fly

Flask + shared memory to asynchronously connect a load of Rasberry Pi sensors and outputs to a web front end.

## Overview

Some sensors take a few seconds to return a reading, others can be polled faster. Create a load of polling loops at different speeds and use these to write to shared memory (see [scoreboard.py](scoreboard.py)).

The web front end shares the scoreboard so can quickly read the sensor values without reading from them directly.

At regular intervals sensor values are stored in an SqlAlchemy ORM managed SQLite database.

Events can be logged or stored in the database. 

Actionals read from the scoreboard; make decisions and switch relays. [main.py](main.py) is a good place to start having a browse.

This runs the solar thermal hot water heating in my house.


## Unit test and getting started

The "rpi.gpio" package will only install on a Raspberry Pi. It can be commented out of the Pipfile when developing and running unit tests on another platform.

The messing about with paths is just whilst this project lives in a mono-repo.

```python
cd pi_fly
pipenv shell
pipenv install
cd ..
export PYTHONPATH=`pwd`
python -m unittest pi_fly/test/test_*.py
```

## System Install

Installed on a Pi Zero November 2020.

```
Raspberry Pi OS (32-bit) Lite
Minimal image based on Debian Buster
Version:August 2020
Release date:2020-08-20
```

Not shown here I setup the pi [without a keyboard and mouse](https://howchoo.com/pi/how-to-set-up-raspberry-pi-without-keyboard-monitor-mouse) with the following-
* WIFI
* SSH with keys, no passwords
* Fixed IP address

Connect (it's in my /etc/hosts file so just `ssh -A zeropi` - the -A is so I can clone from github)

```shell
cd
git clone git@github.com:caffeinate/test-pylot.git
cd test-pylot

# everything from here as root
sudo su

apt install vim git python3-pip
pip3 install pipenv

# enable 1-wire bus
# .. Interfacing Options
# ... 1-Wire
# .... Would you like the one-wire interface to be enabled?
raspi-config


mkdir /data
cd /data
mv ~pi/test-pylot .

# find 1-wire devices and put these into the profile file (e.g. for live this would be /data/test-pylot/pi_fly/profiles/live_profile.py)
ls /sys/bus/w1/devices/

cd /data/test-pylot/pi_fly
pipenv install

cat > /etc/systemd/system/pi_fly.service << EOF
[Unit]
Description=Pi Fly
After=network.target

[Service]
ExecStart=/usr/local/bin/pipenv run python -u main.py live
WorkingDirectory=/data/test-pylot/pi_fly
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl enable pi_fly.service
```

## Authenticated views

Read only views are available without a username or password.

Set the password like this-
```shell
cd profiles/
echo -n supersecretpassword > session_password
```

## Useful Commands

Stop the pi_fly service-

```shell
systemctl start pi_fly.service
```

## Alternative ways to run it

Use `screen`

```shell
sudo su

# one off install
cd /data/test-pylot/pi_fly
pipenv install

# run it
screen bash
pipenv run python -u main.py live
```

where `live_profile.py` is the name of the profile file in `/profiles/`


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
