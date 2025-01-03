import pytest
from fitness import FitnessDB


@pytest.fixture
def db():
    db = FitnessDB(":memory:")
    return db


def test_link_client_and_membership(db):
    client_id = db.add_client("John Doe")
    membership_id = db.add_membership("Swimming pool")

    db.link_client_and_membership(client_id, membership_id)

    cursor = db.conn.cursor()
    cursor.execute('SELECT * FROM t_client_membership WHERE client_id = ? AND membership_id = ?',
                   (client_id, membership_id))
    link = cursor.fetchone()
    cursor.close()
    assert link is not None, "Связь между клиентом и абонементом не была создана."


def test_get_client_membership(db):
    client_id = db.add_client("John Doe")
    membership_id1 = db.add_membership("Gym Access")
    membership_id2 = db.add_membership("Swimming Pool")

    db.link_client_and_membership(client_id, membership_id1)
    db.link_client_and_membership(client_id, membership_id2)

    memberships = db.get_client_membership("John Doe")
    assert len(memberships) == 2, "Количество абонементов неверное."
    assert ("Gym Access",) in memberships, "Абонемент 'Gym Access' отсутствует."
    assert ("Swimming Pool",) in memberships, "Абонемент 'Swimming Pool' отсутствует."


def test_sql_injection_prevention(db):
    client_id = db.add_client("John'; DROP TABLE t_client; --")
    membership_id = db.add_membership("Yoga")

    db.link_client_and_membership(client_id, membership_id)

    memberships = db.get_client_membership("John'; DROP TABLE t_client; --")
    assert len(memberships) == 1, "SQL-инъекция сработала"
    assert ("Yoga",) in memberships, "Абонемент 'Yoga' отсутствует."
