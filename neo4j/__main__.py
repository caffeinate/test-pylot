"""
Place a small EC2 instance on the default VPC's default subnet (this subnet is created if it doesn't already exist).

Run Neo4J in a docker container that restarts on reboot of the host.

See top level README.md
"""
import yaml

import pulumi
from pulumi_aws import ec2, iam

config = pulumi.Config()
ec2_keypair_name = config.require("ec2_keypair_name")

aws_config = pulumi.Config("aws")
aws_region = aws_config.require("region")


stack_name = pulumi.get_stack()
stack_label = f"neo4j_{stack_name}"

ec2_instance_size = "t2.small"
ec2_instance_name = stack_label
ec2_ami_owner = "099720109477"  # Ubuntu

ssh_port = 22
https_port = 443


# arbitrary choice of availability zone
any_az = aws_region + "b"
default_subnet = ec2.DefaultSubnet(
    "default_subnet",
    availability_zone=any_az,
    tags={
        "Name": f"Default subnet for {any_az}",
    },
)


def private_ips(args):
    """
    Find a couple of IP addresses. It's a hack, should at least check if they are already allocated
    see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_network_interfaces.html

    You'll get an error like this if the hack is too hackish-
    "creating EC2 Network Interface: InvalidIPAddress.InUse: The specified address is already in use."

    @param args: tuple with (0) being a cidr in a str
    @return tuple with two private ip addresses
    """
    cidr_block = args[0]  # e.g. "172.31.32.0/20"
    network_address, _netmask = cidr_block.split("/", 1)
    octets = network_address.split(".")
    final_octet = int(octets[-1])

    # anything outside of reserved range
    final_octet += 10

    address_0 = ".".join(octets[0:3]) + f".{final_octet+1}"
    address_1 = ".".join(octets[0:3]) + f".{final_octet+2}"
    return {"http_private_ip": address_0, "bolt_private_ip": address_1}


private_ips = pulumi.Output.all(default_subnet.cidr_block).apply(private_ips)


pulumi.export("http_private_ip", private_ips["http_private_ip"])
pulumi.export("bolt_private_ip", private_ips["bolt_private_ip"])

ami = ec2.get_ami(
    most_recent="true",
    owners=[ec2_ami_owner],
    filters=[
        ec2.GetAmiFilterArgs(name="name", values=["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*"]),
        ec2.GetAmiFilterArgs(name="root-device-type", values=["ebs"]),
        ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
    ],
)


def build_simple_security_group(*ports):
    label = f"secgrp_{stack_name}"

    ingress = []
    for port in ports:
        ingress.append(
            {
                "protocol": "tcp",
                "from_port": port,
                "to_port": port,
                "cidr_blocks": ["0.0.0.0/0"],
            }
        )

    pulumi_security_group = ec2.SecurityGroup(
        label,
        ingress=ingress,
        egress=[
            {
                "protocol": "-1",
                "from_port": 0,
                "to_port": 0,
                "cidr_blocks": ["0.0.0.0/0"],
            }
        ],
        vpc_id=default_subnet.vpc_id,
    )

    return pulumi_security_group


security_groups = [build_simple_security_group(ssh_port, https_port)]


# Allow secrets to be read - not resource specific
instance_policy = """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "*"
        }
    ]
}"""

instance_role = iam.Role(
    f"{stack_name}_policy",
    path="/",
    assume_role_policy="""{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
""",
    inline_policies=[
        iam.RoleInlinePolicyArgs(name="gateway_instance_policy", policy=instance_policy)
    ],
)
instance_profile = iam.InstanceProfile("instance_profile", role=instance_role.name)


# To run both bolt and https on the same port there need to be two public and two associated
# private IP adddresses


def extract_ipv4(args):
    "Get list of str from dict."
    priv_ips_dict = args[0]
    return list(priv_ips_dict.values())


private_ips_list = pulumi.Output.all(private_ips).apply(extract_ipv4)
nic = ec2.NetworkInterface(
    "neo4j_nic",
    subnet_id=default_subnet.id,
    private_ips=private_ips_list,
    security_groups=security_groups,
    tags={"Name": "Neo4j"},
)

http_eip = ec2.Eip(
    "http_eip",
    network_interface=nic.id,
    associate_with_private_ip=private_ips["http_private_ip"],
    tags={"Name": "Neo4j HTTPS"},
)
bolt_eip = ec2.Eip(
    "bolt_eip",
    network_interface=nic.id,
    associate_with_private_ip=private_ips["bolt_private_ip"],
    tags={"Name": "Neo4j Bolt"},
)

# Create EC2 instance
ec2_instance = ec2.Instance(
    ec2_instance_name,
    instance_type=ec2_instance_size,
    ami=ami.id,
    key_name=ec2_keypair_name,
    network_interfaces=[
        ec2.InstanceNetworkInterfaceArgs(
            device_index=0,
            network_interface_id=nic.id,
        )
    ],
    iam_instance_profile=instance_profile.id,
    tags={
        "Name": ec2_instance_name,
    },
)


pulumi.export("public_ipv4_bolt", bolt_eip.public_ip)
pulumi.export("public_ipv4_primary", http_eip.public_ip)
pulumi.export("source_ami_urm", ami.arn)
pulumi.export("instance_id", ec2_instance.id)
