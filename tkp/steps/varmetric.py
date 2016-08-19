from tkp.db.alchemy.varmetric import store_varmetric, del_duplicate_varmetric
from tkp.db.model import Dataset
from tkp.db import Database


def execute_store_varmetric(dataset_id, session=None):
    """
    Executes the storing varmetric function. Will create a database session
    if none is supplied.

    args:
        dataset_id: the ID of the dataset for which you want to store the
                    varmetrics
        session: An optional SQLAlchemy session
    """
    if not session:
        database = Database()
        session = database.Session()

    dataset = Dataset(id=dataset_id)
    delete_ = del_duplicate_varmetric(session=session, dataset=dataset)
    session.execute(delete_)
    insert_ = store_varmetric(session, dataset=dataset)
    session.execute(insert_)
    session.commit()
