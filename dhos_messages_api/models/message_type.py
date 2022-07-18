from typing import Dict

from flask_batteries_included.sqldb import ModelIdentifier, db


class MessageType(ModelIdentifier, db.Model):
    # required
    value = db.Column(db.Integer, unique=True, nullable=False)

    @staticmethod
    def schema() -> Dict:
        return {"optional": {}, "required": {"value": int}, "updatable": {"value": int}}

    def to_dict(self) -> Dict:
        return {"value": self.value, **self.pack_identifier()}
