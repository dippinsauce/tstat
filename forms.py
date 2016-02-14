from flask_wtf import Form
from wtforms import IntegerField, RadioField
from wtforms.validators import NumberRange, Required

class AutoForm(Form):
    setpoint = IntegerField('Desired Temperature', validators=[NumberRange(min=45, max = 85)])

class ManualForm(Form):
    mode = RadioField('Setting', choices=[('heat','Heat'), ('cool','Cool'),
        ('fan','Fan'), ('off', 'OFF')], validators=[Required()])