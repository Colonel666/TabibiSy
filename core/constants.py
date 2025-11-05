class Const:
    # USER_TYPE
    USER_TYPE_SUPERUSER = 'superuser'
    USER_TYPE_STAFF     = 'staff'
    USER_TYPE_PATIENT   = 'patient'
    USER_TYPE_DOCTOR    = 'doctor'


USER_TYPE_CHOICES = (
    (Const.USER_TYPE_SUPERUSER, 'Super User'),
    (Const.USER_TYPE_STAFF    , 'Staff'),
    (Const.USER_TYPE_PATIENT  , 'Patient'),
    (Const.USER_TYPE_DOCTOR   , 'Doctor'),
)

DICT_USER_TYPE_CHOICES = dict(USER_TYPE_CHOICES)
