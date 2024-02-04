import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import InboxMessage, Teacher, ClassRecord, GradeScores, Student
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

def transfer_record(request):
    # Filter based on related students' class_type in GradeScores
    grade_scores = GradeScores.objects.filter(student__class_type='Subject').distinct()

    # Extract unique ClassRecord instances from the filtered GradeScores
    class_records = set(score.class_record for score in grade_scores)

    return render(request, 'teacher_template/adviserTeacher/transfer_records.html', {'class_records': class_records})

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
        teacher = request.user

        # Get JSON data from request.body
        json_data = json.loads(request.body.decode('utf-8'))

        # Extract class_name from JSON data
        file_name = json_data.get('className')

        # Save the data to the InboxMessage model
        InboxMessage.objects.create(teacher=teacher, json_data=json.dumps(json_data), file_name=file_name)

        return JsonResponse({'success': True, 'message': 'Data submitted successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    

def inbox_open(request): 
    inbox_messages = InboxMessage.objects.all()  
    return render(request, 'teacher_template/adviserTeacher/inbox.html', {'inbox_messages': inbox_messages})
@login_required
def inbox(request):
    teacher_username = request.user.username  # Assuming the username is used for filtering
    teacher = get_user_model().objects.get(username=teacher_username)
    
    messages = InboxMessage.objects.filter(teacher=teacher).order_by('-timestamp')

    return render(request, 'teacher_template/adviserTeacher/inbox.html', {'messages': messages})