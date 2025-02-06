from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, Admin, Member, Driver, ClientCompany, IndividualClient


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'phone', 'role', 'profile_pic',
                  'is_active', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}, 'is_active': {'read_only': True},
                        'is_staff': {'read_only': True}}  # Assure que le mot de passe n'est pas lu

    def validate_password(self, value):
        try:
            validate_password(value)
            return value
        except Exception as e:
            raise serializers.ValidationError(e)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model.objects.create_user(
            **validated_data,
            password=password  # Mot de passe passé séparément
        )
        return user


class AdminSerializer(CustomUserSerializer):
    class Meta(CustomUserSerializer.Meta):
        model = Admin
        fields = CustomUserSerializer.Meta.fields + ['created_at', 'last_login']


class MemberSerializer(CustomUserSerializer):
    class Meta(CustomUserSerializer.Meta):
        model = Member
        fields = CustomUserSerializer.Meta.fields + ['registration_date', 'status', 'address']


class DriverSerializer(MemberSerializer):
    class Meta(MemberSerializer.Meta):
        model = Driver
        fields = MemberSerializer.Meta.fields + ['driving_license', 'experience']


class ClientCompanySerializer(MemberSerializer):
    class Meta(MemberSerializer.Meta):
        model = ClientCompany
        fields = MemberSerializer.Meta.fields + ['company_name', 'industry']


class IndividualClientSerializer(MemberSerializer):
    class Meta(MemberSerializer.Meta):
        model = IndividualClient
        fields = MemberSerializer.Meta.fields
