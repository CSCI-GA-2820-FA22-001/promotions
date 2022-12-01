Feature: The promotion service back-end
    As a Promotion admin
    I need a RESTful catalog service
    So that I can keep track of all my promotions

Background:
    Given the following promotions
        | id       | name       | product_id | type        | value   | start_date  | expiration_date | active |
        | 1        | bogo2      | 2          | BOGO        | 1       | 2019-12-15  | 2020-10-10      | True   |
        | 2        | prct3      | 9          | PERCENTAGE  | 50      | 2022-11-29  | 2023-10-12      | False  |
        | 3        | prom8      | 24         | FIXED       | 8       | 2019-11-18  | 2019-11-21      | True   |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotions Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Promo
    When I visit the "Home Page"
    And I set the "ID" to "4"
    And I set the "Name" to "Newpromo"
    And I set the "Type" to "FIXED"
    And I select "False" in the "ACTIVE" dropdown
    And I set the "Product ID" to "7"
    And I set the "value" to "45"
    And I set the "start" to "06-16-2022"
    And I set the "end" to "06-16-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Type" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Newpromo" in the "Name" field
    And I should see "FIXED" in the "Type" field
    And I should see "False" in the "ACTIVE" dropdown
    And I should see "2022-06-16" in the "start" field

Scenario: List all pets
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "bogo2" in the results
    And I should see "prct3" in the results
    And I should not see "prom99" in the results

Scenario: Search for promos by name
    When I visit the "Home Page"
    And I set the "Name" to "prct3"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "prct3" in the results
    And I should not see "bogo2" in the results
    And I should not see "prom8" in the results

'''Scenario: Search for a promo by id
    When I visit the "Home Page"
    And I set the "id" to "1"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "bogo2" in the results
    And I should not see "prct3" in the results
    And I should not see "prom8" in the results
'''

Scenario: Search for Percentage promos
    When I visit the "Home Page"
    And I set the "Type" to "PERCENTAGE"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "prct3" in the results
    And I should not see "bogo2" in the results
    And I should not see "prom8" in the results

Scenario: Update a promo
    When I visit the "Home Page"
    And I set the "Name" to "bogo2"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "bogo2" in the "Name" field
    And I should see "BOGO" in the "Type" field
    When I change "Name" to "ogob2"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "ogob2" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "ogob2" in the results
    And I should not see "bogo2" in the results


Scenario: Delete Promotions
    When I visit the "Home Page"
    And I set the "Id" to "1"
    And I press the "Delete" button
    Then I should see the message "promotion has been Deleted!"
    When I set the "Id" to "2"
    And I press the "Delete" button
    Then I should see the message "promotion has been Deleted!"
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "prom8" in the "Name" field
    And I should not see "bogo2" in the results
    And I should not see "prct3" in the results
