from students.models import Student


def get_student_fields(new=None):
    all_fields = [field.name for field in Student._meta.fields]
    if new:
        all_fields.append(new)
    return all_fields


def check_password_change(student, old, new):
    if old and not new:
        return{'new_password': 'Ensure this value is provided'}
    elif not old and new:
        return{'password': 'Ensure this value is provided'}
    elif old and new and not student.check_password(old):
        return{'password': 'Value is incorrect'}
    elif old == new:
        return{'new_password': 'Value must be different'}
