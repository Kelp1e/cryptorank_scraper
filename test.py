from db.models import Test
from db.setup import create_session

session = create_session()
s = session()

t = Test(key="test_key", name="Test Key", description="2")
s.merge(t)
s.commit()
