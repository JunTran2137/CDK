#!/usr/bin/env python3
import yaml
import aws_cdk as cdk

from packages.vpc.stack import VPCStack
from packages.ec2.stack import EC2Stack
from packages.alb.stack import ALBStack
from packages.acm.stack import ACMStack
from packages.sg.stack import SGStack
from packages.waf.stack import WAFStack

app = cdk.App()
environment = app.node.try_get_context("env")
default_env = cdk.Environment(account="577638365470", region="ap-southeast-1")

with open(f"environments/{environment}/value.yaml", "r") as file:
    value = yaml.safe_load(file)

acm_stack = ACMStack(
    app,
    "ACMStack",
    acm_certs=value.get("acm_certs", {}),
    env=default_env,
)

vpc_stack = VPCStack(
    app,
    "VPCStack",
    vpcs=value.get("vpcs", {}),
    env=default_env,
)

sg_stack = SGStack(
    app,
    "SGStack",
    sgs=value.get("sgs", {}),
    sg_rules=value.get("sg_rules", []),
    vpcs=vpc_stack.vpcs,
    env=default_env,
)

ec2_stack = EC2Stack(
    app,
    "EC2Stack",
    ec2_instances=value.get("ec2_instances", {}),
    vpcs=vpc_stack.vpcs,
    security_groups=sg_stack.sgs,
    env=default_env,
)

alb_stack = ALBStack(
    app,
    "ALBStack",
    albs=value.get("albs", {}),
    vpcs=vpc_stack.vpcs,
    security_groups=sg_stack.sgs,
    ec2_instances=ec2_stack.ec2_instances,
    acm_certs=acm_stack.acm_certs,
    env=default_env,
)

waf_stack = WAFStack(
    app,
    "WAFStack",
    waf_web_acls=value.get("waf_web_acls", {}),
    albs=alb_stack.albs,
    env=default_env,
)

app.synth()
