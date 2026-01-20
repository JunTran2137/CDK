from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_certificatemanager as acm


class ACMStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        acm_certs: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.acm_certs = dict()

        for key, value in acm_certs.items():
            self.acm_certs[key] = acm.Certificate(
                self,
                f"{key}-cert",
                certificate_name=value.get("name", None),
                domain_name=value.get("domain_name", None),
                subject_alternative_names=value.get("subject_alternative_names", None),
                allow_export=value.get("allow_export", None),
                validation=getattr(
                    acm.CertificateValidation, value.get("validation", None)
                )(),
                key_algorithm=acm.KeyAlgorithm(value.get("key_algorithm", None)),
            )
