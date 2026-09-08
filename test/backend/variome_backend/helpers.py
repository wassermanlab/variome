from django.contrib.auth.models import User


def create_authenticated_user(client, username="test-user"):
    user = User.objects.create_user(username=username)
    client.force_login(user)
    return user