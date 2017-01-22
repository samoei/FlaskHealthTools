from wtforms import StringField
from wtforms.validators import Required, Length
from wtforms.widgets import TextArea
from flask_wtf import FlaskForm


class SubmissionForm(FlaskForm):
	phone_no = StringField('Your Phone No', validators=[Required(), Length(10, 13, "Ensure your phone number format is +2547XXXXXXXX")])
	query = StringField('Query', widget=TextArea(), validators=[Required(), ])
