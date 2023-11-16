import json
from django.shortcuts import render
from .models import Student, Teacher  # Import the Teacher model

def student_list(request):
    # Assuming you have authenticated the teacher and have a 'user' object
    user = request.user

    # Check if the user is a teacher
    if user.is_authenticated and hasattr(user, 'teacher'):
        teacher = user.teacher

        # Access the teacher's students
        teacher_students = teacher.students.all()

        # Prepare the data for the Handsontable
        data = []

        # Add the headers as the first row
        data.append(['Name', 'LRN', 'Sex', 'Grade', 'Section'])

        for student in teacher_students:
            data.append([student.name, student.lrn, student.sex, student.grade, student.section])

        # Serialize the data to JSON
        data_json = json.dumps(data)
        print(data_json)  # Add this line for debugging

        return render(request, 'teacher_template/adviserTeacher/new_classrecord.html', {'data_json': data_json})

