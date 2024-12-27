
- check all handling of timezones
- when user changes params of study, change upcoming pings (optionally)
- ping url forwarding
- expiry and reminders
- add functionality to modify study permissions

- check columns of what is displayed in dashboards (e.g. ping dash)

- validation of input data
    - reminder latency, expire latency

- show pings in participant timezone

- deal with orphan enrollments (i.e. no one linked telegram id ). possibly move ping making to after telegram link

- add feedback link on researcher interface
    - save to db
    - send me message on telegram

participants capabilities
- change timezone (and then update pings)
- unenroll

- rotate_keys in cron on server

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
