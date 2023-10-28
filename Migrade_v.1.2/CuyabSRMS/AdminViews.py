from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import CustomUser, Student, Teacher, Grade, Section
from django.contrib.auth import get_user_model  # Add this import statement
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.db import models
from django.views.decorators.http import require_GET
from django.db.models import Q

#OCR
from .models import ExtractedData
from .models import ProcessedDocument
from google.cloud import documentai_v1beta3 as documentai
import re
import os
import json
from .forms import DocumentUploadForm
from django.conf import settings
from django.shortcuts import HttpResponse
from django.utils.text import get_valid_filename
from .forms import ExtractedDataForm

def home_admin(request):
    # Retrieve the grades queryset
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()

    # Retrieve all sections for each grade
    sections = Section.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
    }
    return render(request, 'admin_template/home_admin.html', context)

def add_teacher(request):
    return render(request, 'admin_template/add_teacher.html')

def add_teacher_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_teacher')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        middle_ini = request.POST.get('middle_ini')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Create a CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_ini=middle_ini,
                user_type=2  # This represents a teacher user
            )

            # No need to create a Teacher object here
            # The Teacher object will be associated with the CustomUser automatically

            messages.success(request, "Teacher Added Successfully!")
            return redirect('add_teacher')
        except IntegrityError:
            messages.error(request, "Failed to Add Teacher!")
            return redirect('add_teacher')
        

def teacherList(request):
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()
    sections = Section.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
    }
    return render(request, 'admin_template/list_of_teacher.html', context)



def submit_grade_section(request):
    if request.method == 'POST':
        # Lists to store created grades and sections
        created_grades = []
        created_sections = []

        # Iterate over the form data
        for key, value in request.POST.items():
            if key.startswith('grade_'):
                grade_name = value
                section_key = f'section_{key.split("_")[1]}[]'
                sections = request.POST.getlist(section_key)

                # Check if the grade already exists in the database
                grade, grade_created = Grade.objects.get_or_create(name=grade_name)

                # Create or update sections associated with the grade
                for section_name in sections:
                    section, section_created = Section.objects.get_or_create(name=section_name, grade=grade)
                    created_sections.append(section.name)

                # Append the created or retrieved grade name to the list
                if grade_created:
                    created_grades.append(grade.name)

        # Add a success message
        messages.success(request, 'Form data submitted successfully.')

    # Retrieve the grades queryset
    grades = Grade.objects.all()

    # Retrieve all sections for each grade
    sections = Section.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
    }
    
    return render(request, 'admin_template/add_grade_section.html', context)

@require_GET
def get_sections(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        grade_id = request.GET.get('grade_id')
        sections = Section.objects.filter(grade_id=grade_id)
        section_list = [{'id': section.id, 'name': section.name} for section in sections]
        
        # Check if there are sections to return
        if section_list:
            return JsonResponse({'sections': section_list})
        else:
            return JsonResponse({'message': 'No sections available for the selected grade'})
    else:
        # Handle non-AJAX requests if needed
        return JsonResponse({'message': 'Invalid request'})
    


def assign_teacher(request):
    # Retrieve the grades, teachers, and sections queryset
    grades = Grade.objects.all()
    teachers = Teacher.objects.all()
    sections = Section.objects.all()

    # Include the grades, sections, and teachers in the context
    context = {
        'grades': grades,
        'sections': sections,
        'teachers': teachers,
    }
    return render(request, 'admin_template/assign_teacher.html', context)

def save_assignment(request):
    if request.method == 'POST':
        # Retrieve the data from the form
        teacher_id = request.POST.get('teacher')
        grade_id = request.POST.get('grade')
        section_id = request.POST.get('section')

        # Validate the data
        if teacher_id and grade_id and section_id:
            try:
                section = Section.objects.get(id=section_id)
                teacher = Teacher.objects.get(id=teacher_id)
                # Assign the teacher to the section
                section.teacher = teacher
                section.save()
                # Store a success message
                messages.success(request, 'Assignment saved successfully')
                return JsonResponse({'success': True})
            except (Section.DoesNotExist, Teacher.DoesNotExist):
                messages.error(request, 'Invalid teacher or section')
        else:
            # Handle the case where data is missing
            messages.error(request, 'Invalid data')
    else:
        # Handle other request methods if needed
        messages.error(request, 'Invalid request method')

    return JsonResponse({'success': False})


def add_grade_section(request):
    grades = Grade.objects.all()
    sections = Section.objects.all()

    # Include the grades and sections in the context
    context = {
        'grades': grades,
        'sections': sections,
    }
    return render(request, 'admin_template/add_grade_section.html', context)


def search_students(request):
    if request.method == 'GET':
        search_query = request.GET.get('q', '')

        students = Student.objects.filter(
            Q(name__icontains=search_query) |
            Q(lrn__icontains=search_query) |
            Q(sex__icontains=search_query) |
            Q(birthday__icontains=search_query) |
            Q(teacher__id__icontains=search_query) |
            Q(grade__icontains=search_query) |
            Q(section__icontains=search_query)
        )

        context = {
            'students': students,
            'search_query': search_query,
        }

        return render(request, 'admin_template/home_admin.html', context)

#sf10 views

# def extract_and_edit_data(request):
#     if request.method == 'POST':
#         # Extract data from the form submission
#         extracted_data = request.POST.get('extracted_data')
        
#         # Parse the extracted data (assuming it is in JSON format)
#         extracted_data_dict = json.loads(extracted_data)
        
#         # Render the editable form with the extracted data
#         return render(request, 'teacher_template/adviserTeacher/edit_extracted_data.html', {'extracted_data': extracted_data_dict})

#     else:
#         # Handle GET request, redirect user to the upload document page
#         return render(request, 'teacher_template/adviserTeacher/upload_document.html', {'form': DocumentUploadForm()})

def upload_documents_ocr(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Replace 'YOUR_PROJECT_ID' with your Google Cloud project ID.
            project_id = '359239664082'


            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"doc-ai-ocr-b135d04e24a7.json"

            client = documentai.DocumentProcessorServiceClient()

            # Define the processor resource name.
            processor_name = f"projects/{project_id}/locations/us/processors/a2a69ba6fa1f343b"

            uploaded_file = request.FILES['document']

            # Read the document content from the uploaded file.
            content = uploaded_file.read()

            # Determine the MIME type based on the file extension.
            file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
            if file_extension in ['.pdf']:
                mime_type = "application/pdf"
            elif file_extension in ['.jpg', '.jpeg']:
                mime_type = "image/jpeg"
            else:
                # Handle unsupported file types or provide an error message.
                return render(request, 'unsupported_file_type.html')

            # Configure the processing request.
            processing_request = {
                "name": processor_name,
                "document": {"content": content, "mime_type": mime_type},
            }

            # Process the document.
            response = client.process_document(request=processing_request)

            # Access the extracted text from the document content.
            document = response.document
            text = document.text

            # Extract specific data using regular expressions
            key_phrases = {
                "REGION": r"REGION\s+(.+)",
                "DIVISION": r"DIVISION\s+(.+)",
                "SCHOOL YEAR": r"SCHOOL YEAR\s+(.+)",
                "SCHOOL NAME": r"SCHOOL NAME\s+(.+)",
                "SCHOOL ID": r"SCHOOL ID\s+(\d+)",
                "GRADE & SECTION": r"GRADE & SECTION\s+(.+)",
                "SF10-ES": r"SF10-ES\s+Page\s+\d+\s+of\s+(\d+)",  # Extract SF10-ES page number
                "LAST NAME": r"LAST NAME:\s+(.+)",
                "FIRST NAME": r"FIRST NAME:\s+(.+)",
                "MIDDLE NAME": r"MIDDLE NAME:\s+(.+)",
                "REGION": r"REGION\s+(.+)",
                "DIVISION": r"Division\s+(.+)",
                "SCHOOL YEAR": r"School Year\s+(.+)",
                "SCHOOL NAME": r"School:\s+(.+)",
                "SCHOOL ID": r"School ID\s+(\d+)",
                "NAME OF ADVISER/TEACHER": r"Name of Adviser/Teacher:\s+(.+)\s+Signature",

            }     
            
            key_value_pairs = {}

            # Iterate through the key phrases and extract the information
            for key, pattern in key_phrases.items():
                match = re.search(pattern, text)
                if match:
                    key_value_pairs[key] = match.group(1).strip()

            # Save extracted data to JSON file
            with open("extracted_data.json", "w") as json_file:
                json.dump(key_value_pairs, json_file, indent=4)

            # Assuming you create a ProcessedDocument instance
            processed_document = ProcessedDocument()
        

        # # Save the ProcessedDocument instance
        #     processed_document.save()

        #     # Create ExtractedData instance and save extracted data
        #     extracted_data_instance = ExtractedData(processed_document=processed_document)
        #     extracted_data_instance.save_extracted_data(key_value_pairs)

            # Construct the URL of the uploaded document.
            uploaded_document_path = os.path.join(settings.MEDIA_URL, str(processed_document.document))

            all_extracted_data = ExtractedData.objects.all()

       

            # Iterate through the key phrases and extract the information
            extracted_data_for_review = {}
            for key, pattern in key_phrases.items():
                match = re.search(pattern, text)
                if match:
                    extracted_data_for_review[key] = match.group(1).strip()

            # Print the extracted data for review in the console
            print("Extracted Data for Review:")
            print(extracted_data_for_review)


            # Render the 'processed_document.html' template with the extracted text and document URL.
            # return render(request, 'admin_template/edit_extracted_data.html', {'document_text': text, 'uploaded_document_url': uploaded_document_path, 'all_extracted_data': all_extracted_data,})
        return render(request, 'admin_template/edit_extracted_data.html', {'extracted_data': extracted_data_for_review, 'document_text': text, 'uploaded_document_url': uploaded_document_path, 'all_extracted_data': all_extracted_data,})
    else:
        form = DocumentUploadForm()

    return render(request, 'admin_template/upload_documents.html', {'form': form})



def save_edited_data(request):  
    if request.method == 'POST':
        # Assuming extracted_data is sent as POST data, retrieve it
        extracted_data = {
            "REGION": request.POST.get("REGION"),
            "DIVISION": request.POST.get("DIVISION"),
            "SCHOOL YEAR": request.POST.get("SCHOOL YEAR"),
            "SCHOOL NAME": request.POST.get("SCHOOL NAME"),
            "SCHOOL ID": request.POST.get("SCHOOL ID"),
            "GRADE_SECTION": request.POST.get("GRADE SECTION"),
            "LAST NAME": request.POST.get("LAST NAME", ""),  # Provide a default empty string
            "FIRST NAME": request.POST.get("FIRST NAME", ""),
            "MIDDLE NAME": request.POST.get("MIDDLE NAME", "") ,
        }

        # Create a new ProcessedDocument instance
        processed_document = ProcessedDocument.objects.create()

        # Create an ExtractedData instance and save the extracted data
        extracted_data_instance = ExtractedData(processed_document=processed_document)
        extracted_data_instance.save_extracted_data(extracted_data)

        print(extracted_data)
        # Create a custom success message
        success_message = "Data has been successfully saved!"

        # Send an HTTP response with the success message
        return HttpResponse(success_message)

    else:
        # Handle GET request if necessary
        return HttpResponse("Invalid request method")
    


def sf10_views(request):
    # Query the ExtractedData model to retrieve all records
    all_extracted_data = ExtractedData.objects.all()

    # Pass the extracted data to the template context
    context = {
        'all_extracted_data': all_extracted_data,
    }

    # Render the sf10.html template with the context data
    return render(request, 'admin_template/sf10.html', context)
