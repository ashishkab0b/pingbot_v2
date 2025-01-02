
REQUIRED FOR BASIC FUNCTION

- test ping url forwarding including reminders, expire, completed, and pr completed

- make instructions
    - what is EMA? what is it good for? (gpt fill this in)
    - first make a study using the study dashboard
    - public name will be seen by the participants, internal name is for you in case you want to include things like study numbers and other details about the study (gpt: add to this)
    - contact message can be found in the study dashboard that participants have access to. here you can leave a message with instructions for the participants to contact you if they have any questions or issues with the study (gpt, give an example)
    - next you need to make ping templates for the study. ping templates refer to a kind of ping. for example, a study might have 4 ema pings per day that are described by one ping template and an evening diary ping that gets described by another ping template.
    - in the ping template screen, in the ping template screen you can add variables to the message or to the url. variables are wrapped in <> e.g. <DAY_NUM>. the variable will be replaced in the actual ping that gets sent. this allows you for example to add information to the ping. for example, you can put a variable in the url for day number and then instruct qualtrics to save that variable in the data making it easier to process the data later on. if you type < it will open up a list of possible variables you can include.
    - You can also set parameters for if and after how long a reminder should be sent if the participant didn't respond and if and how long the ping will expire and the link will no longer function
    - there are two ways to set the schedule for a ping template. the first way, labeled "every day" allows you to set one or more ping time blocks that will be sent every day on the same schedule (randomly within the ping time block.) When using the every day option, pings will arrive to the participant the day after they enroll in the study. If you need more granular control (for example if you have an exit survey that you would like to be sent on the final day only or if you would like pings to arrive on the same day the participant enrolls), you can use the "per day" control which allows you to set ping time blocks separately for each day. 
    - in case a ping time block extends across two days (e.g. you want that the ping could arrive any time between 10pm and 2am), you can select the "next day" checkbox in order for the end time to refer to the following day
    - after you have made all your ping templates for your study, you can navigate back to the study overview to get a link which allows participants to enroll
    - you must include a unique participant Id in the link. if you are placing your enrollment link within a qualtrics survey, you can put an embedded variable that looks something like this ${e://Field/participant_id} in lieu of the actual Id and if configured correctly in qualtrics, qualtrics will replace it with a participant id. (link to this https://www.qualtrics.com/support/fr/survey-platform/survey-module/survey-flow/standard-elements/embedded-data/#SettingValuesFromTheSurveyURL)
    - the participant will visit the link you provide and enter in their timezone. after they enter their timezone they will be given a unique code that allows them to enroll in the study on telegram.

    - say more clearly what is ping template(i.e. schedule)
    - say where contact message shows to participant

MID PRIORITY
- show sent message in ping db
- include scheduled_ts in pings or recommend researchers do that (make sure format is good thougha)
- include ping template id in ping table - include link to ping template and to particpant
- prevent double enrollment of a study_pid
- page numbers incorrect sometimes for table
- when user changes params of study, change upcoming pings (optionally)
- otp links are not clickable
- form validation (esp ping templates)
- switch from using localstorage to store access tokens to using httponly
- sanitize all input of javascript.
- probability completed

LOWER PRIORITY
- account.js
- forgot your password
    

- add functionality to modify study permissions

- look at gpt conversation called session management to make sure i'm doing this right

- click on ping to show template or participant

- make a route to get a survey link or survey message 


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
