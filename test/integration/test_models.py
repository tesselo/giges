from datetime import datetime

from giges.models.asana import Project


def test_asana_project(transactional_db):
    assert Project.query.count() == 0

    project = Project(
        external_id="1",
        name="BoringName",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    transactional_db.add(project)
    transactional_db.commit()

    assert Project.query.count() == 1
