Feature: Message processing performance
  As a Clinician
  I want messages to be retrieved fast
  So that I can do my job faster

  Background:
    Given the database is empty

  Scenario Outline: Messages User retrieves messages from the get_messages_by_sender_uuid_or_receiver_uuid endpoint
    Given the database is seeded with <number_messages> messages
    When timing this step
    And the clinician gets messages by <unique_uuid_belongs_to> uuid
    Then it takes less than <seconds_taken_max> seconds to return a list of messages
    And all the messages are retrieved

    Examples:
      | number_messages | seconds_taken_max | unique_uuid_belongs_to |
      | 10000           | 5                 | clinician              |
      | 10000           | 5                 | patient                |
