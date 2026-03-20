#Flask Container

docker container based on Ubuntu (or `Dockerfile_ubi9` for Redhat's ubi9) runnning a simple hello world flask app.

Uses gunicorn as the WSGI server and provides a useful layer for deployment specific settings files (e.g. alternative setting for local development, containers etc.).

The `/show_env/` endpoint dumps environmental variables for debugging. It can be enabled by setting the `BASIC_HTTP_AUTH` environmental variable as `USERNAME:PASSWORDHASH`.

e.g. for username `superman` with password `supersecret`

```shell
docker build -t flask-http-auth .

HASHEDPASS=$(echo -n supersecret | md5 | awk '{ print $1 }')
USERPASS=superman:$HASHEDPASS

docker run \
 --env BASIC_HTTP_AUTH=$USERPASS \
 -p 5000:5000 \
 --detach \
 flask-http-auth
```
