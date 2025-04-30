# noinspection PyUnresolvedReferences,PyPackageRequirements
import factory
from base.models import Project, Organisation, Domain
from core.model_factories import UserF



class ProjectF(factory.django.DjangoModelFactory):
    """
    Project model factory
    """
    class Meta:
        model = Project

    name = 'qgis'
    description = u'This is only for testing'
    owner = factory.SubFactory(UserF)
    project_representative = factory.SubFactory(UserF)
    approved = True
    private = False
    gitter_room = u'test/test'

    @classmethod
    def create(cls, **kwargs):
        name = kwargs.get('name', 'qgis')
        existing_project = Project.objects.filter(name=name).first()
        if existing_project:
            return existing_project
        return super().create(**kwargs)


class OrganisationF(factory.django.DjangoModelFactory):
    """
    Organisation model factory
    """
    class Meta:
        model = Organisation

    name = 'Test Organisation'
    owner = factory.SubFactory(UserF)
    approved = True


class DomainF(factory.django.DjangoModelFactory):
    """
    Domain model factory
    """
    class Meta:
        model = Domain

    user = factory.SubFactory(UserF)
    role = factory.Sequence(lambda n: 'Role %s' % n)
    domain = factory.Sequence(lambda n: 'Domain %s' % n)
