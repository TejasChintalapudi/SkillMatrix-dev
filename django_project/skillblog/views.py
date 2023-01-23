import os
from django.shortcuts import render
from .models import Posts , Resume
from django.http import HttpResponse
from .forms import UploadFileForm
from .resume_analyzer import ResumeAnalyzerMachine as RAM
from django.core.files.storage import default_storage



def home(request):
    context = {
        'posts': Posts.objects.all()
    }
    return render(request, 'skillblog/home.html',context)

def about(request):
    return render(request, 'skillblog/about.html',{'title': "About Page"})


def ResumeAnalyzer(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file = request.FILES['file']
        file_name = default_storage.save(file.name, file)
        ram = RAM()
        result_dict = ram.start_machine(file_name)
        employee = Resume.objects.create(resume=result_dict)
        display_result = ram.convert_list_to_string(result_dict['skillset'])
        employee = {'skillset': display_result,'total_experience':result_dict['total_experience']}
        return render(request,'skillblog/resumeanalyzer.html',{'employee': employee})
        # return HttpResponse(f"{employee.resume}--------------------- {employee.pk}")
        # return HttpResponse(f"Result dict:   {result_dict}") # and saved to Database with id {employee.pk}")
    else:
        form = UploadFileForm()
    return render(request, 'skillblog/resumeanalyzer.html',{'form': form})

