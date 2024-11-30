from sqlalchemy import Column, Integer, String

from data.modelbase import SqlAlchemyBase


class Notification(SqlAlchemyBase):
    __tablename__ = 'manychat_notifications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(Integer)
    user_id = Column(String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'user_id': self.user_id
        }