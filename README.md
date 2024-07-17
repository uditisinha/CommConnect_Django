# CommConnect
<p>CommConnect is a robust and user-friendly system designed for college faculties. It streamlines the retrieval and uploading of committee directories, ensuring efficient and organized management of essential documents. This system was made as an internship project under esteemed professors of K. J. Somaiya College of Engineering.</p>

<h2>Technologies Used:</h2>
<ul>
  <li><strong>Website Development:</strong> Built using Django.</li>
  <li><strong>Database:</strong> SQLite.</li>
  <li><strong>Front-End:</strong> HTML, CSS, JavaScript and bootstrap.</li>
  <li><strong>Hosting:</strong> PythonAnywhere.</li>
</ul>

<h2>Key Features of the Website:</h2>
<ul>
  <li><strong>File Management</strong></li>
  <ul>
    <li><strong>File Access and Download:</strong> Seamless access and download capabilities for all committee files.</li>
    <li><strong>File Upload and Deletion:</strong> Members and conveners can add and remove files within their committees.</li>
    <li><strong>Folder Creation:</strong> Members can create folders within their committees for better organization.</li><br>
  </ul>
  <li><strong>Committee Management</strong></li>
  <ul>
    <li><strong>Update Committee Descriptions:</strong> Conveners can modify and update committee information.</li>
    <li><strong>Manage Committee Members:</strong> Conveners can add or remove committee members as needed.</li><br>
  </ul>
  <li><strong>Administrative Control</strong></li>
  <ul>
    <li><strong>Admin Access:</strong> The HOD can create, edit, and oversee committees and manage platform-wide files and folders.</li>
    <li><strong>Email Address Approval:</strong> The HOD approves email addresses for registration, ensuring controlled access.</li><br>
  </ul>
  <li><strong>User Profiles</strong></li>
  <ul>
    <li><strong>Profile Customization:</strong> Users can view and modify personal profiles, including providing a brief bio.</li>
    <li><strong>Committee Affiliation:</strong> Profiles display user committee memberships and convenerships.</li><br>
  </ul>
  <li><strong>User Authentication</strong></li>
  <ul>
    <li><strong>Email Verification:</strong> Secure user registration requiring email verification to ensure authorized access.</li><br>
  </ul>
  <li><strong>Password Management</strong></li>
  <ul>
    <li><strong>Password Reset:</strong> Users can reset forgotten passwords.</li>
    <li><strong>Password Modification:</strong> Users can change passwords through profile settings for enhanced security.</li><br>
  </ul>
</ul>

<h2>Working demo of the project:</h2>
<video src = "https://github.com/user-attachments/assets/57e77e19-dc69-4b52-a485-f1102ef37e9f"></video>

<h2>Details (MVT format):</h2>
<h3>Models (main ones):</h3>
<ul>
    <li><strong>class User:</strong> Contains details about the users like email, full name, position, department, avatar. It also had the fields 'is_verified', which is used to check whether the user has verified their email, 'auth_token', which is the token that is compared to confirm that the token that user has given is correct or not and 'password_token', which is used in a similar way to 'auth_token' but it is used for changing password.</li><br>
    <li><strong>class Committees:</strong> Contains details about the committees like committee's name, level, convener, members, staffs, etc. The convener, members and staffs are foreign keys referencing Users.</li><br>
    <li><strong>class File:</strong> Apart from file name and keywords describing the file, the class contains a field called 'file' which is a FileField, a field called 'directory' which stores the name of the exact directory it is in and a field called 'committee' which is a foreign key referencing the committee it belongs to.</li><br>
    <li><strong>class Folder:</strong> Contains the name of the folder and the parent directory it exists in. By default this parent directory is settings.MEDIA_ROOT/files/</li>
</ul>

<h3>Views (main ones):</h3>
<ul>
    <li><strong>loginuser():</strong> User has to input their email and password for logging in. It's checked whether the user has registered or not by fetching the email using 'User.objects.get(email = email)', where User is the model name. If the fetch was unsuccessful, the user is notified that they haven't registered. If it was successful then the 'authenticate()' function is used to check if password is correct. If it is then the user gets logged in, given that they have verified their email.</li><br>
  <li><strong>registeruser():</strong> When POST request is sent it is checked whether the form is valid, if it is then it is checked whether the email has registered already. If the email is new then the user is sent a email verification mail.</li><br>
  <li><strong>create_committee():</strong> The admin is able to create committees using a form on the website. If the form is valid, a path is created using str(settings.MEDIA_ROOT) + '/files/' + f'{folder_name}/'. That path is passed into os.makedirs() to create the directory. An object of class Folder() is created, then the name and parent directory of the folder is passed to it, followed by committee.save() and folder.save(). MEDIA_ROOT is BASE_DIR / 'media' and BASE_DIR is the grandparent folder from the settings.py folder, which is the outermost folder.</li><br>
    <li><strong>filestructure():</strong> The main job of the filestructure function is to handle the folder and file uploads. If request is POST and request.POST.keys() is first_post, then the user is trying to create a folder in the present directory. If the folder form is valid, directory.parent_directory = os.path.join(directory.parent_directory, directory_name) is used to create the path to the new directory, where directory_name is the name that user inputted for the folder, os.mkdirs(directory.parent_directory) is used to create the directory and the new folder's data is saved in the model. If the request.POST.keys() is second_post, then the user is trying to upload a file to the directory they're in. FileForm(request.POST,request.FILES) is used to take the POST request and request.FILES stores the file. Upon saving of the form, the file is uploaded in file = models.FileField(max_length=20000,upload_to='cat/'). Other than handling POST requests, this function determines the access rights of user based on their status (superuser, convener, members or staff) and data for the UI.</li><br>
  <li><strong>edit_committee():</strong> This view handles the edit committee functionality. Other than overwriting previous data in the committee instance, it also handles the committee renaming functionality. Once the committee has been renamed, it has to change the parent directory name for all folders in that committee. First, the files File table is filtered using File.objects.filter(directory__startswith=f'{media_root}/files/{old_name}/'), which finds the file instances whose directory field starts with {media_root}/files/{old_name}/. It then iterates through every instance and old name with the new name and the new path is saved for that instance's directory. Then os.replace() is used to replace the older path with the newer path in the local file structure.</li><br>
  <li><strong>deletefile():</strong> Used for deleting files. When the request is POST, the instance of the File model gets deleted using the delete() function. The @receiver decorator is used which receives the pre_delete signal from class File. The file path is then used to delete the file from the system using os.remove(path).</li>
</ul>

<h3>Templates (main ones):</h3>
<ul>
  <li><strong>file_structure.html:</strong> This template file contains the whole file structure. All the folders and files inside these folders are displayed with this HTML file.</li><br>
  <li><strong>searched_files.html:</strong> This template file contains the files that the user has searched for. If user searches for "file1", all the files with "file1" in their name or keyword are displayed.</li><br>
  <li><strong>committees_list.html:</strong> This template file contains a list of all the committees that is there in the system. It also shows the user's position in that committee. Upon clicking on any committee, user is redirected to comms.html.</li><br>
  <li><strong>comms.html:</strong> In this template more details about the committee, that the user clicked on, is shown along with folders inside that committee that the user can redirect to.</li>
</ul>

<h2>Hosting on PythonAnywhere:</h2>
<p>The website is hosted on PythonAnywhere at the following link: <a href="http://uditi.pythonanywhere.com">uditi.pythonanywhere.com</a>.</p>
<p>Our system was initially built on a Windows system, so we manually constructed URLs for file locations upon uploading. However, this feature caused a "Suspicious Path Traversal" error on the hosted website because the Linux server on PythonAnywhere did not allow for manual URL construction. Therefore, we changed the path and ensured there was no manual URL construction.</p>

<h2>User diagram:</h2>
<img src="https://github.com/user-attachments/assets/e7723d2f-a024-4958-bd60-a24cc561410a"></img>

<h2>Intership Certificate:</h2>
<img src = "https://github.com/user-attachments/assets/8496e4e4-c409-4361-966b-cc6cdb95460a"></img>
