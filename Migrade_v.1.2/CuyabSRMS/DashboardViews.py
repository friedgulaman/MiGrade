# views.py in your_app
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .models import Student
from django.db.models import Count
from .models import Teacher, Student, Grade, Section, Subject
class StudentChartDataView(View):
    def get(self, request, *args, **kwargs):
        # Fetch data from the database
        data = Student.objects.values('school_year').annotate(num_students=Count('id'))

        # Prepare data for JsonResponse
        labels = [entry['school_year'] for entry in data]
        values = [entry['num_students'] for entry in data]

        # Send data as JSON response
        response_data = {
            'labels': labels,
            'values': values,
        }
        return JsonResponse(response_data)

def total_counts(request):
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.count()
    total_grades = Grade.objects.count()
    total_sections = Section.objects.count()
    total_subjects = Subject.objects.count()

    context = {
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_grades': total_grades,
        'total_sections': total_sections,
        'total_subjects': total_subjects,
    }

    return render(request, 'admin_template/home_admin.html', context)