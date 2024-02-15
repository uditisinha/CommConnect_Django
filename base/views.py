from django.shortcuts import render,redirect
from urllib.parse import unquote
from django.urls import reverse
import time
# from mimetypes import guess_type
from django.http import HttpResponse,FileResponse
from .models import User, Committees, Folder, File, UserList
from .forms import MyUserCreationForm, LoginForm, UserForm, CommitteeForm, UserListForm
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import FolderForm,FileForm, UserListForm
from django.core.mail import EmailMessage
import uuid
from django.core.mail import send_mail
import os
import sys
from django.core.files.storage import FileSystemStorage
from urllib.parse import unquote
from django.core.cache import cache
# import docx
# import nltk
# import string
# import spacy
# import fitz  # PyMuPDF
# from collections import Counter

temp = 0

def extract_text_from_pdf(file):
    pdf_document = fitz.open(file)
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    return text

def process_file_keywords(file):
    # Check file type
    print("FILE NAME: ",file.name)
    file_path = os.path.join(settings.MEDIA_ROOT, file.name)
    print("FILEPATH:",file_path)
    if file.name.endswith(('.txt', '.pdf', '.docx')):
        if file.name.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file.name.endswith('.docx'):
            doc = docx.Document(file_path)
            text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            text = file.read().decode('utf-8')  # For plain text files

        # Remove stop words and filter out non-alphabetic words
        nlp = spacy.load("en_core_web_sm")
        words = nlp(text)
        stop_words = set(nlp.Defaults.stop_words)
        punctuations = set(string.punctuation)
        spaces = set(" ")
        # Filter out stop words and punctuation
        filtered_words = [word.lemma_ for word in words if word.lemma_.lower() not in stop_words and word.lemma_ not in punctuations and word.text!=" "]
    
        # Now you can use Counter on the filtered words
        word_freq = Counter(filtered_words)

        # Get the most common words
        most_common_words = [word for word, _ in word_freq.most_common(10)]  # Adjust '10' as needed

        return ', '.join(most_common_words)
    else:
        return ""
    
# Create your views here.
@login_required(login_url='login')
def home(request):
    if request.user.is_authenticated:
        user = request.user
        if request.user.is_superuser:
            committees_queryset = Committees.objects.all()
        else:
            committees_queryset = Committees.objects.exclude(
                ~Q(convener=user) & ~Q(members=user) & ~Q(staff=user)
            )

        committee_list = list(committees_queryset)

        context = {
            'committee_list': committee_list,
        }
        return render(request, "base/home.html", context)
    else:
        return redirect('login')

@login_required(login_url = 'login')
def committees_list(request): 

    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''

    selected_committees = Committees.objects.filter(
        Q(name__icontains = q) | Q(convener__pname__icontains = q)
    )

    committees = Committees.objects.all()
    context = {'committees': committees, 'selected_committees': selected_committees}
    return render(request, 'base/committees_list.html', context)

def loginuser(request):
    page = 'login'
    form = LoginForm()

    if(request.user.is_authenticated):
        return redirect('home')
    
    if (request.method == "POST"):

            email = request.POST.get('email')
            password = request.POST.get('password')

            #checks whether user exists
            try:
                email = User.objects.get(email = email)
            except:
                messages.error(request, 'User does not exist.')

            #checks for the user with given mail and password
            user = authenticate(request, email = email, password = password)

            if user != None:
                if user.is_verified:
                    login(request,user)
                    messages.success(request, 'Login Successful!')
                    return redirect('home')
                elif user.is_superuser:
                    login(request,user)
                    messages.success(request,'Login Successful, Welcome Admin!')
                    return redirect('home')
                else:
                    messages.error(request, 'Please verify your email.')
            else:
                messages.error(request,'Incorrect Password.')

    context={
        'page':page,
        'form':form
    }

    return render(request,'base/login_register.html',context)


def forgot_password(request):

    if request.user.is_authenticated:
        return redirect('home')
    
    try:
        if request.method == "POST":

            email = request.POST.get('email')

            if User.objects.filter(email = email).first():
                email_obj = User.objects.get(email = email)
                token = str(uuid.uuid4())
                user_obj = User.objects.get(email = email_obj)
                user_obj.password_token = token
                user_obj.save()
                send_forget_password_mail(email_obj, token)
                messages.success(request, 'An email is sent!')
                return redirect ('/')

            else:
                messages.error(request, 'User does not exist.')
        
    except Exception as e:
        print(e)

    return render (request, 'base/forgot_password.html')


def send_forget_password_mail(email, token):
    subject = "Your forgot password link"
    message = f"http://commconnect.pythonanywhere.com/change_password/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_change_password_mail(email, token):
    subject = "Your change password link"
    message = f"http://commconnect.pythonanywhere.com/change_password/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def change_password(request, token):
    context = {}

    try:
        if request.method == "POST":
            user_obj = User.objects.filter(password_token = token).first()
            context = {'user_id': user_obj.id}
            new_password = request.POST.get('password1')
            confirm_password = request.POST.get('password2')
            user_id = context['user_id']

            if new_password != confirm_password:
                messages.error(request, 'The passwords do not match.')
                return redirect(f'/change_password/{token}')
            
            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, 'Password changed successfully! Please login with your new password.')
            return redirect('/')

    except Exception as e:
        print(e)
        messages.error(request, 'Expired link.')
        return render (request, 'base/error.html')

    if request.user.is_authenticated:
        return render(request, 'base/change_password_loggedin.html', context)
    
    else:
        return render(request, 'base/change_password.html', context)


@login_required(login_url = 'login')
def logoutuser(request):
    logout(request)
    messages.success(request, 'Successfully Logged Out.')
    return redirect('home')


@login_required(login_url = 'login')
def edit_committee(request, pk):
    committee = Committees.objects.get(id = pk)

    if request.user not in committee.convener.all():
        if not request.user.is_superuser:
            return HttpResponse('Only the committee\'s convener can edit the committee.')
    
    form = CommitteeForm(instance = committee)
    old_name = committee.name
    if request.method == "POST":
        form = CommitteeForm(request.POST, instance = committee)
        if form.is_valid():
            media_root = str(settings.MEDIA_ROOT)
            new_name = form.cleaned_data['name']           
            print( f'{media_root}/files/{old_name}/')
            matching_files = File.objects.filter(directory__startswith=f'{media_root}\\files/{old_name}/')
            print("LENGTH OF FILE MATCHES: "+ str(len(matching_files)))
            for f in matching_files:
                old_path = f.directory
                new_path = old_path.replace(old_name,new_name,1)
                f.directory = new_path
                f.save()
            old_folder_path = os.path.join(media_root, 'files', old_name)
            new_folder_path = os.path.join(media_root, 'files', new_name)
            os.rename(old_folder_path, new_folder_path)
            form.save()

            return redirect(reverse('committee', kwargs = {'pk': pk}))
        
    context = {'form': form}
    return render(request, 'base/edit_committee.html', context)


@login_required(login_url = 'login')
def delete_committee(request, pk):
    committee = Committees.objects.get(id = pk)

    if request.user != committee.convener:
        return HttpResponse('Only the committee\'s convener can delete the committee.')
    
    if request.method == "POST":
        committee.delete()
        return redirect('committees_list')
    
    context = {'obj': committee}
    return render(request, 'base/delete.html', context)

def registeruser(request):
    form = MyUserCreationForm()
    page = 'register'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            # Check if a user with the provided email already exists
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                if not existing_user.is_verified:
                    messages.error(request, 'Email has been sent to you for verification.')

            else:
                #checks whether user exists in userlist
                try:
                    email = UserList.objects.filter(email = email).first()
                except:
                    messages.error(request, 'You are not authorized. Please contact the HOD for authorization.')
                
                if email != None:

                    user.username = username.lower()
                    user.auth_token = str(uuid.uuid4())
                    token = user.auth_token
                    user.save()

                    send_mail_for_registration(email, token)
                    messages.error(request, 'Please click on the link mailed to your email ID to verify account.')

                    return redirect('/')
                
                else:
                    messages.error(request, 'You are not authorized. Please contact the HOD for authorization.')

    context = {'form': form, 'page': page}
    return render(request, 'base/login_register.html', context)


def success(request):
    return render(request, 'base/success.html')

def sending_token(request):
    return render(request, 'base/sending_token.html')

def send_mail_for_registration(email, token):
    subject = "Your verification mail for CommConnect"
    message = f"Please click on this link to verify your email and Log in - https://commconnect.pythonanywhere.com///verify/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def verify(request, auth_token):
    try:
        user_obj = User.objects.filter(auth_token=auth_token).first()

        if user_obj:
            if user_obj.is_verified:
                messages.success(request, 'Your email is already verified.')
                return redirect('/')
            else:
                user_obj.is_verified = True
                user_obj.save()
                messages.success(request, 'Your account has been verified!')
                login(request, user_obj)
                return redirect('home')

        return redirect('error')

    except Exception as e:
        print(e)

def error(request):
    return render(request, 'base/error.html')

@login_required(login_url = 'login')
def edit_profile(request, pk):
    user = User.objects.get(id = pk)
    if request.user!=user:
        return redirect('home')
    form = UserForm(instance=user)
    if request.method == 'POST' and 'submit' in request.POST.keys():
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', pk)
    if request.method=='POST' and 'Change Password' in request.POST.keys():
        user_obj = request.user
        token = str(uuid.uuid4())
        user_obj.password_token = token
        user_obj.save()
        email_obj = request.user.email
        send_change_password_mail(email_obj, token)
        messages.success(request, 'Click on the link mailed to you to change the password.')
        return redirect ('/')
    context={
        'form':form
    }
    return render(request,'base/edit_profile.html',context)

@login_required(login_url = 'login')
def profile(request,pk):
    user = User.objects.get(id=pk)
    committees =  list(
        Committees.objects.exclude(
                ~Q(convener = user) & ~Q(members = user) & ~Q(staff = user)
            ))
    
    context={
        'committees':committees,
        'user':user
    }
    return render(request,'base/profile.html',context)

@login_required(login_url = 'login')
def comms(request, pk):
    url_dict.clear()
    committee = Committees.objects.get(id = pk)
    path = str(settings.MEDIA_ROOT) + '/files/' + committee.name + '/'
    files = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            item_url = str(settings.MEDIA_URL) + 'files/' + committee.name + '/' + item + '/'
            files.append([item,item_url])
    print(files)
    context = {'committee': committee,'folders':files}
    return render(request, 'base/comms.html', context)

@login_required(login_url='login')
def users_allowed(request):
    if request.user.is_superuser:
        users = UserList.objects.all()
        context = {'users': users}
    
        if request.method == "POST":
            form = UserListForm(request.POST)
            if form.is_valid():

                email = form['email']
                email = form.save()
                messages.success(request, 'User Added.')
                
                subject = "Access granted to use CommConnect"
                message = f"You can now register and use the features of CommConnect to manage all directories of the committees you're a part of! Check out the website at http://commconnect.pythonanywhere.com"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(subject, message, email_from, recipient_list)

                return redirect('users_allowed')
        else:
            form = UserListForm()

        context['form'] = form 
        return render(request, 'base/userlist.html', context)
    
    else:
        return redirect('home')

@login_required(login_url='login')
def create_committee(request):
    if request.method == "POST":
        form = CommitteeForm(request.POST)
        if form.is_valid():
            committee = form.save(commit=False)
            folder_name = committee.name
            path = str(settings.MEDIA_ROOT) + '/files/' + f'{folder_name}/'
            os.makedirs(path)
            new_folder = Folder()
            new_folder.name = folder_name
            new_folder.parent_directory = path
            new_folder.save() 
            committee.save()
            form.save_m2m()  # Save the many-to-many relationships
            messages.success(request, "Committee added successfully!")
            return redirect('committees_list')
    else:
        form = CommitteeForm()
    
    context = {'form': form}
    return render(request, 'base/add_committee.html', context)

@login_required(login_url = 'login')
def filesview(request,path='',filename=''):
    file_path = os.path.join(settings.MEDIA_ROOT, 'files', path, filename)
    try:
        with open(file_path, 'rb') as file:
            response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except FileNotFoundError:
        return HttpResponse('File not found', status=404)


@login_required(login_url = 'login')
def deletefile(request,pk):
    del_file = File.objects.get(id=pk)
    if request.method =='POST':
        del_file.delete()
        return redirect(settings.MEDIA_URL + 'files/')
    context={
        'obj':del_file
    }
    return render(request,'base/delete.html',context)

@login_required(login_url = 'login')
def search_files(request):
    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''
    user = request.user
    committees = Committees.objects.filter(members=user) | Committees.objects.filter(convener=user) | Committees.objects.filter(staff=user)
    filtered_files = File.objects.filter(
        (Q(name__icontains = q) | Q(keywords__icontains = q) | Q(committee__name__icontains = q) | Q(file__icontains = q))
    )
    committee_list=[]
    for c in committees:
        committee_list.append(c.name)
    bool_list=[]
    search_file_paths=[]
    for file in filtered_files:
        search_file_paths.append(str(settings.MEDIA_URL) + str(file.file))
        if str(file.committee) in committee_list:
            bool_list.append(True)
        else:
            bool_list.append(False)

    files_context = []
    for i in range(len(filtered_files)):
        files_context.append([filtered_files[i],search_file_paths[i],bool_list[i]])
    context={
        'committees':committee_list,
        'files_context':files_context,
        'search_files':filtered_files,
        'search_file_paths':search_file_paths,
    }
    return render(request,'base/searched-files.html',context)
    
url_dict = {}
@login_required(login_url = 'login')
def filestructure(request,path=''):

    delete_this_key = -1

    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''
    committee_id = None
    flag=0
    flag2=0
    user = request.user
    committee_names=[]
    user_committees = Committees.objects.filter(members=user) | Committees.objects.filter(convener=user) | Committees.objects.filter(staff=user)
    if user.is_superuser:
        user_committees = Committees.objects.all()
    for names in user_committees:
        committee_names.append(names.name)
    current_url = request.build_absolute_uri()
    base_url = request.build_absolute_uri('/')
    media_url = settings.MEDIA_URL[1:] # Get the base URL with protocol and domain
    files_url = base_url + media_url + 'files/' # Combine base URL with MEDIA_URL

    for committee in committee_names:
       url = files_url+committee
       if (url in unquote(current_url)):
           committee_id = Committees.objects.get(name=committee)
           flag=1 
    if (flag==0 and current_url!=files_url):
        flag2=1
    if(current_url!=files_url):
        parts = current_url.split('/')
        back_url = '/'.join(parts[:-2]) + '/'
    else:
        back_url = None

    updated_access_parameters = current_url.rsplit("media/",1)[1]
    updated_access_parameters = updated_access_parameters.rsplit("?q",1)[0]
    checker_for_main_file = current_url.rsplit("media/files/",1)[1]
    updated_access_parameters = unquote(updated_access_parameters)
    updated_access_parameters2 = updated_access_parameters.rsplit("files/",1)[1]

    array_url = updated_access_parameters2.rstrip('/').split('/')

    if len(array_url) == 1:
        url_dict.clear()

    var = updated_access_parameters2.replace(" ", "%20")

    for key, val in url_dict.items():
        if val[0] == var:
            delete_this_key = key

    if delete_this_key != -1:
        keys_to_delete = [key for key in url_dict.keys() if key > delete_this_key]
        for key in keys_to_delete:
            del url_dict[key]

    if all(checker_for_main_file not in values[0] for values in url_dict.values()):

        # Generate a unique ID (you can use a more sophisticated method if needed)
        unique_id = len(url_dict)
        
        parts = checker_for_main_file.rstrip('/').split('/')
        path_url = parts[-1]
        path_url = path_url.replace("%20", " ")

        url_dict[unique_id] = []
        
        url_dict[unique_id].append(checker_for_main_file)
        url_dict[unique_id].append(path_url)
            
    cleaned_checker_for_main_file = checker_for_main_file.replace("%20", " ")

    try:
        cleaned_checker_for_main_file = checker_for_main_file.replace("%20", " ")
        cleaned_checker_for_main_file = cleaned_checker_for_main_file.split("/")[0]
    except IndexError:
            cleaned_checker_for_main_file = checker_for_main_file.replace("/", "").replace("%20", " ")


    if(len(checker_for_main_file)>0):
        this_is_first_folder = '0'
    else:
        this_is_first_folder = '1'
        
    path_to = os.path.join(str(settings.MEDIA_ROOT),updated_access_parameters)
    mediaroot = settings.MEDIA_ROOT
    path_to_2 = None
    if(path_to[-1]!='/'):
        path_to_2 = path_to+'/'
    if(path_to_2!=None):
        files_to_access = File.objects.filter(Q(directory=path_to)|Q(directory=path_to_2))
    else:
        path_to_3 = path_to[:-1]
        files_to_access = File.objects.filter(Q(directory=path_to)|Q(directory=path_to_3))
    if q!='':
        current_url = current_url.rsplit("?q",1)[0]
        files_to_access = File.objects.filter(
        Q(name__icontains = q) | Q(keywords__icontains = q) | Q(committee__name__icontains = q) | Q(file__icontains = q),id__in = files_to_access)
    file_paths = []
    file_extensions = []
    i=0
    for file in files_to_access:
        file_paths.append(str(settings.MEDIA_URL) + str(file.file))
        file_extension = file_paths[i].split('.')[-1]  # Extract the extension and convert to lowercase
        file_extensions.append(file_extension)
        i+=1
    files = []
    for item in os.listdir(path_to):
        item_path = os.path.join(path_to, item)
        if os.path.isdir(item_path):
            files.append(item)
        # else:
        #     files.append(f'File: {item}')
    form = FolderForm()
    if committee_id is not None:
        form2 = FileForm(committee_id = committee_id)
    else:
        form2=FileForm()
    if request.method == "POST" and 'first_post' in request.POST.keys():
        form = FolderForm(request.POST)
        if not form.is_valid():
            # Create a mutable copy of request.POST
            post_data = request.POST.copy()
            
            # Clean and modify the form data in the copied dictionary
            post_data['parent_directory'] = os.path.join(post_data['parent_directory'], post_data['name'] + '/')
            
            # Reconstruct the form with the modified data
            form = FolderForm(post_data)
            
            # Re-validate the modified form
            if form.is_valid():
                directory = form.save(commit=False)
                os.makedirs(directory.parent_directory)
                directory.save()
                
                return redirect(current_url)
            else:
                print(form.errors)
                print("ERROR")
        else:
            if form.is_valid():
                directory = form.save(commit=False)
                directory_name = directory.name + '/'
                directory.parent_directory = os.path.join(directory.parent_directory, directory_name)
                os.makedirs(directory.parent_directory)
                directory.save()
                return redirect(current_url)
            else:
                print("ERROR")

    if request.method == "POST" and 'second_post' in request.POST.keys():
            form2 = FileForm(request.POST,request.FILES)
            if form2.is_valid():
                # Save the form to get the file_instance
                form2.save()
                # file_instance = form2.save()

                # # Keep track of the file_instance's ID
                # file_instance_id = file_instance.id
                # # Retrieve the file_instance using the ID
                # file_instance = File.objects.get(id=file_instance_id)

                # print("FILE INSTANCE KEYWORDS BEFORE: " + file_instance.keywords)
                # # Now you can access the file object and update its keywords
                # file_instance.keywords += process_file_keywords(file_instance.file)
                # print("FILE INSTANCE KEYWORDS AFTA: " + file_instance.keywords)

                # # Save the instance with updated keywords
                # file_instance.save()

                return redirect(current_url)
            else:
                print("NOT VALID")
        
    files_context=[]

    for i in range(len(file_paths)):
        files_context.append([files_to_access[i],file_paths[i],file_extensions[i]])
    
    no_of_files = len(files_context)

    if no_of_files == 1 or no_of_files == 0:
        plural = False
    
    else:
        plural = True

    context = {
        'files_context':files_context, 
        'no_of_files':no_of_files, 
        'plural': plural,
        'directory':path_to,
        'form':form,
        'check2':flag2,
        'files':files,
        'form2':form2,
        'check':this_is_first_folder,
        'files_to_access':files_to_access,
        'file_paths':file_paths,
        'current_url':current_url,
        'back_url':back_url,
        'mediaroot': mediaroot,
        'committee_names':committee_names,
        'files_url': files_url,
        'cleaned_checker_for_main_file': cleaned_checker_for_main_file,
        'updated_access_parameters2': updated_access_parameters2,
        'url_dict': url_dict,
    }
    return render(request,'base/file_structure.html',context)