"""
Description:
=============
    This Python 3 script is able to perform Aviatrix-TGW-Orchestrator operations.


Prerequisites:
==============
    + Aviatrix Controller instance
    + Controller version is 4.3 or newer releases
    + AWS TGW


Input Parameters for the Script:
=================================
"ResourceProperties": {
    "LambdaInvokerTypeParam": "terraform",  # (REQUIRED)  # Valid values: "terraform", "tf", "cloudformation", "cf"
    "PrefixStringParam": "avx",  # (OPTIONAL)
    "KeywordForCloudWatchLogParam": "avx-lambda-function",  # (OPTIONAL)  This parameter is a string which is being used for CloudWatch loggin
    "DelimiterForCloudWatchLogParam": "---",  # (OPTIONAL) This parameter is used along with the parameter "KeywordForCloudWatchLogParam"

    "AviatrixControllerHostnameParam": "123.123.123.123",  # (REQUIRED)
    "AviatrixApiVersionParam": "v1",  # (OPTIONAL) Default value is "v1"
    "AviatrixApiRouteParam": "api/",  # (OPTIONAL) Default value is "api/"
    "AviatrixControllerAdminPasswordParam": "Aviatrix123!",  # (REQUIRED)

    "AviatrixActionParam": "CREATE",  # (REQUIRED)  Valid values: "CREATE", "UPDATE", "DELETE", "ATTACH", "DETACH"

    "AccessAccountNameParam": "my-access-account",    # 'CREATE'
    "TgwRegionNameParam": "us-west-1"
    "TgwName": "my-aws-tgw-009"
    "AwsSideASNumberParam": "65003"
    "TgwAccessAccountNameParam": "my-access-account-03"

    "AccessAccountNameParam": "my-access-account",  # 'DELETE'
    "TgwNameParam": "my-aws-tgw-009"

    "VpcAccessAccountNameParam": "my-access-account",  # 'ATTACH'
    "VpcRegionNameParam": "us-west-1"
    "VpcIdParam": "vpc-abc123"
    "TgwNameParam": "my-tgw-009",
    "SecurityRouteDomainNameParam": "Default_Domain"  # Valid Values: "Default_Domain" || "Shared_Service_Domain" || "Your_Custom_Domain"
    "SubnetListParam": ["subnet-abc123", "subnet-xyz789"]
}


Author:
========
    Ryan Liu (Aviatrix System)
"""

# print("Starting Aviatrix Lambda function to initialize an Aviatrix controller instance!\n\n")

import time
import os
import json
import traceback
import requests


requests.packages.urllib3.disable_warnings()


# Global Variables
pass


class AviatrixException(Exception):
    def __init__(self, message="Aviatrix Error Message: ..."):
        super(AviatrixException, self).__init__(message)
# END class MyException


def lambda_handler(event, context):
    print(event)  # For debugging purpose if ever needed

    ### Get the values from "event" for variables, ONLY if the keys are found in the "event" dictionary
    keyword_for_log = ""
    if "KeywordForCloudWatchLogParam" in event["ResourceProperties"] and "DelimiterForCloudWatchLogParam" in event["ResourceProperties"]:
        keyword_for_log = "{0}{1}".format(
            str(event["ResourceProperties"]["KeywordForCloudWatchLogParam"]),
            str(event["ResourceProperties"]["DelimiterForCloudWatchLogParam"])
        )
    lambda_invoker_type = get_lambda_invoker_type(event)
    tgw_action = event["ResourceProperties"]["AviatrixActionParam"]
    controller_hostname = str(event["ResourceProperties"]["AviatrixControllerHostnameParam"])

    try:
        data = _lambda_handler(event, context)
    except AviatrixException as e:
        traceback_msg = traceback.format_exc()
        # print(keyword_for_log + "Oops! Aviatrix Lambda caught an exception! The traceback message is: ")
        # print(traceback_msg)
        lambda_failure_reason = "Aviatrix Error: " + str(e)
        print(keyword_for_log + lambda_failure_reason)
        if lambda_invoker_type == "terraform" or lambda_invoker_type == "tf":
            response_for_terraform = _build_response_for_terraform(
                event=event,
                status=False,
                message=lambda_failure_reason,
                keyword_for_log=keyword_for_log,
                indent=""
            )
            return response_for_terraform
        elif lambda_invoker_type == "cloudformation" or lambda_invoker_type == "cf":
            response_for_cloudformation = _build_response_for_cloudformation_stack(
                event=event,
                context=context,
                status="FAILED",
                reason=lambda_failure_reason,
                keyword_for_log=keyword_for_log,
                indent=""
            )

            response = requests.put(
                url=event["ResponseURL"],
                data=json.dumps(response_for_cloudformation)
            )

            return response_for_cloudformation
        elif lambda_invoker_type == "generic":
            response_for_generic_lambda_invoker = _build_response_for_generic_lambda_invoker(
                event=event,
                status=False,
                message=lambda_failure_reason,
                keyword_for_log=keyword_for_log,
                indent=""
            )
            return response_for_generic_lambda_invoker
        else:
            lambda_failure_reason = "Aviatrix Error: Aviatrix Lambda does not support the Invoker-Type: " + \
                      str(lambda_invoker_type)
            response_for_terraform = _build_response_for_generic_lambda_invoker(
                event=event,
                status=False,
                message=lambda_failure_reason,
                keyword_for_log=keyword_for_log,
                indent=""
            )
            return response_for_terraform
        # END if-else
    except Exception as e:  # pylint: disable=broad-except
        traceback_msg = traceback.format_exc()
        lambda_failure_reason = "Oops! Aviatrix Lambda caught an exception! The traceback message is: \n" + str(traceback_msg)
        print(keyword_for_log + lambda_failure_reason)
        if lambda_invoker_type == "terraform" or lambda_invoker_type == "tf":
            response_for_terraform = _build_response_for_terraform(
                event=event,
                status=False,
                message=lambda_failure_reason
            )
            return response_for_terraform
        elif lambda_invoker_type == "cloudformation" or lambda_invoker_type == "cf":
            response_for_cloudformation = _build_response_for_cloudformation_stack(
                event=event,
                context=context,
                status="FAILED",
                reason=lambda_failure_reason,
                keyword_for_log=keyword_for_log
            )
            response = requests.put(
                url=event["ResponseURL"],
                data=json.dumps(response_for_cloudformation)
            )
            return response_for_cloudformation
        elif lambda_invoker_type == "generic":
            response_for_generic_lambda_invoker = _build_response_for_generic_lambda_invoker(
                event=event,
                status=False,
                message=lambda_failure_reason,
                keyword_for_log=keyword_for_log,
                indent=""
            )
            return response_for_generic_lambda_invoker
        else:
            lambda_failure_reason = "Aviatrix Error: Aviatrix Lambda does not support the Invoker Type: " + \
                      str(lambda_invoker_type)
            response_for_terraform = _build_response_for_generic_lambda_invoker(
                event=event,
                status=False,
                message=lambda_failure_reason
            )
            return response_for_terraform
        # END if-else
    # END try-except


    # At this point, Aviatrix/AWS Lambda function has finished the tasks without error


    success_msg = 'Successfully completed Aviatrix Lambda script for Aviatrix Action: <<<' + tgw_action + \
                  '>>> at Aviatrix Controller: ' + controller_hostname

    if lambda_invoker_type == "terraform" or lambda_invoker_type == "tf":
        response_for_terraform = _build_response_for_terraform(
            event=event,
            status=True,
            message=success_msg,
            keyword_for_log=keyword_for_log,
            indent=""
        )
        return response_for_terraform
    elif lambda_invoker_type == "cloudformation" or lambda_invoker_type == "cf":
        data = {  # MMM
            "message": success_msg,
            "tgw-region": "mars-west-1"
        }
        response_for_cloudformation = _build_response_for_cloudformation_stack(
            event=event,
            context=context,
            status="SUCCESS",
            data=data,  # MMM
            keyword_for_log=keyword_for_log,
            indent=""
        )
        response = requests.put(
            url=event["ResponseURL"],
            data=json.dumps(response_for_cloudformation)  # json.dumps() converts dict() to string
        )
        return response_for_cloudformation
    elif lambda_invoker_type == "generic":
        response_for_generic_lambda_invoker = _build_response_for_generic_lambda_invoker(
            event=event,
            status=True,
            message=success_msg,
            keyword_for_log=keyword_for_log,
            indent=""
        )
        return response_for_generic_lambda_invoker
    else:
        '''
            This section should never be run because get_lambda_invoker_type() already filters the names,
            but it's just a precaution.
        '''
        err_msg = "Aviatrix Error: Aviatrix Lambda does not support the Invoker Type: " + \
                  str(lambda_invoker_type)
        response_for_generic_lambda_invoker = _build_response_for_generic_lambda_invoker(
            event=event,
            status=False,
            message=err_msg,
            keyword_for_log=keyword_for_log,
            indent=""
        )
        return response_for_generic_lambda_invoker
    # END if-else
# END def lambda_handler()


def get_lambda_invoker_type(event=dict()):
    lambda_invoker_type = "generic"  # set default value
    key = "LambdaInvokerTypeParam"


    ### Identify if LambdaInvokerTypeParam is Aviatrix Terraform
    if key in event["ResourceProperties"]:  # IF the AWS Lambda invoker passed its type in "event"
        lambda_invoker_type = "{}".format(str(event["ResourceProperties"]["LambdaInvokerTypeParam"])).lower()
        if _is_valid_lambda_invoker_type(lambda_invoker_type):
            return lambda_invoker_type
        # END inner if
    # END outer if

    ### Identify if LambdaInvokerTypeParam is AWS Cloudformation stack
    try:
        cf_stack_id = event["StackId"]
        lambda_invoker_type = "cloudformation"
        print("Aviatrix Lambda Invoker type is: AWS CFT")
    except (KeyError, AttributeError, TypeError):
        err_msg = 'Aviatrix Error: LambdaInvokerTypeParam is NOT from "terraform" or "cloudformation"'
        raise AviatrixException(
            message=err_msg,
        )

    return lambda_invoker_type
# END def get_lambda_invoker_type()


def _is_valid_lambda_invoker_type(lambda_invoker_type=""):
    lambda_invoker_type = lambda_invoker_type.lower()
    if lambda_invoker_type == "terraform" or \
       lambda_invoker_type == "tf" or \
       lambda_invoker_type == "cloudformation" or \
       lambda_invoker_type == "cf":
        return True
    else:
        return False
# END def is_valid_invoker_type()


def _lambda_handler(event, context):
    ##### Display all parameters from lambda "event" object
    ### Get the values from "event" for variables, ONLY if the keys are found in the "event" dictionary
    keyword_for_log = ""
    if "KeywordForCloudWatchLogParam" in event["ResourceProperties"] and \
       "DelimiterForCloudWatchLogParam" in event["ResourceProperties"]:
        keyword_for_log = "{0}{1}".format(
            str(event["ResourceProperties"]["KeywordForCloudWatchLogParam"]),
            str(event["ResourceProperties"]["DelimiterForCloudWatchLogParam"])
        )

    print(keyword_for_log + 'START: Display all parameters from lambda "event" object')
    print_lambda_event(event, keyword_for_log=keyword_for_log, indent="    ")
    prefix_str = event["ResourceProperties"]["PrefixStringParam"]
    ucc_hostname = event["ResourceProperties"]["AviatrixControllerHostnameParam"]
    aviatrix_api_version = event["ResourceProperties"]["AviatrixApiVersionParam"]
    aviatrix_api_route = event["ResourceProperties"]["AviatrixApiRouteParam"]
    admin_password = event["ResourceProperties"]["AviatrixControllerAdminPasswordParam"]
    aviatrix_action = event["ResourceProperties"]["AviatrixActionParam"]

    ### Reconstruct some parameters
    ucc_hostname = ucc_hostname.rstrip()  # Remove the trailing whitespace characters
    ucc_hostname = ucc_hostname.lstrip()  # Remove the leading whitespace characters
    api_endpoint_url = "https://" + ucc_hostname + "/" + aviatrix_api_version + "/" + aviatrix_api_route

    print(keyword_for_log + 'ENDED: Display all parameters from lambda "event" object\n\n')


    ### Wait until apache2 of controller is up and running
    print(keyword_for_log + 'START: Wait until API server of controller is up and running')
    wait_until_controller_api_server_is_ready(
        ucc_public_ip=ucc_hostname,
        api_version=aviatrix_api_version,
        api_route=aviatrix_api_route,
        total_wait_time=120,  # second(s)  The average time for a brand new controller is about 60 seconds
        interval_wait_time=10,  # second(s)
        keyword_for_log=keyword_for_log,
        indent="    "
    )
    print(keyword_for_log + 'ENDED: Wait until API server of controller is up and running\n\n')


    ### Login Aviatrix Controller as admin
    print(keyword_for_log + 'START: Invoke Aviatrix API to login Aviatrix Controller')
    response = login(
        api_endpoint_url=api_endpoint_url,
        username="admin",
        password=admin_password,
        keyword_for_log=keyword_for_log
    )
    verify_aviatrix_api_response_login(response=response, keyword_for_log=keyword_for_log, indent="    ")
    CID = response.json()["CID"]
    print(keyword_for_log + 'ENDED: Invoke Aviatrix API to login Aviatrix Controller\n\n')


    ### Check if the controller has already been initialized
    print(keyword_for_log + 'START: Check if the controller has already been initialized')
    is_ctlr_initialized = is_controller_initialized(
        api_endpoint_url=api_endpoint_url,
        CID=CID,
        keyword_for_log=keyword_for_log
    )
    if is_ctlr_initialized:
        print(keyword_for_log + "    Good! Aviatrix controller has already been initialized.")
    else:
        print(keyword_for_log + "    Error! Aviatrix controller has not been initialized yet.")
        avx_err_msg = "Error! Aviatrix controller has not been initialized yet."
        raise AviatrixException(message=avx_err_msg)
    print(keyword_for_log + 'ENDED: Check if the controller has already been initialized\n\n')


    ### Get controller version
    print(keyword_for_log + 'START: Get controller version')
    controller_version = get_controller_version(
        api_endpoint_url=api_endpoint_url,
        CID=CID,
        keyword_for_log=keyword_for_log
    )
    print(keyword_for_log + '    Controller Version: ' + str(controller_version))
    print(keyword_for_log + 'ENDED: Get controller version\n\n')


    data = None
    ### Execute the function(s) depends on the "action" user/CFT provides
    if 'CREATE' == aviatrix_action.upper():
        print(keyword_for_log + 'START: Aviatrix Action: "CREATE"')
        access_account_name  = event['ResourceProperties']['AccessAccountNameParam']
        tgw_region_name      = event['ResourceProperties']['TgwRegionNameParam']
        aws_tgw_name         = event['ResourceProperties']['TgwNameParam']
        aws_side_AS_numeber  = event['ResourceProperties']['AwsSideASNumberParam']
        response = create_aws_tgw(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            access_account_name=access_account_name,
            region_name=tgw_region_name,
            aws_tgw_name=aws_tgw_name,
            aws_side_AS_numeber=aws_side_AS_numeber,
            keyword_for_log=keyword_for_log,
            indent="    "
        )
        pydict = response.json()
        print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
        _handle_aviatrix_api_response_from_create_aws_tgw(response=response)
        data = dict()  # MMM to be implemented after feedback
        print(keyword_for_log + 'ENDED: Aviatrix Action: "CREATE"\n\n')
    elif 'DELETE' == aviatrix_action.upper():
        print(keyword_for_log + 'START: Aviatrix Action: "DELETE"')
        aws_tgw_name         = event['ResourceProperties']['TgwNameParam']
        response = delete_aws_tgw(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            aws_tgw_name=aws_tgw_name,
            keyword_for_log=keyword_for_log,
            indent="    "
        )
        pydict = response.json()
        print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
        _handle_aviatrix_api_response_from_delete_aws_tgw(response=response)
        data = dict()  # MMM to be implemented after feedback
        print(keyword_for_log + 'ENDED: Aviatrix Action: "DELETE"\n\n')
    elif 'ATTACH' == aviatrix_action.upper():
        print(keyword_for_log + 'START: Aviatrix Action: "ATTACH"')
        vpc_access_account_name    = event['ResourceProperties']['VpcAccessAccountNameParam']
        vpc_region_name            = event['ResourceProperties']['VpcRegionNameParam']
        vpc_id                     = event['ResourceProperties']['VpcIdParam']

        aws_tgw_name               = event['ResourceProperties']['TgwNameParam']
        route_domain_name          = event['ResourceProperties']['RouteDomainNameParam']
        subnet_list                = event['ResourceProperties']['SubnetListParam']

        response = attach_vpc_to_aws_tgw(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            vpc_access_account_name=vpc_access_account_name,
            vpc_region_name=vpc_region_name,
            vpc_id=vpc_id,
            aws_tgw_name=aws_tgw_name,
            route_domain_name=route_domain_name,
            subnet_list=subnet_list,
            keyword_for_log=keyword_for_log,
            indent="    "
        )
        pydict = response.json()
        print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
        _handle_aviatrix_api_response_from_attach_vpc_to_aws_tgw(response=response)
        data = dict()  # MMM to be implemented after feedback
        print(keyword_for_log + 'ENDED: Aviatrix Action: "ATTACH"\n\n')
    elif 'DETACH' == aviatrix_action.upper():
        print(keyword_for_log + 'START: Aviatrix Action: "DETACH"')
        vpc_id                     = event['ResourceProperties']['VpcIdParam']
        aws_tgw_name               = event['ResourceProperties']['TgwNameParam']

        response = detach_vpc_from_aws_tgw(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            vpc_id=vpc_id,
            aws_tgw_name=aws_tgw_name,
            keyword_for_log=keyword_for_log,
            indent="    "
        )
        pydict = response.json()
        print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
        _handle_aviatrix_api_response_from_detach_vpc_from_aws_tgw(response=response)  # to be implemented
        data = dict()  # MMM to be implemented after feedback
        print(keyword_for_log + 'ENDED: Aviatrix Action: "DETACH"\n\n')
    elif 'CreateAccessAccount'.upper() == aviatrix_action.upper():
        print(keyword_for_log + 'START: Aviatrix Action: "CreateAccessAccount"')
        new_access_account_name   = event['ResourceProperties']['AccessAccountNameParam']
        # access_account_password = "Aviatrix123!"  # This parameter is no longer required after version ???
        # account_email           = "test@aviatrix.com"  # This parameter is no longer required after version ???
        cloud_type                = "1"
        aws_account_number        = event['ResourceProperties']['AWS_Account_ID']
        is_iam_role_based         = "true"
        aviatrix_app_role_arn     = event['ResourceProperties']['AviatrixAppRoleArnParam']
        aviatrix_ec2_role_arn     = event['ResourceProperties']['AviatrixEc2RoleArnParam']

        response = create_access_account(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            controller_version="4.0",
            account_name=new_access_account_name,
            # account_password="**********",
            # account_email="test@aviatrix.com",
            cloud_type=cloud_type,
            aws_account_number=aws_account_number,
            is_iam_role_based=is_iam_role_based,
            app_role_arn=aviatrix_app_role_arn,
            ec2_role_arn=aviatrix_ec2_role_arn,
            keyword_for_log=keyword_for_log,
            indent="    "
        )
        pydict = response.json()
        print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
        _handle_aviatrix_api_response_from_create_access_account(response=response)
        data = dict()  # MMM to be implemented after feedback
        print(keyword_for_log + 'ENDED: Aviatrix Action: "CreateAccessAccount"\n\n')
    elif 'DeleteAviatrixAccessAccount'.upper() == aviatrix_action.upper():
        print(keyword_for_log + 'START: Aviatrix Action: "DeleteAviatrixAccessAccount"')
        access_account_name   = event['ResourceProperties']['AccessAccountNameParam']

        response = delete_access_account(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            access_account_name=access_account_name,
            keyword_for_log=keyword_for_log,
            indent="    "
        )
        pydict = response.json()
        print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
        _handle_aviatrix_api_response_from_delete_access_account(response=response)
        data = dict()  # MMM to be implemented after feedback
        print(keyword_for_log + 'ENDED: Aviatrix Action: "DeleteAviatrixAccessAccount"\n\n')
    elif 'BuildNewRouteDomain'.upper() == aviatrix_action.upper():
        print(keyword_for_log + 'START: Aviatrix Action: "BuildNewRouteDomain"')
        tgw_region_name                  = event['ResourceProperties']['TgwRegionNameParam']
        aws_tgw_name                     = event['ResourceProperties']['TgwNameParam']
        new_route_domain_name            = event['ResourceProperties']['NewRouteDomainNameParam']
        is_firewall_domain               = event['ResourceProperties']['IsFirewallDomainParam']
        list_of_route_domains_to_connect = event['ResourceProperties']['ListOfRouteDomainsToConnectParam']
        list_of_route_domains_to_connect = parse_route_domains_from_1_string_into_list_of_strings(
            raw_route_domains_string=list_of_route_domains_to_connect
        )

        responses = build_new_route_domain(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            tgw_region_name=tgw_region_name,
            aws_tgw_name=aws_tgw_name,
            new_route_domain_name=new_route_domain_name,
            is_firewall_domain=is_firewall_domain,
            list_of_route_domains_to_connect=list_of_route_domains_to_connect,
            keyword_for_log=keyword_for_log,
            indent="    "
        )
        # API-responses handling has already been done within the build_new_route_domain()
        data = dict()  # MMM to be implemented after feedback
        print(keyword_for_log + 'ENDED: Aviatrix Action: "BuildNewRouteDomain"\n\n')
    elif 'TeardownRouteDomain'.upper() == aviatrix_action.upper():
        print(keyword_for_log + 'START: Aviatrix Action: "TeardownRouteDomain"')
        aws_tgw_name                     = event['ResourceProperties']['TgwNameParam']
        source_route_domain_name   = event['ResourceProperties']['SourceRouteDomainNameParam']
        list_of_route_domains_to_disconnect = event['ResourceProperties']['ListOfRouteDomainsToDisconnect']
        list_of_route_domains_to_disconnect = parse_route_domains_from_1_string_into_list_of_strings(
            raw_route_domains_string=list_of_route_domains_to_disconnect
        )

        responses = teardown_route_domain(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            aws_tgw_name=aws_tgw_name,
            source_route_domain_name=source_route_domain_name,
            list_of_route_domains_to_disconnect=list_of_route_domains_to_disconnect,
            keyword_for_log=keyword_for_log,
            indent="    "
        )
        # API-responses handling has already been done within the teardown_route_domain()
        data = dict()  # MMM to be implemented after feedback
        print(keyword_for_log + 'ENDED: Aviatrix Action: "TeardownRouteDomain"\n\n')
    else:
        print('Error: Invalid Aviatrix Action: ' + aviatrix_action.upper())
        raise AviatrixException(message='Error: Invalid Aviatrix Action: ' + aviatrix_action.upper())
    # END if-else


    # At this point, all lambda code statements are executed successfully with no errors.
    print(keyword_for_log + "Successfully completed lambda function with no errors!\n\n")


    return data
# END def _lambda_handler()


def print_lambda_event(
    event,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    for key in event:
        print(str(key) + " --- " + str(event[key]))

    for key in event["ResourceProperties"]:
        if 'password' in key.lower():  # Don't print password or any sensitive data
            continue
        elif 'passcode' in key.lower():  # Don't print password or any sensitive data
            continue
        elif 'secret' in key.lower():  # Don't print password or any sensitive data
            continue
        else:
            print(indent + keyword_for_log + key + "  ::  " + str(event["ResourceProperties"][key]))


    '''  MMM
    print(indent + keyword_for_log + "PrefixStringParam                    --> " +
          event["ResourceProperties"]["PrefixStringParam"])
    print(indent + keyword_for_log + "KeywordForCloudWatchLogParam         --> " +
          event["ResourceProperties"]["KeywordForCloudWatchLogParam"])
    print(indent + keyword_for_log + "DelimiterForCloudWatchLogParam       --> " +
        event["ResourceProperties"]["DelimiterForCloudWatchLogParam"])
    print(indent + keyword_for_log + "AviatrixControllerHostnameParam              --> " +
        event["ResourceProperties"]["AviatrixControllerHostnameParam"])
    print(indent + keyword_for_log + "AviatrixApiVersionParam              --> " +
        event["ResourceProperties"]["AviatrixApiVersionParam"])
    print(indent + keyword_for_log + "AviatrixApiRouteParam                --> " +
        event["ResourceProperties"]["AviatrixApiRouteParam"])
    print(indent + keyword_for_log + "ControllerVersionParam               --> " +
        event["ResourceProperties"]["ControllerVersionParam"])


    print(indent + keyword_for_log + "ControllerAccessAccountNameParam     --> " +
        event["ResourceProperties"]["ControllerAccessAccountNameParam"])
    # print(indent + keyword_for_log + "ControllerAccessAccountPasswordParam --> " +
    #     event["ResourceProperties"]["ControllerAccessAccountPasswordParam"])
    # print(indent + keyword_for_log + "ControllerAccessAccountEmailParam    --> " +
    #     event["ResourceProperties"]["ControllerAccessAccountEmailParam"])
    '''
# END def print_lambda_event()


def _build_response_for_terraform(
    event=None,  # AWS Lambda "event"
    status=False,  # Valid values: True, False (bool)
    # message="Successfully finished Initial Setup for Aviatrix Controller: 255.255.255.255",
    message="Failed Initial Setup for Aviatrix Controller: 255.255.255.255 due to: xxx",
    keyword_for_log="avx-lambda-function---",
    indent=""
        ):
    print(indent + keyword_for_log + "START: _build_response_for_terraform()")
    response_for_tf = {
        'status': status,  # (Required)
        'message': message  # (Required)
    }
    print(str(json.dumps(obj=response_for_tf, indent=4)))
    print(indent + keyword_for_log + "ENDED: _build_response_for_terraform()\n\n")
    return response_for_tf
# END def _build_response_for_terraform()


def _build_response_for_generic_lambda_invoker(
    event=None,  # AWS Lambda "event"
    status=False,  # Valid values: True, False (bool)
    # message="Succeesfully finished Initial Setup for Aviatrix Controller: 255.255.255.255",
    message="Failed Initial Setup for Aviatrix Controller: 255.255.255.255 due to: xxx",
    keyword_for_log="avx-lambda-function---",
    indent=""
        ):
    print(indent + keyword_for_log + "START: _build_response_for_generic_lambda_invoker()")
    response_for_generic_lambda_invoker = {
        'status': status,  # (Required)
        'message': message  # (Required)
    }
    print(str(json.dumps(obj=response_for_generic_lambda_invoker, indent=4)))
    print(indent + keyword_for_log + "ENDED: _build_response_for_generic_lambda_invoker()\n\n")
    return response_for_generic_lambda_invoker
# END def _build_response_for_generic_lambda_invoker()


def _build_response_for_cloudformation_stack(
    event=dict(),
    context=None,
    status="FAILED or SUCCESS",
    reason="Failed because...",
    data=dict(),
    keyword_for_log="avx-lambda-function---",
    indent=""
        ):
    """
        Reference:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-responses.html
    """
    print(indent + keyword_for_log + "START: _build_response_for_cloudformation_stack()")

    ### Fill out required fields for return response for cloudformation
    response_for_cf = dict()
    response_for_cf['Status'] = status
    response_for_cf['StackId'] = event["StackId"]
    response_for_cf['RequestId'] = event["RequestId"]
    response_for_cf['LogicalResourceId'] = event["LogicalResourceId"]
    response_for_cf['PhysicalResourceId'] = context.log_stream_name


    if 'SUCCESS' is status.upper():
        # response_for_cf['NoEcho'] = False  # Optional
        response_for_cf['Data'] = data
    elif 'FAILED' is status.upper():
        response_for_cf['Reason'] = reason


    print(str(json.dumps(obj=response_for_cf, indent=4)))
    print(indent + keyword_for_log + "ENDED: _build_response_for_cloudformation_stack()\n\n")
    return response_for_cf
# END def _build_response_for_cloudformation_stack


def wait_until_controller_api_server_is_ready(
    ucc_public_ip="123.123.123.123",
    api_version="v1",
    api_route="api/",
    total_wait_time=300,  # second(s)
    interval_wait_time=10,  # second(s)
    keyword_for_log="avx-lambda-function---",
    indent=""
        ):
    api_endpoint_url = "https://" + ucc_public_ip + "/" + api_version + "/" + api_route
    payload = {
        "action": "is_server_ready"  # The value here does not matter
    }
    remaining_wait_time = total_wait_time

    ''' Variable Description: (time_spent_for_requests_lib_timeout)
    Description: 
        * This value represents how many seconds for "requests" lib to timeout by default. 
    Detail: 
        * The value 20 seconds is actually a rough number which is not  
        * If there is a connection error and causing timeout when 
          invoking--> requests.get(xxx), it takes about 20 seconds for requests.get(xxx) to throw timeout exception.
        * When calculating the remaining wait time, this value is considered.
    '''
    time_spent_for_requests_lib_timeout = 20
    response_status_code = -1
    last_err_msg = ""
    while remaining_wait_time > 0:
        try:
            response = requests.get(
                url=api_endpoint_url,
                params=payload,
                verify=False
            )
            if response is not None:
                # pydict = response.json()
                # print(str(pydict))  # test
                response_status_code = response.status_code

                ### IF 200, return True
                if 200 == response_status_code:
                    print(
                        indent +
                        keyword_for_log +
                        "Server status code: " +
                        str(response_status_code) + ". "
                        "API Server is ready!"
                    )
                    return True
            # END outer if

        except Exception as e:
            print(indent + keyword_for_log + "Aviatrix Controller " + api_endpoint_url + " is still not available")
            last_err_msg = str(e)
            pass  # Purposely ignore the exception by displaying the error message only since it's retry
        # END try-except

        if 404 == response_status_code:
            err_msg = "Error: Aviatrix Controller returns error code: 404 for " + api_endpoint_url + \
                      " Please check if the API version or API endpoint route is correct."
            raise AviatrixException(
                message=err_msg,
            )
        # END if

        # At this point, server status code is NOT 200, or some other error has occurred. Retrying...

        remaining_wait_time = remaining_wait_time - interval_wait_time - time_spent_for_requests_lib_timeout
        print(indent + keyword_for_log + "Remaining wait time: " + str(remaining_wait_time) + " second(s)")
        if remaining_wait_time > 0:
            # print(indent + keyword_for_log + "Wait for " + str(interval_wait_time) + " second(s) before next retry...")
            time.sleep(interval_wait_time)
    # END while

    # TIME IS UP!! At this point, server is still not available or not reachable
    err_msg = "Aviatrix Controller " + api_endpoint_url + " is still not available after " + \
              str(total_wait_time) + " seconds retry. " + \
              "Server status code is: " + str(response_status_code) + ". " + \
              "The last retry message (if any) is: " + last_err_msg
    raise AviatrixException(
        message=err_msg,
    )
# END wait_until_controller_api_server_is_ready()


def _send_aviatrix_api(
    api_endpoint_url="https://123.123.123.123/v1/api",
    request_method="POST",
    payload=dict(),
    retry_count=5,
    keyword_for_log="avx-lambda-function---",
    indent=""
        ):
    response = None
    responses = list()
    request_type = request_method.upper()
    response_status_code = -1

    for i in range(retry_count):
        try:
            if request_type == "GET":
                response = requests.get(url=api_endpoint_url, params=payload, verify=False)
                response_status_code = response.status_code
            elif request_type == "POST":
                response = requests.post(url=api_endpoint_url, data=payload, verify=False)
                response_status_code = response.status_code
            else:
                lambda_failure_reason = "ERROR: Bad HTTPS request type: " + request_method
                print(keyword_for_log + lambda_failure_reason)
                return lambda_failure_reason
            # END if-else

            responses.append(response)  # For error message/debugging purposes
        except requests.exceptions.ConnectionError as e:
            print(indent + keyword_for_log + "WARNING: Oops, it looks like the server is not responding...")
            responses.append(str(e))  # For error message/debugging purposes
            # hopefully it keeps retrying...

        except Exception as e:
            traceback_msg = traceback.format_exc()
            print(indent + keyword_for_log + "Oops! Aviatrix Lambda caught an exception! The traceback message is: ")
            print(traceback_msg)
            lambda_failure_reason = "Oops! Aviatrix Lambda caught an exception! The traceback message is: \n" + str(traceback_msg)
            print(keyword_for_log + lambda_failure_reason)
            responses.append(str(traceback_msg))  # For error message/debugging purposes
        # END try-except

        finally:
            if 200 == response_status_code:  # Successfully send HTTP request to controller Apache2 server
                    return response
            elif 404 == response_status_code:
                lambda_failure_reason = "ERROR: Oops, 404 Not Found. Please check your URL or route path..."
                print(indent + keyword_for_log + lambda_failure_reason)
            # END IF-ELSE: Checking HTTP response code

            '''
            IF the code flow ends up here, it means the current HTTP request have some issue 
            (exception occurs or HTTP response code is NOT 200)
            '''

            '''
            retry     --> 5
            wait_time -->    1, 2, 4, 8 (no 16 because when i == , there will be NO iteration)
            i         --> 0, 1, 2, 3, 4
            '''
            if i+1 < retry_count:
                print(indent + keyword_for_log + "START: Wait until retry")
                print(indent + keyword_for_log + "    i == " + str(i))
                wait_time_before_retry = pow(2, i)
                print(
                    indent + keyword_for_log + "    Wait for: " + str(wait_time_before_retry) +
                    " second(s) until next retry"
                )
                time.sleep(wait_time_before_retry)
                print(indent + keyword_for_log + "ENDED: Wait until retry  \n\n")
                # continue next iteration
            else:
                lambda_failure_reason = 'ERROR: Failed to invoke Aviatrix API. Max retry exceeded. ' + \
                                        'The following includes all retry responses: ' + \
                                        str(responses)
                raise AviatrixException(
                    message=lambda_failure_reason,
                )
        # END try-except-finally
    # END for

    return response  # IF the code flow ends up here, the response might have some issues
# END def _send_aviatrix_api()


def login(
    api_endpoint_url="https://123.123.123.123/v1/api",
    username="admin",
    password="**********",
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    request_method = "POST"
    data = {
        "action": "login",
        "username": username,
        "password": password
    }
    payload_with_hidden_password = dict(data)
    payload_with_hidden_password["password"] = "************"

    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(
        indent + keyword_for_log + "Request payload     : \n" +
        str(json.dumps(obj=payload_with_hidden_password, indent=4))
    )

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=data,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )
    return response
# END def set_admin_email()


def verify_aviatrix_api_response_login(response=None, keyword_for_log="avx-lambda-function---", indent="    "):
    py_dict = response.json()
    print(indent + keyword_for_log + "Aviatrix API response --> " + str(py_dict))

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        err_msg = "Fail to login Aviatrix controller. " \
                  "Expected HTTP response code is 200. However the actual " \
                  "response code is: " + str(response_code)
        raise AviatrixException(
            message=err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is not True:
        err_msg = "Fail to login Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "authorized successfully"
    if (expected_string in api_return_msg) is False:
        err_msg = "Fail to login Aviatrix controller. API actual return message is: " + \
                  str(py_dict) + \
                  " The string we expect to find is: " + \
                  expected_string

        raise AviatrixException(
            message=err_msg,
        )
    # END if
# END def verify_aviatrix_api_response_login()


def is_controller_initialized(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):

    request_method = "GET"
    data = {
        "action": "initial_setup",
        "subaction": "check",
        "CID": CID
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=data, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=data,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    py_dict = response.json()
    print(indent + keyword_for_log + "Aviatrix API response --> " + str(py_dict))
    if py_dict["return"] is False and py_dict["reason"] == "not run":
        return False  # Controller has NOT been initialized
    # END if

    return True  # Controller has ALREADY been initialized
# END def is_controller_initialized()


def get_controller_version(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    """    "list_version_info" API is supported by all controller versions since 2.7  """
    request_method = "GET"
    params = {
        "action": "list_version_info",
        "CID": CID
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=params, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=params,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    ##### Get controller info
    py_dict = response.json()
    # Commented out on purpose to avoid confusion since 2.6 doesn't support "list_version_info"
    # print(keyword_for_log + "Aviatrix API response --> " + str(py_dict))
    ### IF controller doesn't find the API "list_version_info", it means controller version is 2.6 or older
    if py_dict["return"] is False and py_dict["reason"] == "valid action required":
        # print(indent + keyword_for_log + 'Controller version does not support the API, "list_version_info". '
        #                         'Controller version is 2.6 or earlier release.')
        return "2.6"

    ### IF "list_version_info" API call succeeded, then start parsing and trimming the strings to get the version ONLY
    elif py_dict["return"] is True:
        controller_version = _parse_list_version_info_API_to_get_controller_version(
            response=response,
            with_subversion=False,
            keyword_for_log="avx-lambda-function---",
            indent="    "
        )
        return controller_version
    # END if-else

    avx_err_msg = 'Error: Not able to get controller version.'
    raise AviatrixException(
        message=avx_err_msg,
    )
# END def get_controller_version()


def _parse_list_version_info_API_to_get_controller_version(
    response=None,
    with_subversion=False,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    """
    This function will extract the version in the digit part, like ...
    from
    "UserConnect-3.4.105"
    to
    "3.4.105"

    This API is supported in 2.7 or later release
    """
    pydict = response.json()
    current_version_string = ""
    if pydict["return"] is True:
        current_version_string = pydict["results"]["current_version"]
    else:
        print(indent + keyword_for_log + "Fail to get Aviatrix controller version")
        return None  # Fail to get Aviatrix controller version

    # Trim the version string
    if "UserConnect-" in current_version_string:
        current_version_string = current_version_string[12:]  # Get rid of the string "UserConnect-"

    if with_subversion:
        return current_version_string
    else:
        index_of_last_dot = current_version_string.rfind('.')
        current_version_string = current_version_string[0:index_of_last_dot]
        return current_version_string

# END _parse_list_version_info_API_to_get_controller_version


def create_access_account(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    controller_version="4.0",
    account_name="my-aws-role-based",
    account_password="**********",
    account_email="test@aviatrix.com",
    cloud_type="1",
    aws_account_number="123456789012",
    is_iam_role_based="true",
    app_role_arn="arn:aws:iam::123456789012:role/aviatrix-role-app",
    ec2_role_arn="arn:aws:iam::123456789012:role/aviatrix-role-ec2",
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    controller_version = eval(controller_version)
    request_method = "POST"

    if controller_version <= 2.6:
        data = {
            "action": "xxxxx",
            "CID": CID,
            "account_name": account_name,
            "account_password": account_password,
            "account_email": account_email,
            "cloud_type": cloud_type,
            "aws_account_number": aws_account_number,
            "aws_iam": is_iam_role_based,
            "aws_role_arn": app_role_arn,
            "aws_role_ec2": ec2_role_arn
        }
    else:  # The API, "edit_account_user" is supported in 2.7 or later release
        data = {
            "action": "setup_account_profile",
            "CID": CID,
            "account_name": account_name,
            "account_password": account_password,
            "account_email": account_email,
            "cloud_type": cloud_type,
            "aws_account_number": aws_account_number,
            "aws_iam": is_iam_role_based,
            "aws_role_arn": app_role_arn,
            "aws_role_ec2": ec2_role_arn
        }
    # END determine API depends on controller version

    payload_with_hidden_password = dict(data)
    payload_with_hidden_password["account_password"] = "************"

    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(
        indent + keyword_for_log + "Request payload     : \n" +
        str(json.dumps(obj=payload_with_hidden_password, indent=4))
    )

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=data,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )
    return response
# END def create_access_account()


def _handle_aviatrix_api_response_from_create_access_account(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "An email confirmation has been sent to"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_create_access_account()


def delete_access_account(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    access_account_name="my-aws-role-based",
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    request_method = "POST"
    data = {
        "action": "delete_account_profile",
        "CID": CID,
        "account_name": access_account_name
    }

    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(
        indent + keyword_for_log + "Request payload     : \n" +
        str(json.dumps(obj=data, indent=4))
    )

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=data,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )
    return response
# END def delete_access_account()


def _handle_aviatrix_api_response_from_delete_access_account(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to delete access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "deleted, and an email notification has been sent to"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on  Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_delete_access_account()


def create_aws_tgw(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    access_account_name='my-avx-iam-role-basd-access-account-009',
    region_name='us-east-1',
    aws_tgw_name='my-1st-tgw',
    aws_side_AS_numeber='64512',
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    request_method = "POST"
    payload = {
        "action": "add_aws_tgw",
        "CID": CID,
        "account_name": access_account_name,
        "region": region_name,
        "tgw_name": aws_tgw_name,
        "aws_side_asn": aws_side_AS_numeber
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=payload, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=payload,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    return response
# END def create_aws_tgw()


def _handle_aviatrix_api_response_from_create_aws_tgw(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "Successfully created TGW"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_create_aws_tgw()


def delete_aws_tgw(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    aws_tgw_name='my-1st-tgw',
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    request_method = "POST"
    payload = {
        "action": "delete_aws_tgw",
        "CID": CID,
        "tgw_name": aws_tgw_name
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=payload, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=payload,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    return response
# END def delete_aws_tgw()


def _handle_aviatrix_api_response_from_delete_aws_tgw(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "Successfully deleted TGW"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_delete_aws_tgw()


def parse_route_domains_from_1_string_into_list_of_strings(
    raw_route_domains_string="Default_Domain, Aviatrix_Edge_Domain, Shared_Service_Domain"
        ):
    """
    + This function takes 1 string represents a list of Aviatrix-Route-Domains and returns a list of strings.
    + This function will trims the white-space-characters for each string element (Route-Domain)
    :param route_domains_string:
        Description: This is a single string, which contains a list of Aviatrix-Route-Domains, separated by comma ','
        Required: YES
        Type: String
        Default Value: None
        Example Value(s): "Default_Domain, Aviatrix_Edge_Domain, Shared_Service_Domain"
    :return:
        Description: This is a single string, which contains a list of Aviatrix-Route-Domains, separated by comma ','
        Type: list
        Example Value(s): list("Default_Domain", "Aviatrix_Edge_Domain", "Shared_Service_Domain")
    """
    final_route_domain_list = list()
    raw_route_domains = raw_route_domains_string.split(sep=',')  # Get a list of strings (each string represents an Aviatrix-Route-Domain) using comma ',' to split the original string

    for route_domain in raw_route_domains:
        route_domain = route_domain.rstrip()  # Remove the trailing whitespace characters
        route_domain = route_domain.lstrip()  # Remove the trailing whitespace characters
        final_route_domain_list.append(route_domain)
    # END for

    return final_route_domain_list
# END def parse_route_domains_from_1_string_into_list_of_strings


def create_route_domain(
            api_endpoint_url="https://123.123.123.123/v1/api",
            CID="ABCD1234",
            tgw_region_name="us-east-1",
            aws_tgw_name="my-aws-tgw-009",
            new_route_domain_name="my-new-avx-security-domain",
            is_firewall_domain="false",
            keyword_for_log="avx-lambda-function---",
            indent="    "
            ):
    """
            + This function is actually leveraging 2 Aviatrix APIs 1) add_route_domain 2) add_connection_between_route_domains.
            +  Aviatrix API, "add_connection_between_route_domains" actually can only add/connect 1 domain at a time.
                However, the parameter of this function, "list_of_route_domains_to_connect" is a list of array, which allows this function can add/connect multiple domains

            :param api_endpoint_url:
                Description: URL of Aviatrix controller API endpoint
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "https://123.123.123.123/v1/api"
            :param CID:
                Description: Aviatrix API session/token
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "YQVGabn8VDyDf27Zjv5s"
            :param access_account_name:
            :param tgw_region_name:
            :param new_security_route_domain_name:
            :param is_firewall_domain:
                Description: Indicates whether this new domain is a firewall domain or not
                Required: No
                Type: String
                Default Value: "false"
                Example Value(s): "true"  ||  "false"
            :param list_of_route_domains_to_connect:
                Description: The list of domains that for the new security-route-domain to connect
                Required: No
                Type: list of Strings
                Default Value: None
                Example Value(s): ["Default_Domain", "Shared_Service_Domain"]
            :param keyword_for_log:
            :param indent:
            :return: response object from "requests" library/package
    """
    request_method = "POST"
    payload = {
        "action": "add_route_domain",
        "CID": CID,
        "region": tgw_region_name,
        "tgw_name": aws_tgw_name,
        "route_domain_name": new_route_domain_name,
        "firewall_domain": is_firewall_domain
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=payload, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=payload,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    return response
# END def create_route_domain()


def _handle_aviatrix_api_response_from_create_route_domain(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "Successfully added Route Domain"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_create_route_domain()


def delete_route_domain(
        api_endpoint_url="https://123.123.123.123/v1/api",
        CID="ABCD1234",
        aws_tgw_name="my-aws-tgw-009",
        route_domain_name="my-avx-route-domain",
        keyword_for_log="avx-lambda-function---",
        indent="    "
            ):
    """
            + This function is actually leveraging 2 Aviatrix APIs 1) add_route_domain 2) add_connection_between_route_domains.
            +  Aviatrix API, "add_connection_between_route_domains" actually can only add/connect 1 domain at a time.
                However, the parameter of this function, "list_of_route_domains_to_connect" is a list of array, which allows this function can add/connect multiple domains

            :param api_endpoint_url:
                Description: URL of Aviatrix controller API endpoint
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "https://123.123.123.123/v1/api"
            :param CID:
                Description: Aviatrix API session/token
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "YQVGabn8VDyDf27Zjv5s"
            :param access_account_name:
            :param tgw_region_name:
            :param new_security_route_domain_name:
            :param is_firewall_domain:
                Description: Indicates whether this new domain is a firewall domain or not
                Required: No
                Type: String
                Default Value: "false"
                Example Value(s): "true"  ||  "false"
            :param list_of_route_domains_to_connect:
                Description: The list of domains that for the new security-route-domain to connect
                Required: No
                Type: list of Strings
                Default Value: None
                Example Value(s): ["Default_Domain", "Shared_Service_Domain"]
            :param keyword_for_log:
            :param indent:
            :return: response object from "requests" library/package
    """
    request_method = "POST"
    payload = {
        "action": "delete_route_domain",
        "CID": CID,
        "tgw_name": aws_tgw_name,
        "route_domain_name": route_domain_name
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=payload, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=payload,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    return response
# END def delete_route_domain()


def _handle_aviatrix_api_response_from_delete_route_domain(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "Successfully deleted Route Domain"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_delete_route_domain()


def connect_route_domain(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    aws_tgw_name="my-tgw-009",
    source_route_domain_name="My_New_Security_Route_Domain_009",
    destination_route_domain_name="Default_Domain",
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    request_method = "POST"
    payload = {
        "action": "add_connection_between_route_domains",
        "CID": CID,
        "tgw_name": aws_tgw_name,
        "source_route_domain_name": source_route_domain_name,
        "destination_route_domain_name": destination_route_domain_name
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=payload, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=payload,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    return response
# END def connect_route_domain()


def _handle_aviatrix_api_response_from_connect_route_domain(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "Successfully connected Route Domain"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_connect_route_domain()


def disconnect_route_domain(
            api_endpoint_url="https://123.123.123.123/v1/api",
            CID="ABCD1234",
            aws_tgw_name="my-aws-tgw-009",
            source_route_domain_name="my-avx-route-domain",
            destination_route_domain_name="Default_Domain",
            keyword_for_log="avx-lambda-function---",
            indent="    "
            ):
    """
            + This function is actually leveraging 2 Aviatrix APIs 1) add_route_domain 2) add_connection_between_route_domains.
            +  Aviatrix API, "add_connection_between_route_domains" actually can only add/connect 1 domain at a time.
                However, the parameter of this function, "list_of_route_domains_to_connect" is a list of array, which allows this function can add/connect multiple domains

            :param api_endpoint_url:
                Description: URL of Aviatrix controller API endpoint
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "https://123.123.123.123/v1/api"
            :param CID:
                Description: Aviatrix API session/token
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "YQVGabn8VDyDf27Zjv5s"
            :param access_account_name:
            :param tgw_region_name:
            :param new_security_route_domain_name:
            :param is_firewall_domain:
                Description: Indicates whether this new domain is a firewall domain or not
                Required: No
                Type: String
                Default Value: "false"
                Example Value(s): "true"  ||  "false"
            :param list_of_route_domains_to_connect:
                Description: The list of domains that for the new security-route-domain to connect
                Required: No
                Type: list of Strings
                Default Value: None
                Example Value(s): ["Default_Domain", "Shared_Service_Domain"]
            :param keyword_for_log:
            :param indent:
            :return: response object from "requests" library/package
    """
    request_method = "POST"
    payload = {
        "action": "delete_connection_between_route_domains",
        "CID": CID,
        "tgw_name": aws_tgw_name,
        "source_route_domain_name": source_route_domain_name,
        "destination_route_domain_name": destination_route_domain_name
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=payload, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=payload,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    return response
# END def disconnect_route_domain()


def _handle_aviatrix_api_response_from_disconnect_route_domain(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "Successfully disconnected Route Domain"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_disconnect_route_domain()


def build_new_route_domain(
        api_endpoint_url="https://123.123.123.123/v1/api",
        CID="ABCD1234",
        tgw_region_name="us-east-1",
        aws_tgw_name="my-aws-tgw-009",
        new_route_domain_name="my-new-avx-security-route-domain",
        is_firewall_domain="false",
        list_of_route_domains_to_connect=["Default_Domain", "Shared_Service_Domain"],
        keyword_for_log="avx-lambda-function---",
        indent="    "
            ):
    """
            + This function is actually leveraging 2 Aviatrix APIs 1) add_route_domain 2) add_connection_between_route_domains.
            +  Aviatrix API, "add_connection_between_route_domains" actually can only add/connect 1 domain at a time.
                However, the parameter of this function, "list_of_route_domains_to_connect" is a list of array, which allows this function can add/connect multiple domains

            :param api_endpoint_url:
                Description: URL of Aviatrix controller API endpoint
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "https://123.123.123.123/v1/api"
            :param CID:
                Description: Aviatrix API session/token
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "YQVGabn8VDyDf27Zjv5s"
            :param access_account_name:
            :param tgw_region_name:
            :param new_route_domain_name:
            :param is_firewall_domain:
                Description: Indicates whether this new domain is a firewall domain or not
                Required: No
                Type: String
                Default Value: "false"
                Example Value(s): "true"  ||  "false"
            :param list_of_route_domains_to_connect:
                Description: The list of domains that for the new security-route-domain to connect
                Required: No
                Type: list of Strings
                Default Value: None
                Example Value(s): ["Default_Domain", "Shared_Service_Domain"]
            :param keyword_for_log:
            :param indent:
            :return: response object from "requests" library/package
    """
    responses = list()

    response = create_route_domain(
        api_endpoint_url=api_endpoint_url,
        CID=CID,
        tgw_region_name=tgw_region_name,
        aws_tgw_name=aws_tgw_name,
        new_route_domain_name=new_route_domain_name,
        is_firewall_domain=is_firewall_domain,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )
    responses.append(response)
    pydict = response.json()
    print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
    _handle_aviatrix_api_response_from_create_route_domain(response=response)


    for route_domains_to_connect in list_of_route_domains_to_connect:
        response = connect_route_domain(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            aws_tgw_name=aws_tgw_name,
            source_route_domain_name=new_route_domain_name,
            destination_route_domain_name=route_domains_to_connect,
            keyword_for_log=keyword_for_log,
            indent=indent + "    "
        )
        responses.append(response)
        pydict = response.json()
        print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
        _handle_aviatrix_api_response_from_connect_route_domain(response=response)
    # END for

    return responses
# END def build_new_route_domain()



def teardown_route_domain(
        api_endpoint_url="https://123.123.123.123/v1/api",
        CID="ABCD1234",
        tgw_region_name="us-east-1",
        aws_tgw_name="my-aws-tgw-009",
        source_route_domain_name="my-new-avx-security-route-domain",
        list_of_route_domains_to_disconnect=["Default_Domain", "Shared_Service_Domain"],
        keyword_for_log="avx-lambda-function---",
        indent="    "
            ):
    """
            + This function is actually leveraging 2 Aviatrix APIs 1) add_route_domain 2) add_connection_between_route_domains.
            +  Aviatrix API, "add_connection_between_route_domains" actually can only add/connect 1 domain at a time.
                However, the parameter of this function, "list_of_route_domains_to_connect" is a list of array, which allows this function can add/connect multiple domains

            :param api_endpoint_url:
                Description: URL of Aviatrix controller API endpoint
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "https://123.123.123.123/v1/api"
            :param CID:
                Description: Aviatrix API session/token
                Required: YES
                Type: String
                Default Value: None
                Example Value(s): "YQVGabn8VDyDf27Zjv5s"
            :param access_account_name:
            :param tgw_region_name:
            :param new_route_domain_name:
            :param is_firewall_domain:
                Description: Indicates whether this new domain is a firewall domain or not
                Required: No
                Type: String
                Default Value: "false"
                Example Value(s): "true"  ||  "false"
            :param list_of_route_domains_to_connect:
                Description: The list of domains that for the new security-route-domain to connect
                Required: No
                Type: list of Strings
                Default Value: None
                Example Value(s): ["Default_Domain", "Shared_Service_Domain"]
            :param keyword_for_log:
            :param indent:
            :return: response object from "requests" library/package
    """
    responses = list()

    for destination_route_domain_name in list_of_route_domains_to_disconnect:
        response = disconnect_route_domain(
            api_endpoint_url=api_endpoint_url,
            CID=CID,
            aws_tgw_name=aws_tgw_name,
            source_route_domain_name=source_route_domain_name,
            destination_route_domain_name=destination_route_domain_name,
            keyword_for_log=keyword_for_log,
            indent=indent + "    "
        )
        responses.append(response)
        pydict = response.json()
        print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
        # _handle_aviatrix_api_response_from_disconnect_route_domain(response=response)  # comment this line out on purpose because invoking delete_route_domain() will also disconnect all route-domains
    # END for

    response = delete_route_domain(
        api_endpoint_url=api_endpoint_url,
        CID=CID,
        aws_tgw_name=aws_tgw_name,
        route_domain_name=source_route_domain_name,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )
    responses.append(response)
    pydict = response.json()
    print(keyword_for_log + '    Aviatrix API Response: ' + str(pydict))
    _handle_aviatrix_api_response_from_delete_route_domain(response=response)

    return responses
# END def teardown_route_domain()


def attach_vpc_to_aws_tgw(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    vpc_access_account_name="my-access-account-009",
    vpc_region_name="us-west-1",
    vpc_id="vpc-abc123",
    aws_tgw_name="my-1st-aws-tgw",
    route_domain_name="Default_Domain",
    subnet_list=["subnet-abc123", "subnet-xyz-789"],
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    request_method = "POST"
    payload = {
        "action": "attach_vpc_to_tgw",
        "CID": CID,
        "region": vpc_region_name,
        "vpc_account_name": vpc_access_account_name,
        "vpc_name": vpc_id,
        "tgw_name": aws_tgw_name,
        "route_domain_name": route_domain_name,
        "subnet_list": subnet_list
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=payload, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=payload,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    return response
# END def attach_vpc_to_aws_tgw()


def _handle_aviatrix_api_response_from_attach_vpc_to_aws_tgw(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "Successfully attached"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_attach_vpc_to_aws_tgw()


def detach_vpc_from_aws_tgw(
    api_endpoint_url="https://123.123.123.123/v1/api",
    CID="ABCD1234",
    vpc_id="vpc-abc123",
    aws_tgw_name="my-1st-aws-tgw",
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    request_method = "POST"
    payload = {
        "action": "detach_vpc_from_tgw",
        "CID": CID,
        "vpc_name": vpc_id,
        "tgw_name": aws_tgw_name
    }
    print(indent + keyword_for_log + "API End Point URL   : " + str(api_endpoint_url))
    print(indent + keyword_for_log + "Request Method Type : " + str(request_method))
    print(indent + keyword_for_log + "Request payload     : \n" + str(json.dumps(obj=payload, indent=4)))

    response = _send_aviatrix_api(
        api_endpoint_url=api_endpoint_url,
        request_method=request_method,
        payload=payload,
        keyword_for_log=keyword_for_log,
        indent=indent + "    "
    )

    return response
# END def detach_vpc_from_aws_tgw()


def _handle_aviatrix_api_response_from_detach_vpc_from_aws_tgw(
    response=None,
    keyword_for_log="avx-lambda-function---",
    indent="    "
        ):
    py_dict = response.json()

    ### Verify if HTTP response code is 200
    response_code = response.status_code  # expect to be 200
    if response_code is not 200:
        avx_err_msg = "Fail to create access account on Aviatrix controller. " \
                      "Expected HTTP response code is 200, but the actual " \
                      "response code is: " + str(response_code)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    ### Verify if API response returns True
    api_return_boolean = py_dict["return"]
    if api_return_boolean is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API response is: " + str(py_dict)
        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if

    # At this point, py_dict["return"] is True

    ### Verify if able to find expected string from API response
    api_return_msg = py_dict["results"]
    expected_string = "Successfully deleted"
    if (expected_string in api_return_msg) is False:
        avx_err_msg = "Fail to create access account on Aviatrix controller. API actual return message is: " + \
                      str(py_dict) + \
                      " The string we expect to find is: " + \
                      expected_string

        raise AviatrixException(
            message=avx_err_msg,
        )
    # END if
# END def _handle_aviatrix_api_response_from_detach_vpc_from_aws_tgw()
