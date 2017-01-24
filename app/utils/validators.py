from wtforms.validators import ValidationError

class PhoneFormat(object):
	def __init__(self, message=u'The Phone number provided is not valid. Ensure you start with country code e.g +2547 for Kenya'):
		self.message = message

	def __call__(self, form, field):
		phone
		phone = (field.data).strip()
		if phone[0] != "+":
			raise ValidationError(self.message)