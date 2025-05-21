from django.core.mail import mail_managers
from django.core import serializers
from django.forms.models import model_to_dict
import datetime
from django.utils import timezone
import json


def notify_access_limit_reached(user, limit):
    data = serializers.serialize(
        "json",
        [
            user,
        ],
    )
    data_dict = json.loads(data)
    fields_data = data_dict[0]["fields"]  # Get the 'fields' data
    fields_data.pop("password", None)  # Remove the password field
    pretty_user_json = json.dumps(fields_data, indent=4)
    mail_managers(
        "A user's access limit was reached",
        message=f"""
This user has reached their access limit of {limit} accesses per day:

{pretty_user_json}
""",
    )
