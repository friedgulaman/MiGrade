from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, resolve
from .models import ClassRecord, GradeScores, Subject
from django.db.models import Q
from django.template.loader import render_to_string

def search_classrecord(request):
    ctx = {}
    search_input = request.GET.get("search_input")
    matched_urls = {}
    error_message = None

    if search_input:
        # Assuming the user has a teacher profile linked
        teacher = request.user.teacher 
        class_records = ClassRecord.objects.filter(
            Q(name__contains=search_input) |
            Q(grade__icontains=search_input) |
            Q(section__icontains=search_input) |
            Q(subject__icontains=search_input) |
            Q(quarters__icontains=search_input) |
            Q(school_year__icontains=search_input),
            teacher=teacher,
        )
        ctx["class_records"] = class_records

        # Extract the search input from the URL
        search_terms = search_input.lower()  # Convert to lowercase for case-insensitive comparison
        
        # Mapping of search terms to view names
        view_mapping = {
            'faqs': 'faqs',
            'documentation': 'documentation',
            'about': 'about',
            'adviser_manual': 'adviser_manual',
            'subject_manual': 'subject_manual',
            'submit_feedback': 'submit_feedback',
            'home_adviser_teacher': 'home_adviser_teacher',
            'upload_adviser_teacher': 'upload_adviser_teacher',
            'inbox_open': 'inbox_open',
            'display_students': 'display_students',
            'get_grade_details': 'get_grade_details',
            'sf9': 'sf9',
            'generate_per_subject': 'generate_per_subject',
            'generate_per_all_subject': 'generate_per_all_subject',
            'generate_final_grade': 'generate_final_grade',
            'archived_records': 'archived_records',
            'profile_page': 'profile_page',
            'update_profile_photo': 'update_profile_photo',
            'update_teacher_profile': 'update_teacher_profile',
            'change_password': 'change_password',
            'activity': 'activity',
        }

        # Check if the search term matches any key in the view_mapping
        matched_views = [view for term, view in view_mapping.items() if term.lower().startswith(search_input.lower())]

        if matched_views:
            # Generate URLs for matched views
            matched_urls = matched_views
        else:
            error_message = f"No matching view found for '{search_input}'."

    # Prepare the context for rendering
    ctx.update({
        "matched_urls": matched_urls,
        "error_message": error_message,
        "search_input": search_input
    })

    # Check if it's an Ajax request and return JSON response
    does_req_accept_json = request.accepts("application/json")
    is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest" and does_req_accept_json

    if is_ajax_request:
        html = render_to_string(
            template_name="teacher_template/adviserTeacher/results_partial.html", context=ctx
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    # Render the HTML template with the context
    return render(request, "teacher_template/adviserTeacher/adviser_teacher_base.html", context=ctx)
    
def display_classrecord(request, class_record_id=None):
     # If class_record_id is provided, retrieve the ClassRecord object
    class_record = get_object_or_404(ClassRecord, id=class_record_id)
    subject_name = class_record.subject
    teacher = request.user.teacher
    teacher_id = teacher.id
    if teacher_id != class_record.teacher_id:
        return HttpResponseForbidden("You don't have permission to access this class record.")


    grade_scores = GradeScores.objects.filter(class_record=class_record)
    subject = Subject.objects.get(name=subject_name)
    assessments = subject.assessment

    assessment_types = list(assessments.keys())
    processed_types = []
    for assessment_type in assessment_types:
        processed_type = assessment_type.replace(' ', '-').lower()
        processed_types.append(processed_type)

    print(processed_types)

    assessment_type_processed = None

    context = {
            'class_record': class_record,
            'gradescores': grade_scores,
            'assessment_types': processed_types,
            'assessment_values': list(assessments.values()),
        }

    return render(request, 'teacher_template/adviserTeacher/display_classrecord.html', context)