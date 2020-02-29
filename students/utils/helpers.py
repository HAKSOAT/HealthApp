from students.models import Student


def get_student_fields():
    all_fields = [field.name for field in Student._meta.fields]
    return all_fields
