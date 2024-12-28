
REQUIRED FOR BASIC FUNCTION

- cascade deletes 
    - (finished enrollment -> ping)
    - study -> ping, enrollment, ping_templates
    - ping_templates -> ping
- test ping url forwarding including reminders, expire, completed, and pr completed

MID PRIORITY
- prevent double enrollment of a study_pid
- page numbers incorrect sometimes for table
- when user changes params of study, change upcoming pings (optionally)
- otp links are not clickable
- form validation (esp ping templates)

LOWER PRIORITY
- account.js
- forgot your password


- add feedback link on researcher interface
    - save to db
    - send me message on telegram
    

- add functionality to modify study permissions

- look at gpt conversation called session management to make sure i'm doing this right


- click on ping to show template or participant

- make a route to get a survey link or survey message 

- add material ui

- instructions
    - clarify on ping template page that day 0 is not included in "every day"
    - add instruction of variables in url and message

- adjust timezone var variables like reminder and expiretime that go in message and url


participants capabilities
- change timezone (and then update pings)
- unenroll

- add edit for ping templates
- rotate_keys in cron on server
- make update interfaces - i.e. edit

- make create ping template interface better


prolific integration
- studies get published at the beginning of the ping block
- post unpublished study draft
- post publish study
- auto approve participants after completion
- one click approve completed participants'
- approval button on pings sheet
- generate spreadsheet with all pings and "approve" column. user uploads spreadsheet again to approve participants.

- pings get assigned when telegram is linked
    - within this process, messages get constructed and vars replaced
    - enrolled = True
