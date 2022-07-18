Feature: Sending and receiving messages

    Scenario Outline: Messages are sent between patient and clinician
        When the <sender> sends (<version>) the <receiver> a GENERAL message
        Then the API result body matches that of the sent message
        Examples:
        | sender    | receiver  | version |
        | clinician | patient   | v1      |
        | patient   | clinician | v1      |

    Scenario Outline: Messages are sent between patient and clinician
        When the <sender> sends (<version>) the <receiver> a GENERAL message
        Then the API result body matches that of the sent message
        Examples:
        | sender    | receiver  | version |
        | clinician | patient   | v2      |
        | patient   | clinician | v2      |

    Scenario Outline: Message can retrieved by sender or by recipient
        When the clinician sends (<version>) the patient a DIETARY message
        Then <user> can retrieve the message
        Examples:
            | user                | version |
            | sender              | v1      |
            | receiver            | v1      |
            | sender and receiver | v1      |
            | sender or receiver  | v1      |

    Scenario Outline: Messages are sent between patient and clinician
        When the <sender> sends (<version>) the <receiver> a CLEAR_ALERTS message
        Then the API result body matches that of the sent message
        Examples:
        | sender    | receiver  | version |
        | clinician | patient   | v2      |
