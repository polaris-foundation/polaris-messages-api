Feature: Message and callback management

    Scenario: Patient sends callback request
        Given the patient sends (v1) the clinician a CALLBACK message
        And clinician can see the message in the list of active callbacks for patients
        And the clinician can see the message in the list of active messages
        When the clinician confirms the message
        Then clinician can not see the message in the list of active callbacks for patients
        But the clinician can see the message in the list of active messages        

    Scenario: Clinician sends general message, patient confirms
        Given the clinician sends (v1) the patient a GENERAL message
        And the patient can see the message in the list of active messages
        When the patient confirms the message
        Then the patient can not see the message in the list of active messages        
        But the system can see the message in the list of received messages
        And the patient can see the message in the list of received messages

    Scenario: If the user type does not match the message cannot be seen
        Given the clinician sends (v1) the bad_user_type a GENERAL message
        And the system can see the message in the list of received messages
        Then the patient can not see the message in the list of received messages
        
