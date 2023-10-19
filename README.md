# drift-fixer-lambda

Installation Instruction: 
1. In the Firefly Console create Access Key / Secret pair. Copy the Values.
2. Click to create on following CloudFormation Stack (make sure that the stack is created in region N. virginia)
    
    https://us-east-1.console.aws.amazon.com/cloudformation/home?#/stacks/create/review?templateURL=https://infralight-templates-public.s3.amazonaws.com/drift_fixer_template.yml&stackName=Firefly-Drift-Fixer
   
    Use the Access Key / Secret pair created and insert them in the requested variables.
    
    Create the CloudFormation Stack
   
3. Once the CloudFormation Stack is created successfully, copy the value of 'DriftFixerLambdaFunctionUrl' from the Outputs tab.
   
4. Go to Firefly Console and create new webhook integration using 'DriftFixerLambdaFunctionUrl'

5. create new Firefly notification.
   
    5.1 Event Type - Drift
   
    5.2 Destination - the formerly created webhook integration.  
   

After going over the steps, the integration is set, and the drift-fixer lambda is initiated. 
Make sure that the following conditions are applied for drift fix to occur:
* New drift resources should have backend integrated and discovered (the location of the code needs to be discovered in Firefly inventory).  
* New drift resources should be also drifted in the source code. If the source code is aligned with IAC configuration - Only need to apply current code to fix the drift.  