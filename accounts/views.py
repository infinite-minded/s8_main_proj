from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from accounts.models import User, EmergencyContact
from .serializers import UserLoginSerializer, UserSerializer, ContactSerializer, SMS_Serializer

import requests

from geopy.geocoders import GoogleV3

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
            'user_id': user.pk,
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
        user=request.user
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
            user=request.user
        except ObjectDoesNotExist:
            return Response({"message": "User profile does not exist!"}, status=status.HTTP_404_NOT_FOUND)
        emergency_contacts = EmergencyContact.objects.filter(user=user)
        contact_list = {}
        for phone in emergency_contacts:
            contact_list[phone.name]=phone.number
        return Response(contact_list, status=status.HTTP_200_OK)

class ContactDelete(APIView):

    permission_classes(IsAuthenticated)

    def post(self, request):
        user=request.user
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            number = serializer.validated_data.get("number")
            e = EmergencyContact.objects.filter(user=user, name=name, number=number)
            if not e:
                return Response({"message": "No such contact found!"}, status=status.HTTP_200_OK)
            elif len(e) == 1:
                obj = e[0]
                obj.delete()
                return Response({"message": "Contact removed"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Please provide all parameters for this request."}, status=status.HTTP_400_BAD_REQUEST)

class EmergencySMS(APIView):

    permission_classes(IsAuthenticated)

    def post(self, request):
        serializer = SMS_Serializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data.get("message")
            mlist = message.split(";", 1)
            userid = int(mlist[0])
            coord = mlist[1]
            coords = coord.replace(" ", ", ")
            geolocator = GoogleV3(api_key='AIzaSyDDzP4oIcMhVdzWOJGsQWF3d0D7_csECaU')
            location = geolocator.reverse(coords)
            addr = location.address
            user = User.objects.get(id=userid)
            name = user.full_name
            msg = "Accident - " + name + "\n\n" + addr
            emergency_contacts = EmergencyContact.objects.filter(user=user)
            contact_list = []
            for phone in emergency_contacts:
                contact_list.append(phone.number)
            contacts = ",".join(contact_list)
            url = "https://www.fast2sms.com/dev/bulkV2"
            payload = f"sender_id=TXTIND&message={msg}&route=v3&numbers={contacts}"
            headers = {'authorization': "Xu3AkvCBiSEaWVzUDsMmpQoqrc7TYJfhRPHK5njOIbtG4g2896c20ztN9MR6J8ObDqfQokplwiXKaPLH",
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
            }
            response = requests.request("POST", url, data=payload, headers=headers)
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Please provide all parameters for this request."}, status=status.HTTP_400_BAD_REQUEST)