 
REGION = 'us-east-2'
AWS.config.region = 'us-east-2'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-2:7db2b6ac-7f0e-45ec-91a8-2ec05083d96d',
});
	
   // Prepare to call Lambda function
   var lambda = new AWS.Lambda({region: REGION, apiVersion: '2015-03-31'});
   var userParams = {
      Username : 'firstUser',
	  Password: 'Password123'
      InvocationType : 'RequestResponse',
      LogType : 'None'
   };
	
   function login() {
	  //Get user info here
      // Call the Lambda to initiate login
      lambda.invoke(userParams, function(err, data) {
         if (err) {
            prompt(err);
         } else {
            pullResults = JSON.parse(data.Payload);
           //Handle Results
		   if(authToken != null){
			   redirectToListings()
		   } else{
			   //Give Error message
		   }
         }
      });	
   }
	
   function redirectToListings() {
		//redirect to listing page
   }