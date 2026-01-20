from aws_cdk import (
    Stack,
    Duration,
    aws_elasticloadbalancingv2 as alb,
    aws_elasticloadbalancingv2_targets as alb_target,
)
from constructs import Construct


class ALBStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        albs: dict,
        vpcs: dict,
        security_groups: dict,
        ec2_instances: dict,
        acm_certs: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.albs = dict()

        for key, value in albs.items():
            self.albs[key] = dict()

            self.albs[key]["alb"] = alb.ApplicationLoadBalancer(
                self,
                f"{key}-alb",
                load_balancer_name=value.get("name", None),
                internet_facing=value.get("internet_facing", None),
                ip_address_type=alb.IpAddressType[value.get("ip_address_type", None)],
                vpc=vpcs.get(value.get("vpc_key", None), None),
                security_group=security_groups.get(value.get("sg_key", None), None),
            )

            for sub_key, sub_value in value.get("target_groups", {}).items():
                targets = list()

                for item in sub_value.get("targets", []):
                    targets.append(
                        alb_target.InstanceTarget(
                            instance=ec2_instances.get(item.get("ec2_key", None), None),
                            port=item.get("port", None),
                        )
                    )

                self.albs[key]["target_groups"] = dict()

                self.albs[key]["target_groups"][sub_key] = alb.ApplicationTargetGroup(
                    self,
                    f"{key}-alb-{sub_key}-target-group",
                    target_type=alb.TargetType[sub_value.get("target_type", None)],
                    target_group_name=sub_value.get("name", None),
                    protocol=alb.ApplicationProtocol[sub_value.get("protocol", None)],
                    port=sub_value.get("port", None),
                    ip_address_type=alb.TargetGroupIpAddressType[
                        sub_value.get("ip_address_type", None)
                    ],
                    vpc=vpcs.get(sub_value.get("vpc_key", None), None),
                    protocol_version=alb.ApplicationProtocolVersion[
                        sub_value.get("protocol_version", None)
                    ],
                    health_check=alb.HealthCheck(
                        enabled=sub_value.get("health_check", None).get(
                            "enabled", None
                        ),
                        protocol=alb.Protocol[
                            sub_value.get("health_check", None).get("protocol", None)
                        ],
                        path=sub_value.get("health_check", None).get("path", None),
                        port=sub_value.get("health_check", None).get("port", None),
                        healthy_threshold_count=sub_value.get("health_check", None).get(
                            "healthy_threshold", None
                        ),
                        unhealthy_threshold_count=sub_value.get(
                            "health_check", None
                        ).get("unhealthy_threshold", None),
                        timeout=Duration.seconds(
                            sub_value.get("health_check", None).get("timeout", None)
                        ),
                        interval=Duration.seconds(
                            sub_value.get("health_check", None).get("interval", None)
                        ),
                        healthy_http_codes=sub_value.get("health_check", None).get(
                            "matcher", None
                        ),
                    ),
                    targets=targets,
                )

            for sub_key, sub_value in value.get("listeners", {}).items():
                self.albs[key]["listeners"] = dict()

                self.albs[key]["listeners"][sub_key] = (
                    alb.ApplicationListener(
                        self,
                        f"{key}-alb-{sub_key}-listener",
                        load_balancer=self.albs[key]["alb"],
                        protocol=alb.ApplicationProtocol[
                            sub_value.get("protocol", None)
                        ],
                        port=sub_value.get("port", None),
                        certificates=[
                            alb.ListenerCertificate.from_certificate_manager(
                                acm_certs.get(sub_value.get("acm_key", None), None)
                            )
                        ]
                        if sub_value.get("protocol", None) == "HTTPS"
                        else None,
                        default_action=alb.ListenerAction.redirect(
                            protocol=sub_value.get("redirect", None).get(
                                "protocol", None
                            ),
                            port=sub_value.get("redirect", None).get("port", None),
                            permanent=sub_value.get("redirect", None).get(
                                "permanent", None
                            ),
                        )
                        if sub_value.get("protocol", None) == "HTTP"
                        else alb.ListenerAction.forward(
                            [
                                self.albs[key]["target_groups"].get(
                                    sub_value.get("forward", None).get(
                                        "target_group_key", None
                                    ),
                                    None,
                                )
                            ],
                        ),
                    ),
                )
