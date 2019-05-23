# Landing Zone Lambda Examples

This project provides AWS Lambda and Cloudformation examples to invoke Aviatrix APIs for TGW operations


## Prerequisites

+ Aviatrix Controller, Version 4.3 or above
    - [Refer to Aviatrix Doc](https://docs.aviatrix.com/StartUpGuides/aviatrix-cloud-controller-startup-guide.html)
+ Zipped file (which contains the Lambda source file and 3rd party libraries/packages)
    - The zipped file example can be found in the directory  -->>  /s3_bucket_zipped_file/aviatrix_lambda_for_tgw_actions.zip
    - Place the zipped file in any S3 bucket that your Lambda can access.
    - [Refer AWS Doc](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)
+ Cloudformation template
    - [In the Lambda function definition under the section "Resources", make sure the following fields match your configurations:]
        * (S3Bucket) S3 bucket name
        * (S3Key) zipped file name
        * (Handler) Name of the source file '.' Lambda function name for code entry point
        * [Refer to AWS Doc](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html)


## Steps to Run

+ Login to AWS, and navigate to Cloudformation service
+ Import the Cloudformation template, fill out the required fields then create the Cloudformation stack


## Results

+ After Cloudformation stack successfully/failed to create, you can access AWS CloudWatch service to view the logs of the Lambda function
    - [Refer to AWS Doc](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-functions-logs.html)


