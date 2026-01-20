from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ec2 as ec2


class EC2Stack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ec2_instances: dict,
        vpcs: dict,
        security_groups: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ec2_instances = dict()

        for key, value in ec2_instances.items():
            block_devices = list()

            for item in value.get("block_devices", []):
                block_devices.append(
                    ec2.BlockDevice(
                        device_name=item.get("device_name", None),
                        volume=ec2.BlockDeviceVolume.ebs(
                            volume_size=item.get("volume_size", None),
                            volume_type=ec2.EbsDeviceVolumeType[
                                item.get("volume_type", None)
                            ],
                            iops=item.get("iops", None),
                            throughput=item.get("throughput", None),
                            delete_on_termination=item.get(
                                "delete_on_termination", None
                            ),
                            encrypted=item.get("encrypted", None),
                            kms_key=item.get("kms_key", None),
                        ),
                    )
                )

            self.ec2_instances[key] = ec2.Instance(
                self,
                f"{key}-instance",
                instance_name=value.get("name", None),
                machine_image=ec2.MachineImage.generic_linux(
                    {self.region: value.get("ami", None)}
                ),
                instance_type=ec2.InstanceType(value.get("instance_type", None)),
                key_pair=ec2.KeyPair.from_key_pair_name(
                    self, f"{key}-key", value.get("key_pair", None)
                )
                if value.get("key_pair", None)
                else None,
                vpc=vpcs.get(value.get("vpc_key", None), None),
                vpc_subnets=ec2.SubnetSelection(
                    subnets=[
                        vpcs.get(value.get("vpc_key", None), None).public_subnets[0]
                    ]
                ),
                associate_public_ip_address=value.get(
                    "associate_public_ip_address", None
                ),
                security_group=security_groups.get(value.get("sg_key", None), None),
                block_devices=block_devices,
                user_data=ec2.UserData.custom(value.get("user_data", None)),
            )
