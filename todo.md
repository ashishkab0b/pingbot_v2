
REQUIRED FOR BASIC FUNCTION

- test ping url forwarding including reminders, expire, completed, and pr completed
- limit late sending to an acceptable delay
- feedbackwidget
- add userstudy to cascading deletes
- send email on updating support db
- ping send time is wrong. i chose it to be 5am to 5:01 and it's showing 4:53 am

- make instructions
    - first make a study using the study dashboard
    - public name will be seen by the participants, internal name is for you in case you want to include things like study numbers and other details about the study (gpt: add to this)
    - contact message can be found in the study dashboard that participants have access to. here you can leave a message with instructions for the participants to contact you if they have any questions or issues with the study
    - click the study to open up the study interface. here you can find a link that you can give to participants that will allow them to enroll in the study
    - you must include a unique participant Id in the link. if you are using a survey platform like qualtrics, you will put in a variable (link to this https://www.qualtrics.com/support/fr/survey-platform/survey-module/survey-flow/standard-elements/embedded-data/#SettingValuesFromTheSurveyURL)
    - 

MID PRIORITY
- include scheduled_ts in pings or recommend researchers do that (make sure format is good thougha)
- include ping template id in ping table - include link to ping template and to particpant
- prevent double enrollment of a study_pid
- page numbers incorrect sometimes for table
- when user changes params of study, change upcoming pings (optionally)
- otp links are not clickable
- form validation (esp ping templates)
- switch from using localstorage to store access tokens to using httponly
- sanitize all input of javascript.

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
