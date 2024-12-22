
from flask import Blueprint

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/get_studies', methods=['POST'])
def admin_get_studies():
    pass

@admin_bp.route('/get_study')
def admin_get_study():
    pass

@admin_bp.route('/get_pings', methods=['POST'])
def admin_get_pings():
    pass

@admin_bp.route('/get_ping', methods=['POST'])
def admin_get_ping():
    pass

@admin_bp.route('/get_participants', methods=['POST'])
def admin_get_participants():
    pass

@admin_bp.route('/get_participant', methods=['POST'])
def admin_get_participant():
    pass

@admin_bp.route('/get_ping_templates', methods=['POST'])
def admin_get_ping_templates():
    pass

@admin_bp.route('/get_ping_template', methods=['POST'])
def admin_get_ping_template():
    pass

