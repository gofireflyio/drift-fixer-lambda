# drift-fixer-lambda

Installation Instruction: 

1. In the [Firefly Users console](https://app.firefly.ai/users) create Access Key / Secret pair. Copy the Values.

2. Create on following [CloudFormation Stack](https://us-east-1.console.aws.amazon.com/cloudformation/home?#/stacks/create/review?templateURL=https://infralight-templates-public.s3.amazonaws.com/drift_fixer_template.yml&stackName=Firefly-Drift-Fixer) in your AWS account. 

    2.1. The stack creates the Lambda Function itself and it's supporting resources.

    2.2. Use the Access Key / Secret pair created and insert them in the requested variables.

    2.3. Make sure that the stack is created in region N. virginia.


3. Once the CloudFormation Stack is created successfully, open the 'Outputs' tab and copy the value of `DriftFixerLambdaFunctionUrl`.
   
4. In the Firefly [Create Webhook integration page](https://app.firefly.ai/integrations/webhook-integration), create a new Webhook integration using the value copied from `DriftFixerLambdaFunctionUrl`.

5. In the Firefly [Notification page](https://app.firefly.ai/notifications), create a new Firefly notification with the following properties:
   
    5.1. **Event Type** - Drift
   
    5.2. **Destination** - the formerly created Firefly Webhook integration.  
   
At this point, the integration is set and the drift-fixer lambda is initiated. 
Make sure that the following conditions are applied for drift fix to occur:
* New drift resources should have a backend code source integrated and discovered (the location of the code needs to be discovered in Firefly inventory).  
* New drift resources should be also drifted in the source code. If the source code is aligned with IAC configuration - The drift is already fixed in the current code and only needs to be applied.