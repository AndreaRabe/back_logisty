from datetime import datetime

from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from apps.subscription.models import SubscriptionPlan, Subscription
from apps.users.serializers import MemberSerializer


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        read_only_fields = ['id', 'is_active']


class SubscriptionSerializer(serializers.ModelSerializer):
    client_details = MemberSerializer(source='client', read_only=True)
    sub_plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'client', 'sub_plan', 'start_date', 'end_date', 'status', 'client_details', 'sub_plan_details']
        read_only_fields = ['id', 'user_details', 'sub_plan_details']

    def create(self, validated_data):
        # Récupérer le plan d'abonnement à partir des données validées
        sub_plan = validated_data.get('sub_plan')
        
        # Calculer la date de fin en fonction de la durée du plan
        start_date = validated_data.get('start_date', datetime.now().date())
        end_date = start_date + relativedelta(months=sub_plan.duration_month)

        # Ajouter la date de fin aux données validées
        validated_data['end_date'] = end_date

        # Créer et retourner l'objet Subscription
        return super().create(validated_data)
