
- check all handling of timezones
- when user changes params of study, change upcoming pings (optionally)
- ping url forwarding
- expiry and reminders

- reinit db 
    - add functionality for url_text

- validation of input data
    - reminder latency, expire latency

- add scheduled_ts_user_tz to ping display

- deal with orphan enrollments (i.e. no one linked telegram id ). possibly move ping making to after telegram link

participants capabilities
- change timezone (and then update pings)
- unenroll

- rotate_keys in cron on server

- put "get_user_studies" and similar methods from ping templates bp and other files into a separate file

- make create ping template interface better

- check blueprints use .to_dict()

prolific integration
- studies get published at the beginning of the ping block
- post unpublished study draft
- post publish study
- auto approve participants after completion
- one click approve completed participants'
- approval button on pings sheet
- generate spreadsheet with all pings and "approve" column. user uploads spreadsheet again to approve participants.