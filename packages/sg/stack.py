from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ec2 as ec2


class SGStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        sgs: dict,
        sg_rules: list,
        vpcs: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.sgs = dict()

        for key, value in sgs.items():
            self.sgs[key] = ec2.SecurityGroup(
                self,
                f"{key}-sg",
                security_group_name=value.get("name", None),
                description=value.get("description", None),
                vpc=vpcs.get(value.get("vpc_key", None), None),
                allow_all_outbound=value.get("allow_all_outbound", False),
            )

            for rule in value.get("ingress_rules", []):
                self.sgs[key].add_ingress_rule(
                    peer=ec2.Peer.ipv4(rule[0]),
                    connection=ec2.Port.all_tcp()
                    if rule[1] == "all"
                    else ec2.Port.tcp(rule[1]),
                )

            for rule in value.get("egress_rules", []):
                self.sgs[key].add_egress_rule(
                    peer=ec2.Peer.ipv4(rule[0]),
                    connection=ec2.Port.all_tcp()
                    if rule[1] == "all"
                    else ec2.Port.tcp(rule[1]),
                )

        for rule in sg_rules:
            if rule["type"] == "ingress":
                self.sgs[rule["sg_key"]].add_ingress_rule(
                    peer=self.sgs[rule["source_sg_key"]],
                    description=rule.get("description", None),
                    connection=ec2.Port(
                        protocol=ec2.Protocol[rule["protocol"]],
                        from_port=rule["from_port"],
                        to_port=rule["to_port"],
                        string_representation=f"{rule['source_sg_key']}-{rule['sg_key']}-{rule['from_port']}-{rule['to_port']}",
                    ),
                )

            elif rule["type"] == "egress":
                self.sgs[rule["sg_key"]].add_egress_rule(
                    peer=self.sgs[rule["target_sg_key"]],
                    description=rule.get("description", None),
                    connection=ec2.Port(
                        protocol=ec2.Protocol[rule["protocol"]],
                        from_port=rule["from_port"],
                        to_port=rule["to_port"],
                        string_representation=f"{rule['sg_key']}-{rule['target_sg_key']}-{rule['from_port']}-{rule['to_port']}",
                    ),
                )
