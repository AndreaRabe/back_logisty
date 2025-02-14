from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, Admin, Member, Driver, ClientCompany, IndividualClient, DriverChiefRequest, ChiefFleet


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'password', 'phone', 'role', 'profile_pic',
                  'is_active', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}  # Assure que le mot de passe n'est pas lu
        read_only_fields = ['id', 'is_active', 'is_staff']

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
        fields = CustomUserSerializer.Meta.fields + ['created_at', 'last_admin_login']
        read_only_fields = ["id", "created_at", "last_admin_login"]


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


class ChiefFleetSerializer(CustomUserSerializer):
    drivers_list = DriverSerializer(many=True, read_only=True, source="drivers")

    class Meta(CustomUserSerializer.Meta):
        model = ChiefFleet
        fields = CustomUserSerializer.Meta.fields + ['company_name', 'company_address', 'drivers_list']
        read_only_fields = ["drivers_list"]


class DriverChiefRequestSerializer(serializers.ModelSerializer):
    driver = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all(),
    )
    chief_fleet = serializers.PrimaryKeyRelatedField(
        queryset=ChiefFleet.objects.all(),
    )

    driver_details = DriverSerializer(source='driver', read_only=True)  # Affichage détaillé
    chief_fleet_details = ChiefFleetSerializer(source='chief_fleet', read_only=True)  # Affichage détaillé

    class Meta:
        model = DriverChiefRequest
        fields = ['id', 'driver', 'chief_fleet', 'status', 'created_at', 'updated_at', 'driver_details',
                  'chief_fleet_details']
        read_only_fields = ['id', 'created_at', 'updated_at', 'driver_details',
                            'chief_fleet_details']  # Ces champs sont gérés automatiquement

    def validate(self, data):
        """
        Vérifie qu'un même conducteur ne peut pas envoyer plusieurs demandes au même Chef de flotte.
        """
        driver = data.get('driver')
        chief_fleet = data.get('chief_fleet')

        # Vérifie s'il existe déjà une demande acceptée pour ce conducteur et ce Chef de flotte
        if DriverChiefRequest.objects.filter(
                driver=driver,
                chief_fleet=chief_fleet,
                status='accepted'
        ).exists():
            raise serializers.ValidationError({
                "error": "Ce conducteur est déjà associé au Chef de flotte sélectionné."
            })

        # Vérifie s'il existe déjà une demande en attente (pending) pour ce conducteur et ce Chef de flotte
        if DriverChiefRequest.objects.filter(
                driver=driver,
                chief_fleet=chief_fleet,
                status='pending'
        ).exists():
            raise serializers.ValidationError(
                {"error": "Une demande en attente existe déjà pour ce conducteur et ce Chef de flotte."})

        if DriverChiefRequest.objects.filter(
                driver=driver,
                status='accepted'
        ).exists():
            raise serializers.ValidationError({
                "error": "Ce conducteur est déjà associé a un Chef de flotte."
            })

        return data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de DriverChiefRequest.
        Les IDs de `driver` et `chief_fleet` sont récupérés depuis les données initiales ou le contexte.
        """

        return DriverChiefRequest.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Met à jour le statut d'une demande existante.
        """
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
