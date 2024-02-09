import json
import queue
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import FinalGrade, Grade, InboxMessage, Quarters, Section, Teacher, ClassRecord, GradeScores, Student
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.db.models import Q

def transfer_record(request):
    teacher = request.user.teacher
    final_grades = FinalGrade.objects.filter(teacher=teacher)
    unique_final_grades = final_grades.values('grade', 'section', 'subject').distinct()
    
  
    # Filter based on related students' class_type in GradeScores
    grade_scores = GradeScores.objects.filter(student__class_type='Subject', student__teacher_id=teacher).distinct()

    # Extract unique ClassRecord instances from the filtered GradeScores
    class_records = set(score.class_record for score in grade_scores)



    print(unique_final_grades)
    context = {
        'class_records': class_records,
        'unique_final_grades': unique_final_grades,
    }

    return render(request, 'teacher_template/adviserTeacher/transfer_records.html', context)



def final_grade_details(request):
    teacher = request.user.teacher
    # Retrieve data based on the provided grade, section, and subject
    grade = request.GET.get('grade')
    section = request.GET.get('section')
    subject = request.GET.get('subject')

    final_grades = FinalGrade.objects.filter(grade=grade, section=section, subject=subject, teacher=teacher)
    # Extract final grade JSON data
    final_grade_data = []
    for final_grade in final_grades:
        final_grade_data.append(final_grade.final_grade)

    context = {
        'final_grades': final_grades,
        'final_grade_data': final_grade_data,
    }

    return render(request, 'teacher_template/adviserTeacher/final_grades_details.html', context)


def transfer_details(request):
    # Use 'class_record_id' instead of 'class_record_id'
    class_record_id = request.GET.get('id')

    # Check if class_record_id is provided in the request
    if class_record_id:
        # Filter based on related students' class_type in GradeScores
        grade_scores = GradeScores.objects.filter(student__class_type='Subject', class_record__id=class_record_id).distinct()

        # Extract unique ClassRecord instances from the filtered GradeScores
        class_records = set(score.class_record for score in grade_scores)
    else:
        # If class_record_id is not provided, handle accordingly (e.g., redirect, show an error message)
        class_records = None

    return render(request, 'teacher_template/adviserTeacher/transfer_details.html', {'class_records': class_records})

@csrf_exempt
def get_teacher_list(request):
    if request.method == 'GET':
        teachers = Teacher.objects.all()
        teacher_list = [{'id': teacher.id, 'name': f"{teacher.user.first_name} {teacher.user.last_name}"} for teacher in teachers]
        return JsonResponse({'teachers': teacher_list})

    elif request.method == 'POST':
        try:
            # Assuming you receive JSON data in the request
            data = json.loads(request.body.decode('utf-8'))
            teacher_id = data.get('teacher_id')
            json_data = data.get('json_data')

            # Now you can use teacher_id and json_data as needed
            # For example, save the json_data to the corresponding teacher

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@require_POST
@login_required
def submit_json(request):
    try:
        # Get JSON data from request.body
        json_data = json.loads(request.body.decode('utf-8'))

        to_teacher = json_data.get('teacherId')
        user = request.user
        from_teacher = user.teacher  # Assuming user.teacher is a Teacher instance
        file_name = json_data.get('className')
        grade = json_data.get('transferRecords', [])[0].get('grade', None)
        section = json_data.get('transferRecords', [])[0].get('section', None)

        # Check if the section with the specified name, class_type, and teacher_id exists
        existing_section = Section.objects.filter(name=section, class_type="Advisory", teacher_id=to_teacher).exists()

        if existing_section:
            # Save the data to the InboxMessage model
            InboxMessage.objects.create(to_teacher=to_teacher, from_teacher=from_teacher, json_data=json.dumps(json_data), file_name=file_name)
            return JsonResponse({'success': True, 'message': 'Data submitted successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid section or teacher.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
@csrf_exempt
@require_POST
@login_required
def transfer_json_to_teacher(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            target_teacher_id = json_data.get('target_teacher')
            from_teacher_id = json_data.get('teacher')
            from_teacher = Teacher.objects.get(id=from_teacher_id)  # Assuming from_teacher_id is the ID of the teacher
            file_name = json_data.get('quarters')
            section = json_data.get('section')
            print(json_data)
            print(from_teacher)
            # Check if the section with the specified name, class_type, and teacher_id exists
            existing_section = Section.objects.filter(name=section, class_type="Advisory", teacher_id=target_teacher_id).exists()
            print(existing_section)
            if existing_section:
                # Save the data to the InboxMessage model
                InboxMessage.objects.create(to_teacher=target_teacher_id, from_teacher=from_teacher, json_data=json.dumps(json_data), file_name=file_name)
                return JsonResponse({'success': True, 'message': 'Data submitted successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid section or teacher.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def inbox_open(request):
    try:
        user = request.user

        # Check if the logged-in user is a teacher
        if hasattr(user, 'teacher'):
            teacher = user.teacher.id
            print(teacher)
            # Get inbox messages where the logged-in teacher is the intended recipient
            inbox_messages = InboxMessage.objects.filter(to_teacher=teacher)

            return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': inbox_messages})

        else:
            # Handle the case where the logged-in user is not a teacher
            return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': []})

    except Exception as e:
        # Handle any exceptions
        print(f"Error in inbox_open: {e}")
        return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': []})




@login_required
def inbox(request):
    teacher_username = request.user.username  # Assuming the username is used for filtering
    teacher = get_user_model().objects.get(username=teacher_username)
    
    messages = InboxMessage.objects.filter(teacher=teacher).order_by('-timestamp')

    return render(request, 'teacher_template/adviserTeacher/inbox.html', {'messages': messages})


def transfer_quarterly_grade(request, grade, section, subject, class_record_id):
    # Retrieve the specific class record based on the provided class_record_id
    class_record = get_object_or_404(ClassRecord, id=class_record_id, grade=grade, section=section, subject=subject)

    # Retrieve grade scores related to the class record
    grade_scores = GradeScores.objects.filter(class_record=class_record)

    
    context = {
        'class_record': class_record,
        'grade_scores': grade_scores,
    }

    return render(request, "teacher_template/adviserTeacher/transfer_quarterly_grade.html", context)