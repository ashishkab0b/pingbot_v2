
- TOKEN#token, USER#UserID
    - email
- EMAIL#Email, USER#UserID
- STUDY#StudyID, STUDY#StudyID
    - GSI1 - CODE#StudyCode
- USER#UserID, STUDY#StudyID 
- STUDY#StudyID, USER#UserID 
- PARTICIPANT#PartID, PARTICIPANT#PartID
    - GSI1 - TELEGRAM#TelegramID
- STUDY#StudyID, PARTICIPANT#PartID
    - GSI1 - PID#StudyPid
- PARTICIPANT#PartID, STUDY#StudyID
    - GSI1 - PID#StudyPid
- PARTICIPANT#PartID, PING#PingID
    - GSI1 - STUDY#StudyID, PING#PingID
    - GSI2 - PINGTEMPLATE#PingTemplateID, PING#PingID
- STUDY#StudyID, PINGTEMPLATE#TemplateID


