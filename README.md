# Landing Zone Lambda Examples

This project provides AWS Lambda and Cloudformation examples to invoke Aviatrix APIs for TGW operations. 

One use case is to integrate the Lambda handler functions in this repo into your AWS Landing Zone plan, such that TGW VPC attachment can be part of Account Vending machine onboarding. 

Functions provided:

 1. [TGW Creation and Deletion.](https://docs.aviatrix.com/HowTos/tgw_plan.html#create-aws-tgw)
 2. [Aviatrix Access Account creation and deletion. (This can be invoked when a new AWS account is created.)](https://docs.aviatrix.com/HowTos/aviatrix_account.html)
 3. [Security Domain creation and deletion. (This is optional, the function is used to create network segmentation.)](https://docs.aviatrix.com/HowTos/tgw_plan.html#create-a-new-security-domain)
 4. [Security Domain Connection Policy connect and disconnect. (This is optional, the function allows two network segmentation to communicate.](https://docs.aviatrix.com/HowTos/tgw_plan.html#create-a-new-security-domain)
 5. [VPC attachment creation and deletion. (This can be invoked when a new VPC is created.)](https://docs.aviatrix.com/HowTos/tgw_build.html#attach-vpc-to-tgw)


## Prerequisites

+ [Aviatrix Controller, Version 4.3 or above](https://docs.aviatrix.com/StartUpGuides/aviatrix-cloud-controller-startup-guide.html)

+ [Zipped file (which contains the Lambda source file and 3rd party libraries/packages)](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)
    - The zipped file example can be found in the directory  -->>  /s3_bucket_zipped_file/aviatrix_lambda_for_tgw_actions.zip
    - Place the zipped file in any S3 bucket that your Lambda can access.
    
+ Cloudformation template
    - [In the Lambda function definition under the section "Resources", make sure the following fields match your configurations:](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html)
        * (S3Bucket) S3 bucket name
        * (S3Key) zipped file name
        * (Handler) Name of the source file '.' Lambda function name for code entry point


## Steps to Run

+ Login to AWS, and navigate to Cloudformation service
+ Import the Cloudformation template, fill out the required fields then create the Cloudformation stack


## Results

+ After Cloudformation stack successfully/failed to create, you can access AWS CloudWatch service to view the logs of the Lambda function
    - [Refer to AWS Doc](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-functions-logs.html)


