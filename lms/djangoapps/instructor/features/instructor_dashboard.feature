@shard_2
Feature: LMS.Instructor Dashboard
    As an instructor or course staff,
    In order to manage my class
    I want to manage grades, view and update data, and send email.

    ## TODO: COURSE INFO
    ## TODO: MEMBERSHIP
    ## TODO: STUDENT ADMIN

    ## DATA DOWNLOAD
    ### todos when more time can be spent on instructor dashboard
    #Scenario: List enrolled students' profile information
    #Scenario: Download profile information as a CSV
    #Scenario: View the grading configuration
    #Scenario: Download student anonymized IDs as a CSV
    Scenario: Generate & download a grade report
       Given I am "<Role>" for a course
       When I click 'Generate Grade Report'
       Then I see a csv file in the grade reports table
       Examples:
       | Role          |
       | instructor    |
       | staff         |


    ## SEND EMAIL
    Scenario: Send bulk email
        Given I am "<Role>" for a course
        When I send email to "<Recipient>"
        Then Email is sent to "<Recipient>"

        Examples:
        | Role          |  Recipient     |
        | instructor    |  myself        |
        | instructor    |  course staff  |
        | instructor    |  students, staff, and instructors  |
        | staff         |  myself        |
        | staff         |  course staff  |
        | staff         |  students, staff, and instructors  |

