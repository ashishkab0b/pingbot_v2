
REQUIRED FOR BASIC FUNCTION
- 

MID PRIORITY
- show sent message in ping db
- include link to ping template and to particpant
- prevent double enrollment of a study_pid
- when user changes params of study, change upcoming pings (optionally)
- form validation (esp ping templates)
- switch from using localstorage to store access tokens to using httponly
- check sanitizization all input of javascript.
- put captcha on register and login
- sorting not working on all pages
- add functionality to modify study permissions
- make a route to get a survey link or survey message 
- add testing functionality - add researcher telegram ID to account - send pings to self
- account.js
- forgot your password
    
LOWER PRIORITY

participants capabilities
- change timezone (and then update pings)
- unenroll
- rotate_keys in cron on server


prolific integration
- studies get published at the beginning of the ping block
- post unpublished study draft
- post publish study
- auto approve participants after completion
- one click approve completed participants'
- approval button on pings sheet
- generate spreadsheet with all pings and "approve" column. user uploads spreadsheet again to approve participants.

cloud research integration
- user selects CR integration when making study and adds n participants
- now, when participants enroll in the study, it sends an api request to cloud research to add them to a participant group
- when making ping templates, it creates a cloud research project for each ping template ping
    - including
- db adjustments
    - study
        - cr_integration - boolean
        - cr_n_participants - integer - num participants
    - ping templates
        - survey time (in minutes)
    