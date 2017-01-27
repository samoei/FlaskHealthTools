from wtforms import StringField
from wtforms.validators import Required, Length
from wtforms.widgets import TextArea
from flask_wtf import FlaskForm
from ..utils.validators import PhoneFormat


class SubmissionForm(FlaskForm):
	phone_no = StringField('Your Phone No', validators=[Required(), Length(10, 13, "Ensure your phone number format is +2547XXXXXXXX and is not more than 13 characters"), PhoneFormat(message='The Phone number provided is not valid. Ensure you start with country code e.g +2547 for Kenya')], render_kw={"placeholder": "+2547XXXXXXXX"})
	query = StringField('Query', widget=TextArea(), validators=[Required(), ], render_kw={"placeholder": "Doctor Philemon Kipkorir Samoei"})
