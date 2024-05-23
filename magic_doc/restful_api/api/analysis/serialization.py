import lxml
from marshmallow import Schema, fields, validates, ValidationError


class MagicHtmlSchema(Schema):
    pageUrl = fields.Str()
    html = fields.Str(required=True)
    html_type = fields.Str()

    @validates('html')
    def validate_html(self, data, **kwargs):
        if not data:
            raise ValidationError('HTML cannot be empty')
        else:
            if lxml.html.fromstring(data).find('.//*') is None:
                raise ValidationError('Content is not HTML')
            return data


class MagicPdfSchema(Schema):
    pageUrl = fields.Str(required=True)

    @validates('pageUrl')
    def validate_url(self, data, **kwargs):
        if not data:
            raise ValidationError('pageUrl cannot be empty')
        else:
            return data
