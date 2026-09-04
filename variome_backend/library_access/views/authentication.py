import json

from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(["POST"])
def login_view(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    if username is None or password is None:
        return Response(
            {"detail": "Please provide username and password."}, status=400
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({"detail": "Invalid credentials."}, status=400)

    login(request, user)
    return Response({"detail": "Successfully logged in."})


@api_view(["POST","GET"])
def logout_view(request):
    if not request.user.is_authenticated:
        return Response({"detail": "You are not logged in."}, status=400)

    logout(request)
    return Response({"detail": "Successfully logged out."})
