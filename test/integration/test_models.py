from datetime import datetime

from giges.models.asana import Project


def test_asana_project(db_session):
    assert Project.query.count() == 0

    project = Project(
        external_id="1",
        name="BoringName",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db_session.add(project)
    db_session.commit()

    assert Project.query.count() == 1
