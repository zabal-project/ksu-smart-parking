from models.activity_log import ActivityLog
from flask import request

def log_activity(user_id, action, details):
    ip = request.remote_addr if request else None
    ActivityLog.create(user_id, action, details, ip)
