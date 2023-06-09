from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from rest_framework import serializers

from accounts.models import User, EmergencyContact


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'full_name', 'date_joined', 'last_login']
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'email': {
                'required': True
            },
            'full_name': {
                'required': True
            },
            'password': {
                'write_only': True,
                'required': True
            },
            'date_joined': {
                'read_only': True
            },
            'last_login': {
                'read_only': True
            },

        }

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("password", ),
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                msg = _("Unable to Login with the credentials provided")
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _("Must include email and password.")
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'number']
        extra_kwargs = {
            'name': {
                'required': True
            },
            'number': {
                'required': True
            },
        }

class SMS_Serializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)