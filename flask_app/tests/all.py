

from register import register
from make_study import get_token, create_study, get_study, make_ping_templates

register()
token = get_token()
resp = create_study(token)
study_id = resp["study"]["id"]
get_study(token, study_id)
make_ping_templates(token, study_id)
