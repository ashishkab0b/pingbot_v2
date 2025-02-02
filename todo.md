
HIGH PRIORITY
- check if participant blocked bot and record in DB
- add "limit" parameter to url for viewing data tables
- sorting not working on all pages
- updating functionality (e.g. pings etc)
    - when user changes params of study, change upcoming pings (optionally)
- make page so that when they open a survey for a second time they are alerted

MID PRIORITY
- show sent message in ping db
- include link to ping template and to particpant with ping
- prevent double enrollment of a study_pid
- form validation (esp ping templates)
- switch from using localstorage to store access tokens to using httponly
- put captcha on register and login
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

cloud research integration
- user creates an enrollment project. they can do this on their own manually
- when you make a ping template, it makes a CR project for each ping
- when participants enroll, they get added to a scheduler such that when their ping block time comes, they are added to included participants for the appropriate project. when ping expires, they are removed
- when participants click ema link, they get a telegram message with a link that asks if they completed the ping. when they click that they get credited (optional feature)



add users to study
- make it so that people can't change their own privilege (i.e. owners can't make themselves non-owners), both on the front end and on the backend
- make it so that the dropdown says what "owner" means i.e. "Owner (sharing privilege)"
- where viewing the users on a study, combine the first and last name into a single field
- in the studynav, make it so that you can only see the users tab if you are an owner. this may involve editing the study context to include role