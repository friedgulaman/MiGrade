from django.shortcuts import render, redirect
from django.urls import reverse
from .models import ClassRecord, ArchivedClassRecord


def archive_class_record(request, class_record_id):
    # Retrieve the ClassRecord instance to be archived
    class_record = ClassRecord.objects.get(id=class_record_id)
    
    # Create an ArchivedClassRecord instance using the data from the ClassRecord
    ArchivedClassRecord.objects.create(
        name=class_record.name,
        grade=class_record.grade,
        section=class_record.section,
        subject=class_record.subject,
        teacher=class_record.teacher,
        quarters=class_record.quarters
    )

    # Delete the original ClassRecord instance
    class_record.delete()
    
    # Get the referer URL, which contains the original URL
    referer_url = request.META.get('HTTP_REFERER')

    if referer_url:
        # Redirect to the referer URL
        return redirect(referer_url)
    else:
        # If referer URL is not available, redirect to a default URL
        return redirect('archived_records')

def restore_archived_record(request, archived_record_id):
    # Retrieve the ArchivedClassRecord instance to be restored
    archived_record = ArchivedClassRecord.objects.get(id=archived_record_id)
    
    # Restore the archived record
    archived_record.restore()
    
    # url = reverse('student_list_for_class') + f'?grade={archived_record.grade}&section={archived_record.section}'

    # # Redirect to the constructed URL
    # return redirect(url)
    
    return redirect('archived_records')

def archived_records(request):
    archived_records = ArchivedClassRecord.objects.all()
    return render(request, 'archive_template/archived_records.html', {'archived_records': archived_records})
