from django.db.models import Q

from students.models import Student


def filter_student(*fields, query):
    terms = query.split()
    matches = Student.objects.none()
    for term in terms:
        conditions = Q()
        for field in fields:
            condition = {field + '__icontains': term}
            conditions |= Q(**condition)
        matches |= Student.objects.filter(conditions)
    return matches.distinct().order_by('first_name')
