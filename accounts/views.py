from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from accounts.models import User, EmergencyContact
from .serializers import UserLoginSerializer, UserSerializer, ContactSerializer


@api_view(["POST", ])
@permission_classes([AllowAny, ])
def create_user_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        full_name = serializer.validated_data.get("full_name")
        print(password)
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            user = User.objects.create_user(email=email, password=password, full_name=full_name)
            # user.set_password(password)
            # user.save()
    else:
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
    return Response(
        {
            "message": "Account created",
            "email": user.email,
            "full_name": user.full_name,
        },
        status=status.HTTP_201_CREATED
    )


@api_view(["POST", ])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user.save()

        return Response(
            {
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                "full_name": user.full_name,
            },
            status=status.HTTP_200_OK
        )
    else:
        try:
            message = serializer.errors['non_field_errors'][0]
        except (IndexError, KeyError) as e:
            message = "Some random message I don't know y"

    return Response({'message': message}, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)

class ContactModify(APIView):

    permission_classes(IsAuthenticated)

    def post(self, request):
        user = User.objects.get(user=request.user)
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            number = serializer.validated_data.get("number")
            e = EmergencyContact(user=user, name=name, number=number)
            e.save()
            return Response({"message": "Contact added"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Contact could not be added"}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            user = User.objects.get(user=request.user)
        except ObjectDoesNotExist:
            return Response({"message": "User profile does not exist!"}, status=status.HTTP_404_NOT_FOUND)
        emergency_contacts = user.emergency_contacts.all()
        contact_list = []
        for phone in emergency_contacts:
            contact_list.append(phone.number)
        return Response(contact_list, status=status.HTTP_200_OK)