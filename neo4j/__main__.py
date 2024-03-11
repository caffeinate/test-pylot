"""
Place a small EC2 instance on the default VPC's default subnet (this subnet is created if it doesn't already exist).

Run Neo4J in a docker container that restarts on reboot of the host.

See top level README.md
"""
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

# botl port supports TLS and non-TLS. Config passed to docker ensures TLS
bolt_port = 7687
neo4j_secure_port = 7473
ssh_port = 22

# arbitrary choice of availability zone
any_az = aws_region + "b"
default_subnet = ec2.DefaultSubnet(
    "default_subnet",
    availability_zone=any_az,
    tags={
        "Name": f"Default subnet for {any_az}",
    },
)

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


security_groups = [build_simple_security_group(bolt_port, neo4j_secure_port, ssh_port)]


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

# Create EC2 instance
ec2_instance = ec2.Instance(
    ec2_instance_name,
    instance_type=ec2_instance_size,
    vpc_security_group_ids=security_groups,
    ami=ami.id,
    key_name=ec2_keypair_name,
    associate_public_ip_address=True,
    subnet_id=default_subnet.id,
    iam_instance_profile=instance_profile.id,
    tags={
        "Name": ec2_instance_name,
    },
)

pulumi.export("source_ami_urm", ami.arn)
pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("instance_id", ec2_instance.id)
