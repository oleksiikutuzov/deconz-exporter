# deconz-exporter

A super simple and dirty prometheus exporter for deconz.

Currently only exports battery and Zigbee humidity, temperature, pressure and open-close sensor.

```
Environment variables used to configure the exporter.
HOST_PORT       Sets port to expose the prometheus metrics on. default to 80
DECONZ_PORT     Sets the port deconz is available on. default to 9090
DECONZ_URL      Sets the url deconz can be reached by. default is 'localhost'
DECONZ_TOKEN    Sets the token used in the deconz api. default is ''
UPDATE_INTERVAL Sets interval between updates in seconds, default is 10.0 seconds
```
## Run with Docker

You can run the image in the background with the following command:
```
docker run -d -p 8090:9090 --restart unless-stopped -e HOST_PORT=9090 -e DECONZ_PORT=80 -e DECONZ_URL=XXXXXX -e DECONZ_TOKEN=XXXXXX -e UPDATE_INTERVAL=10.0 --name deconz-exporter oleksiikutuzov/deconz-exporter
```

To check image status:
```
docker ps -a
```

To stop running image:
```
docker stop deconz-exporter
```

To start running image:
```
docker start deconz-exporter
```

To delete:
```
docker rm deconz-exporter
```
## Run with Docker-compose

Create a `docker-compose.yml` file and add your configuration to it:

```
version: "3"

services:
  deconz-exporter:
    container_name: deconz-exporter
    image: oleksiikutuzov/deconz-exporter:latest
    restart: always
    ports:
      - 8090:9090
    environment:
      HOST_PORT: 9090
      DECONZ_PORT: 80
      DECONZ_URL: XXXXXX
      DECONZ_TOKEN: XXXXXX
      UPDATE_INTERVAL: 10.0
```

Then run the image with the following command:

```
docker-compose up -d
```
### To update the image:

```
docker pull oleksiikutuzov/deconz-exporter
```

And use the `docker-compose` command again:

```
docker-compose up -d
```
## Run with systemd

Almost all versions of Linux come with systemd out of the box, but if your’s didn’t come with it then you can simply run the following command:
```
sudo apt-get install systemd
```

To check which version of systemd you have simply run the command:
```
systemd --version
```

Now let's create configuration file:
```
sudo nano /etc/systemd/system/deconz-exporter.service
```

And paste the following into it:
```
# /etc/systemd/system/deconz-exporter.service
[Unit]
Description=deCONZ exporter service
After=multi-user.target

[Service]
Type=simple
User=<username>
Restart=always
Environment=HOST_PORT=8090
Environment=DECONZ_PORT=80
Environment=DECONZ_URL=XXXX
Environment=DECONZ_TOKEN=XXXX
Environment=UPDATE_INTERVAL=10.0
ExecStart=/usr/bin/python3 /home/<username>/deconz-exporter/main.py

[Install]
WantedBy=multi-user.target
```

Insert the username in your OS where `<username>` is written. The ExecStart flag takes in the command that you want to run. So basically the first argument is the python path (in my case it’s python3) and the second argument is the path to the script that needs to be executed. Restart flag is set to always because I want to restart my service if the server gets restarted. For more information on this, you can go to this link. Now we need to reload the daemon.
```
sudo systemctl daemon-reload
```

Let’s enable our service so that it doesn’t get disabled if the server restarts.
```
sudo systemctl enable deconz-exporter.service
```

And now let’s start our service.
```
sudo systemctl start deconz-exporter.service
```

Now our service is up and running.

### There are several commands you can do to start, stop, restart, and check status.

To stop the service:
```
sudo systemctl stop name_of_your_service
```
To restart:
```
sudo systemctl restart name_of_your_service
```

To check status:
```
sudo systemctl status name_of_your_service
```
