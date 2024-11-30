from flask_restframework import fields
from flask_restframework.fields import BaseField
from flask_restframework.serializer.model_serializer import ModelSerializer
from sqlalchemy import Column
import sqlalchemy as sa

class SqlAlchemyModelSerializer():

    field_mapping = {
        sa.Integer: fields.IntegerField,
        sa.String: fields.StringField,
    }

    def get_fields(self):

        if not self._fields:
            model = self.get_model()

            output = {}

            for column in model.__table__.columns:  #type: Column
                columnType = column.type if callable(column.type) else column.type.__class__

                if columnType not in self.field_mapping:
                    raise ValueError("No mapping for field {}".format(columnType))

                serializerFieldClass = self.field_mapping[columnType]

                output[column.name] = self.instantiate_serializer_field(serializerFieldClass, column, model)

            self._fields = output

        return self._fields

    def instantiate_serializer_field(self, serializerFieldClass, column, model):
        #type: (type, Column, None)->BaseField
        return serializerFieldClass(
            required=(not column.nullable),
            blank=column.nullable,
            default=column.default
        )
