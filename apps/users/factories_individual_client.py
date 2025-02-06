from apps.users.models import IndividualClient  # Remplacez par le chemin réel de votre modèle

fake = Faker()


class IndividualClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IndividualClient

    email = factory.LazyAttribute(lambda _: fake.email())
    username = factory.LazyAttribute(lambda _: fake.user_name())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    phone = factory.LazyAttribute(lambda _: fake.phone_number())
    address = factory.LazyAttribute(lambda _: fake.address())
    role = 'client'
