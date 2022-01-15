from models import Connection


def test_it_can_get_connections_between_organizations(factory):
    org1 = factory.organization()
    org2 = factory.organization()

    factory.link(
        source_webpage=factory.webpage(website=org1.website),
        target_webpage=factory.webpage(website=org2.website),
    )

    assert Connection.query.count() == 1
    connection = Connection.first()

    connection.source_organization = org1
    len(org1.outbound_connections) == 1
    len(org1.inbound_connections) == 0

    connection.target_organization = org2
    len(org2.outbound_connections) == 0
    len(org2.inbound_connections) == 1


def test_it_includes_only_unique_connections(factory):
    org1 = factory.organization()
    org2 = factory.organization()

    factory.link(
        source_webpage=factory.webpage(website=org1.website),
        target_webpage=factory.webpage(website=org2.website),
    )
    factory.link(
        source_webpage=factory.webpage(website=org1.website),
        target_webpage=factory.webpage(website=org2.website),
    )

    assert Connection.query.count() == 1
    connection = Connection.first()
    connection.source_organization = org1
    connection.target_organization = org2


def test_it_ignores_connections_unless_both_sides_are_organizations(factory):
    link = factory.link()
    factory.organization(website=link.source_webpage.website)

    assert Connection.query.count() == 0

    factory.organization(website=link.target_webpage.website)

    assert Connection.query.count() == 1