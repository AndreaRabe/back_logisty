import factory
import pytest
from faker import Faker
from rest_framework.test import APIClient

from apps.users.models import IndividualClient  # Remplacez par le chemin réel de votre modèle

prelink = "http://127.0.0.1:8000/api/v1/"

fake = Faker()


class IndividualClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IndividualClient

    email = factory.LazyAttribute(lambda _: fake.email())
    username = factory.LazyAttribute(lambda _: fake.user_name()[:25])
    first_name = factory.LazyAttribute(lambda _: fake.first_name()[:25])
    last_name = factory.LazyAttribute(lambda _: fake.last_name()[:20])
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    phone = factory.LazyAttribute(lambda _: fake.phone_number()[:15])
    address = factory.LazyAttribute(lambda _: fake.address())
    role = 'client'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_individual_client():
    def _create_individual_client(**kwargs):
        return IndividualClientFactory.create(**kwargs)

    return _create_individual_client


# Test POST - Créer un compte client particulier
@pytest.mark.django_db
def test_create_individual_client(api_client, create_individual_client):
    url = prelink + 'client_signup/'  # Assurez-vous que le nom de l'URL est correct
    data = {
        "email": fake.email(),
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "password": "SecurePass123!",
        "phone": "+261342078956",
        "address": fake.address(),
        "role": "client"
    }
    response = api_client.post(url, data, format='json')
    print(response.content)
    assert response.status_code == 201
    assert IndividualClient.objects.count() == 1
    assert response.data['email'] == data['email']


# Test GET - Voir le profil du client particulier
@pytest.mark.django_db
def test_get_individual_client_profile(api_client, create_individual_client):
    client = create_individual_client()
    api_client.force_authenticate(user=client)  # Authentifiez le client
    url = prelink + 'client_profile/'  # Assurez-vous que le nom de l'URL est correct
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['email'] == client.email


# Test PUT - Mettre à jour le profil du client particulier
@pytest.mark.django_db
def test_update_individual_client_profile(api_client, create_individual_client):
    client = create_individual_client()
    api_client.force_authenticate(user=client)  # Authentifiez le client
    url = prelink + 'client_profile/'  # Assurez-vous que le nom de l'URL est correct
    updated_data = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        "phone": "1234567890"
    }
    response = api_client.put(url, updated_data, format='multipart')
    assert response.status_code == 200
    client.refresh_from_db()
    assert client.first_name == updated_data['first_name']
    assert client.last_name == updated_data['last_name']


# Test DELETE - Supprimer le compte du client particulier
@pytest.mark.django_db
def test_delete_individual_client(api_client, create_individual_client):
    client = create_individual_client()
    api_client.force_authenticate(user=client)  # Authentifiez le client
    url = prelink + 'client_profile/'  # Assurez-vous que le nom de l'URL est correct
    response = api_client.delete(url)
    assert response.status_code == 204
    assert IndividualClient.objects.count() == 0
