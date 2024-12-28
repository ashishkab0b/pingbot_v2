
REQUIRED FOR BASIC FUNCTION

- start date is incorrect
- cascade deletes
- prevent double enrollment of a telegram id
- test ping url forwarding including reminders, expire, completed, and pr completed

LOWER PRIORITY
- check all handling of timezones

- when user changes params of study, change upcoming pings (optionally)

- add functionality to modify study permissions

- look at gpt conversation called session management to make sure i'm doing this right

- form validation (esp ping templates)

- click on ping to show template or participant

- show pings in participant timezone

- make a route to get a survey link or survey message 

- add material ui

- instructions
    - clarify on ping template page that day 0 is not included in "every day"
    - add instruction of variables in url and message

- adjust timezone var variables like reminder and expiretime that go in message and url

- add feedback link on researcher interface
    - save to db
    - send me message on telegram

- check for re-use of study pid in enrollment - check implications

participants capabilities
- change timezone (and then update pings)
- unenroll

- add edit for ping templates
- rotate_keys in cron on server
- make update interfaces - i.e. edit

- make create ping template interface better

- account.js
- forgot your password

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
