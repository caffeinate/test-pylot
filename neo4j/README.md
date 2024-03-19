# Neo4J Experiments

Run the Neo4J graph database in docker on a single EC2 instance with TLS. Stand it all up using Pulumi and Ansible.

Both bolt (neo4j API) and web front end are accessed though the https tcp port.

# TLS

Using [Lets Encrypt](https://letsencrypt.org/) for the TLS certificates. This part isn't scripted as it's a pain for a proof of concept/experient in an environment which uses the certificates outside of a webserver (i.e. the Neo4J server is used).

For everything below, *xxxx.com* is your domain

I created the TLS certs with a small EC2 instance with public IP address. Make DNS entries for domain neo4j.xxxx.com and neoapi.xxxxx.com so both certs can be made at once. Same IP address as an A record for both.

https://certbot.eff.org/instructions?ws=apache&os=ubuntufocal&tab=standard

TLDR; Summary-

```shell
sudo su
apt update
apt upgrade
/sbin/reboot
```

... a minute later ...

```shell
sudo su
apt install apache2 awscli
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot
certbot --apache
```

When "We were unable to find a vhost with a ServerName or Address of neoapi.xxxxx."
choose the ssl.conf option.

Make sure your AWS CLI tools have permission to write secrets. Maybe with *sts:AssumeRole* or a `~/.aws/credentials` file.
chmod -R og-rwx ~/.aws

Make all the cert files into a tarball ; base64 encode it so it can become a normal string secret and then send it to the AWS secrets manager-

```shell
cd /etc/letsencrypt/archive/neo4j.xxxx.com
tar cfvz /root/letsencrypt_neo4j_xxxx.tgz *.pem
cd
cat letsencrypt_neo4j_xxxx.tgz | base64 > letsencrypt_neo4j_xxxx.tgz.b64
aws --region eu-west-2 secretsmanager create-secret --name letsencrypt_xxxx --secret-string file:///root/letsencrypt_neo4j_xxxx.tgz.b64
```

Then terminate the EC2 instance.

# Build the EC2 instance

First, [setup Pulumi](https://www.pulumi.com/docs/get-started/).

Create a file called `neo4j_STACK_NAME_conf.yml` to include the startup password and AWS secret name (created in secion above) and domain names-

Replace *STACK_NAME* with the same stack name you give to pulumi. In the example below this is *dev*.

```
---
secret_name: aws_secrets_manager_secret_name
neo4j_password: supersecretpassword
bolt_dns_name: neoapi.xxxxx.com
https_dns_name: neo4j.xxxxx.com
```

Note-
* The choose a name for your stack. `dev` is used in the example below.
* Use your preferred AWS region. e.g. `eu-west-2`
* Setup an SSH keypair in AWS' EC2. This is *xxxx* below.

```shell
pipenv shell
pipenv install
pulumi stack init dev
pulumi config set aws:region eu-west-2
pulumi config set ec2_keypair_name xxxx
./go.sh dev
```

An EC2 instance will be created in the default subnet with a single public IP address. The instance will be provisioned (using ansible) to support a docker container running Neo4J.

Update your DNS records (corresponding to the TLS certificate) to point to the public IP address output at the end of the process above.

Point your browser at "https://xxxx.com". The username will be neo4j and the password will be whatever you set in `neo4j_STACK_NAME_conf.yml`.


# Running some code

Ensure you are in the pipenv shell created above and your current working directory is the same as this README and more importantly the `neo4j_STACK_NAME_conf.yml` file (which is used by the code to determine the password).


```shell
export PULUMI_STACK=$(pulumi stack --show-name)
python hello_world.py
```

It will print out the query that was run.

Then point your brower at the Neo4J server and you should see the new nodes.


# Cleaning up

To delete the resources above use `pulumi destroy`. It will display a list of resources that it will delete.

Note-
- You will loose any data within the neo4j databases
- The default subnet won't be deleted even if it was created by pulumi


# References

* https://neo4j.com/docs/operations-manual/current/docker/security/
* https://neo4j.com/docs/operations-manual/current/configuration/connectors/
