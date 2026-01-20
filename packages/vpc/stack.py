from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ec2 as ec2


class VPCStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, vpcs: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpcs = dict()

        for key, value in vpcs.items():
            subnet_configuration = list()

            for item in value.get("subnet_configuration", []):
                subnet_configuration.append(
                    ec2.SubnetConfiguration(
                        name=item.get("name", None),
                        cidr_mask=item.get("cidr_mask", None),
                        subnet_type=ec2.SubnetType[item.get("subnet_type", None)],
                    )
                )

            self.vpcs[key] = ec2.Vpc(
                self,
                f"{key}-vpc",
                vpc_name=value.get("name", None),
                ip_addresses=ec2.IpAddresses.cidr(value.get("cidr", None)),
                ipv6_addresses=value.get("ipv6_addresses", None),
                default_instance_tenancy=ec2.DefaultInstanceTenancy[
                    value.get("instance_tenancy", None)
                ],
                availability_zones=value.get("availability_zones", None),
                subnet_configuration=subnet_configuration,
                nat_gateways=value.get("nat_gateways", None),
                gateway_endpoints=value.get("gateway_endpoints", None),
                enable_dns_hostnames=value.get("enable_dns_hostnames", None),
                enable_dns_support=value.get("enable_dns_support", None),
                restrict_default_security_group=value.get(
                    "restrict_default_security_group", False
                ),
            )
