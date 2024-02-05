import json
import queue
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Grade, InboxMessage, Quarters, Section, Teacher, ClassRecord, GradeScores, Student
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

def transfer_record(request):
    teacher = request.user.teacher
    # Filter based on related students' class_type in GradeScores
    grade_scores = GradeScores.objects.filter(student__class_type='Subject', student__teacher_id=teacher).distinct()

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

@require_POST
@login_required
def process_message(request):
    if request.method == 'POST':
        try:
            teacher = request.user.teacher
            message_id = request.POST.get('message_id')
            action = request.POST.get('action')

            # Retrieve the message from the database
            message = InboxMessage.objects.get(id=message_id)

            # Load JSON data from the message
            data = json.loads(message.json_data)

            # Create or retrieve the ClassRecord instance
            class_record, created = ClassRecord.objects.get_or_create(
                name=data["className"],
                defaults={
                    'grade': Grade.objects.get_or_create(name=data["transferRecords"][0]["grade"])[0],
                    'section': Section.objects.filter(name=data["transferRecords"][0]["section"]).first(),
                    'subject': data["transferRecords"][0]["subject"],
                    'quarters': Quarters.objects.get_or_create(quarters=data["transferRecords"][0]["quarter"])[0],
                    'teacher': Teacher.objects.get(id=teacher.id)
                }
            )

# Iterate through students and update their scores
            for student_data in data["transferRecords"][0]["students"]:
                # Assuming that the students already exist, retrieve the student by name and lrn
                students = Student.objects.filter(name=student_data["name"], lrn=student_data["lrn"])

                if students.exists():
                    # If there are multiple students with the same name and LRN, choose one (you may want to add more logic here)
                    student = students.first()

                    grade_scores, created = GradeScores.objects.get_or_create(
                        student=student,
                        class_record=class_record,
                        defaults={
                            'scores_hps_written': [],
                            'scores_hps_performance': [],
                            'total_ww_hps': None,
                            'total_pt_hps': None,
                            'total_qa_hps': None,
                            'written_works_scores': [],
                            'performance_task_scores': [],
                            'initial_grades': None,
                            'transmuted_grades': None,
                            'total_score_written': None,
                            'total_max_score_written': None,
                            'total_score_performance': None,
                            'total_max_score_performance': None,
                            'total_score_quarterly': None,
                            'total_max_score_quarterly': None,
                            'percentage_score_written': None,
                            'percentage_score_performance': None,
                            'percentage_score_quarterly': None,
                            'weight_input_written': None,
                            'weight_input_performance': None,
                            'weight_input_quarterly': None,
                            'weighted_score_written': None,
                            'weighted_score_performance': None,
                            'weighted_score_quarterly': None,
                            # Add other fields as needed
                        }
                    )

                    if not created:
                        # Update existing GradeScores instance
                        scores_data = student_data["scores"]

                        grade_scores.scores_hps_written = scores_data.get("scores_hps_written", [])
                        grade_scores.scores_hps_performance = scores_data.get("scores_hps_performance", [])
                        grade_scores.total_ww_hps = scores_data.get("total_ww_hps", None)
                        grade_scores.total_pt_hps = scores_data.get("total_pt_hps", None)
                        grade_scores.total_qa_hps = scores_data.get("total_qa_hps", None)
                        grade_scores.written_works_scores = scores_data.get("written_works_scores", [])
                        grade_scores.performance_task_scores = scores_data.get("performance_task_scores", [])
                        grade_scores.initial_grades = scores_data.get("initial_grades", None)
                        grade_scores.transmuted_grades = scores_data.get("transmuted_grades", None)
                        grade_scores.total_score_written = scores_data.get("total_score_written", None)
                        grade_scores.total_max_score_written = scores_data.get("total_max_score_written", None)
                        grade_scores.total_score_performance = scores_data.get("total_score_performance", None)
                        grade_scores.total_max_score_performance = scores_data.get("total_max_score_performance", None)
                        grade_scores.total_score_quarterly = scores_data.get("total_score_quarterly", None)
                        grade_scores.total_max_score_quarterly = scores_data.get("total_max_score_quarterly", None)
                        grade_scores.percentage_score_written = scores_data.get("percentage_score_written", None)
                        grade_scores.percentage_score_performance = scores_data.get("percentage_score_performance", None)
                        grade_scores.percentage_score_quarterly = scores_data.get("percentage_score_quarterly", None)
                        grade_scores.weight_input_written = scores_data.get("weight_input_written", None)
                        grade_scores.weight_input_performance = scores_data.get("weight_input_performance", None)
                        grade_scores.weight_input_quarterly = scores_data.get("weight_input_quarterly", None)
                        grade_scores.weighted_score_written = scores_data.get("weighted_score_written", None)
                        grade_scores.weighted_score_performance = scores_data.get("weighted_score_performance", None)
                        grade_scores.weighted_score_quarterly = scores_data.get("weighted_score_quarterly", None)
                        # Update other fields as needed

                        grade_scores.save()
                else:
                    # Handle the case where no student is found (print a message, log, or take appropriate action)
                    print(f"No student found for Name: {student_data['name']} and LRN: {student_data['lrn']}")

            # ...

            # Delete the processed message from the InboxMessage model
            message.delete()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error'})
