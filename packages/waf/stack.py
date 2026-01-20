from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_wafv2 as waf


class WAFStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        waf_web_acls: dict,
        albs: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.waf_web_acls = dict()

        for key, value in waf_web_acls.items():
            rules = list()

            for item in value.get("rules", {}):
                if item.get("and_statement", None) is not None:
                    and_statements = list()

                    for sub_key, sub_value in (
                        item.get("and_statement", None).get("statements", None).items()
                    ):
                        if sub_key == "not_statement":
                            and_statements.append(
                                waf.CfnWebACL.StatementProperty(
                                    not_statement=waf.CfnWebACL.NotStatementProperty(
                                        statement=waf.CfnWebACL.StatementProperty(
                                            regex_match_statement=waf.CfnWebACL.RegexMatchStatementProperty(
                                                field_to_match=waf.CfnWebACL.FieldToMatchProperty(
                                                    body=waf.CfnWebACL.BodyProperty(
                                                        oversize_handling=sub_value.get(
                                                            "regex_match_statement"
                                                        )
                                                        .get("field_to_match", None)
                                                        .get("body", None)
                                                        .get("oversize_handling", None)
                                                    )
                                                ),
                                                regex_string=sub_value.get(
                                                    "regex_match_statement"
                                                ).get("regex_string", None),
                                                text_transformations=[
                                                    waf.CfnWebACL.TextTransformationProperty(
                                                        type=sub_value.get(
                                                            "regex_match_statement"
                                                        )
                                                        .get(
                                                            "text_transformations", None
                                                        )
                                                        .get("type", None),
                                                        priority=sub_value.get(
                                                            "regex_match_statement"
                                                        )
                                                        .get(
                                                            "text_transformations", None
                                                        )
                                                        .get("priority", None),
                                                    ),
                                                ],
                                            )
                                            if sub_value.get(
                                                "regex_match_statement", None
                                            )
                                            is not None
                                            else None,
                                        )
                                    )
                                )
                            )
                        elif sub_key == "byte_match_statement":
                            and_statements.append(
                                waf.CfnWebACL.StatementProperty(
                                    byte_match_statement=(
                                        waf.CfnWebACL.ByteMatchStatementProperty(
                                            field_to_match=waf.CfnWebACL.FieldToMatchProperty(
                                                method={}
                                                if sub_value.get(
                                                    "field_to_match", None
                                                ).get("method", None)
                                                is not None
                                                else None,
                                            ),
                                            search_string=sub_value.get(
                                                "search_string", None
                                            ),
                                            positional_constraint=sub_value.get(
                                                "positional_constraint", None
                                            ),
                                            text_transformations=[
                                                waf.CfnWebACL.TextTransformationProperty(
                                                    type=sub_value.get(
                                                        "text_transformations", None
                                                    ).get("type", None),
                                                    priority=sub_value.get(
                                                        "text_transformations", None
                                                    ).get("priority", None),
                                                ),
                                            ],
                                        )
                                    )
                                )
                            )

                rules.append(
                    waf.CfnWebACL.RuleProperty(
                        name=item.get("name", None),
                        action=waf.CfnWebACL.RuleActionProperty(
                            block=waf.CfnWebACL.BlockActionProperty()
                            if item.get("action", None) == "block"
                            else None
                        ),
                        priority=item.get("priority", None),
                        statement=waf.CfnWebACL.StatementProperty(
                            managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                                name=item.get("statement", None).get("name", None),
                                vendor_name=item.get("statement", None).get(
                                    "vendor_name", None
                                ),
                            )
                            if item.get("managed_rule_group_statement", None)
                            is not None
                            else None,
                            and_statement=waf.CfnWebACL.AndStatementProperty(
                                statements=and_statements
                            )
                            if item.get("and_statement", None) is not None
                            else None,
                        ),
                        visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                            cloud_watch_metrics_enabled=item.get(
                                "visibility_config", None
                            ).get("cloudwatch_metrics_enabled", None),
                            metric_name=item.get("visibility_config", None).get(
                                "metric_name", None
                            ),
                            sampled_requests_enabled=item.get(
                                "visibility_config", None
                            ).get("sampled_requests_enabled", None),
                        ),
                    )
                )

            self.waf_web_acls[key] = dict()

            self.waf_web_acls[key]["web_acl"] = waf.CfnWebACL(
                self,
                f"{key}-web-acl",
                scope=value.get("scope", None),
                name=value.get("name", None),
                description=value.get("description", None),
                visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=value.get(
                        "visibility_config", None
                    ).get("cloudwatch_metrics_enabled", None),
                    metric_name=value.get("visibility_config", None).get(
                        "metric_name", None
                    ),
                    sampled_requests_enabled=value.get("visibility_config", None).get(
                        "sampled_requests_enabled", None
                    ),
                ),
                default_action=waf.CfnWebACL.DefaultActionProperty(
                    allow=waf.CfnWebACL.AllowActionProperty()
                    if value.get("default_action", None) == "allow"
                    else None,
                ),
                token_domains=value.get("token_domains", None),
                rules=rules,
            )

            if value.get("alb_key", None) is not None:
                self.waf_web_acls[key]["association"] = waf.CfnWebACLAssociation(
                    self,
                    f"{key}-web-acl-association",
                    resource_arn=albs.get(value.get("alb_key", None), None)
                    .get("alb")
                    .load_balancer_arn,
                    web_acl_arn=self.waf_web_acls[key]["web_acl"].attr_arn,
                )
