# CommConnect
<p>CommConnect is a robust and user-friendly system designed for college faculties. It streamlines the retrieval and uploading of committee directories, ensuring efficient and organized management of essential documents.</p>

<h2>Technologies Used:</h2>
<ul>
  <li><strong>Website Development:</strong> Built using Django.</li>
  <li><strong>Database:</strong> SQLite.</li>
  <li><strong>Front-End:</strong> HTML, CSS, JavaScript and bootstrap.</li>
</ul>

<h2>Key Features of the Website:</h2>
<ul>
  <li><strong>File Management</strong></li>
  <ul>
    <li><strong>File Access and Download:</strong> Seamless access and download capabilities for all committee files.</li>
    <li><strong>File Upload and Deletion:</strong> Members and conveners can add and remove files within their committees.</li>
    <li><strong>Folder Creation:</strong> Members can create folders within their committees for better organization.</li>
    <li><strong>File Search:</strong> Comprehensive search functionality with keyword-based retrieval using NLP for efficient file finding.</li>
  </ul><br>
  <li><strong>Committee Management</strong></li>
  <ul>
    <li><strong>Update Committee Descriptions:</strong> Conveners can modify and update committee information.</li>
    <li><strong>Manage Committee Members:</strong> Conveners can add or remove committee members as needed.</li>
  </ul><br>
  <li><strong>Administrative Control</strong></li>
  <ul>
    <li><strong>Admin Access:</strong> The HOD can create, edit, and oversee committees and manage platform-wide files and folders.</li>
    <li><strong>Email Address Approval:</strong> The HOD approves email addresses for registration, ensuring controlled access.</li>
  </ul><br>
  <li><strong>User Profiles</strong></li>
  <ul>
    <li><strong>Profile Customization:</strong> Users can view and modify personal profiles, including providing a brief bio.</li>
    <li><strong>Committee Affiliation:</strong> Profiles display user committee memberships and convenerships.</li>
  </ul><br>
  <li><strong>User Authentication</strong></li>
  <ul>
    <li><strong>Email Verification:</strong> Secure user registration requiring email verification to ensure authorized access.</li>
  </ul><br>
  <li><strong>Password Management</strong></li>
  <ul>
    <li><strong>Password Reset:</strong> Users can reset forgotten passwords.</li>
    <li><strong>Password Modification:</strong> Users can change passwords through profile settings for enhanced security.</li>
  </ul>
</ul>

<h2>Details:</h2>
<h3>Main models or tables used:</h3>
    <li><strong>class User:</strong> Contains details about the users like email, full name, position, department, avatar. It also had the fields 'is_verified', which is used to check whether the user has verified their email, 'auth_token', which is the token that is compared to confirm that the token that user has given is correct or not and 'password_token', which is used in a similar way to 'auth_token' but it is used for changing password.</li>
    <li><strong>class Committees:</strong> Contains details about the committees like committee's name, level, convener, members, staffs, etc. The convener, members and staffs are foreign keys referencing Users.</li>
    <li><strong>class File:</strong> Apart from file name and keywords describing the file, the class contains a field called 'file' which is a FileField, a field called 'directory' which stores the name of the exact directory it is in and a field called 'committee' which is a foreign key referencing the committee it belongs to.</li>
    
<h3>Main views used:</h3>
