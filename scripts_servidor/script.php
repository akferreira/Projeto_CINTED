<?php
function get_all_quiz($courseid) {
	global $DB;
	
	$quizesid = array();
	$quizes = $DB->get_records('moodle.quiz', array('course' => $courseid));
	foreach ($quizes as $quiz) {
   		$quizesid[] = $quiz->id;
					}

	return $quizesid;
}

function get_student_grade($courseid,$studentid) {

	global $DB;

	$studentgrades = $DB->get_record_sql('SELECT DISTINCT u.firstname,gg.id,gg.userid,gg.finalgrade,gi.courseid,gr.id AS groupid
FROM moodle.grade_grades gg
JOIN moodle.user u ON u.id = gg.userid
JOIN moodle.grade_items gi ON gi.id = gg.itemid
JOIN moodle.course c ON c.id = gi.courseid
LEFT JOIN moodle.groups gr ON gr.courseid = gi.courseid
LEFT JOIN moodle.groups_members gm ON gm.groupid = gr.id
WHERE gi.itemtype = ? AND gg.finalgrade IS NOT NULL AND gi.courseid = ? AND gg.userid = ?
ORDER BY gg.userid', array ('course',$courseid,$studentid));

	if($studentgrades->finalgrade > 10)
		$studentgrades->finalgrade = $studentgrades->finalgrade /10;
	return round($studentgrades->finalgrade,2);	
	
}

function get_all_student_course($courseid){
	
	global $DB;
	
	$students= array();
	$rolestudent = 5;
	

	$enrol = $DB->get_record('moodle.enrol', array('courseid' => $courseid, 'enrol' => "manual"));
	
	$coursestudents = $DB->get_records('moodle.user_enrolments', array('enrolid' => $enrol->id));

	foreach ($coursestudents as $student) {
		$role = $DB->get_record('moodle.role_assignments', array('userid' => $student->userid, 'roleid' => $rolestudent));
		if($role != NULL)
			$students[] = $student->userid;
					}

	return $students;

}	
function get_all_teacher_course($courseid){
	
	global $DB;
	
	$teachers= array();
	$roleteacher = 4;
	

	$enrol = $DB->get_record('moodle.enrol', array('courseid' => $courseid, 'enrol' => "manual"));
	
	$courseteachers = $DB->get_records('moodle.user_enrolments', array('enrolid' => $enrol->id));

	foreach ($courseteachers as $teacher) {
		$role = $DB->get_record('moodle.role_assignments', array('userid' => $teacher->userid, 'roleid' => $roleteacher));
		if($role != NULL)
			$teachers[] = $teacher->userid;
					}

	return $teachers;

}	


function get_all_student_course_concept ($courseid) {
	
	global $DB;
	$studentsA = array();
	$studentsB = array();
	$studentsC = array();
	$studentsD = array();
	
	$students = get_all_student_course($courseid);
	//$quizesid = get_all_quiz($courseid);
	

	foreach ($students as $student){
		$studentgrade = get_student_grade($courseid,$student);

		if($studentgrade >= 9)
			$studentsA[] = $student;
		elseif($studentgrade >= 7.5)
			$studentsB[] = $student;
		elseif($studentgrade >= 6)
			$studentsC[] = $student;
		else
			$studentsD[] = $student;
		}
	
	return array($studentsA,$studentsB,$studentsC,$studentsD);
	
		
	
}	

function file_grades (){

global $DB;
	
$myfile = fopen("grades.csv", "w") or die("Unable to open file!");
//fwrite($myfile, "userid;course;grade"."\r\n");
fwrite($myfile, "userid;course;grade;enrol_date"."\r\n");

$students = get_all_students();

foreach($students as $student){

	$enrols = $DB->get_records('moodle.enrol', array('enrol'=>'manual'));
	
	foreach($enrols as $enrol){
		$userenrol = $DB->get_record('moodle.user_enrolments', array('enrolid'=>$enrol->id,'userid'=>$student));
		
		if($userenrol != False){
			$grade=get_student_grade($enrol->courseid,$student);
			fwrite($myfile, $student.";".$enrol->courseid.";".$grade.";".$enrol->timecreated."\r\n");
					
					}
					}

	
}
}

function get_all_students(){

	global $DB;
	
	$allstudents= array();
	$rolestudent = 5;
	
	$students = $DB->get_records('moodle.role_assignments', array('roleid' => $rolestudent));
	
	
	foreach ($students as $student){
		if(!in_array($student->userid,$allstudents)){
			
			$allstudents[] = $student->userid;
			
		}
		
	}

	return $allstudents;
}

function get_all_teachers(){

	global $DB;
	
	$allteachers= array();
	$roleteacher = 4;
	
	$teachers = $DB->get_records('moodle.role_assignments', array('roleid' => $roleteacher));
	
	
	foreach ($teachers as $teacher){
		if(!in_array($teacher->userid,$allteachers)){
			
			$allteachers[] = $teacher->userid;
			
		}
		
	}

	return $allteachers;
}

function get_all_resources_course($courseid){
	
	global $DB;
	$allresources = array();

	$resources = $DB->get_records('moodle.resource', array('course' => $courseid));

	foreach ($resources as $resource){
		if(!in_array($resource->id,$allresources)){
			
			$allresources[] = $resource->id;
			
		}}

	return $allresources;
}


function file_students (){

global $DB;
	
$myfile = fopen("students.csv", "w") or die("Unable to open file!");
fwrite($myfile, "userid;name"."\r\n");

$students = get_all_students();



foreach($students as $student){
	$grades = array();
	fwrite($myfile, $student.";");

	$usuario = $DB->get_record('moodle.user', array('id'=>$student));
	fwrite($myfile, $usuario->firstname);

	
				
	
	fwrite($myfile,"\r\n");
}
}

function file_teachers (){

global $DB;
	
$myfile = fopen("teachers.csv", "w") or die("Unable to open file!");
fwrite($myfile, "userid;name"."\r\n");

$teachers = get_all_teachers();


foreach($teachers as $teacher){
	
	fwrite($myfile, $teacher.";");

	$usuario = $DB->get_record('moodle.user', array('id'=>$teacher));
	fwrite($myfile, $usuario->firstname."\r\n");

	
}


}

function file_courses (){

global $DB;
	
$myfile = fopen("courses.csv", "w") or die("Unable to open file!");
fwrite($myfile, "courseid;coursename;teachers;students;resources"."\r\n");

$courses = $DB->get_records('moodle.course', array());


foreach($courses as $course){

	if($course->id != 1)
	{
	
	fwrite($myfile, $course->id.";".$course->fullname.";");
	$teachers = get_all_teacher_course($course->id);
	
	foreach($teachers as $teacher){
		fwrite($myfile, $teacher.",");
	}
	fwrite($myfile,";");
	
	$students = get_all_student_course($course->id);
	
	foreach($students as $student){
		fwrite($myfile, $student.",");
	}
	fwrite($myfile,";");

	$resources = get_all_resources_course($course->id);
	
	foreach($resources as $resource){
		fwrite($myfile, $resource.",");
	}
	
	fwrite($myfile,"\r\n");
	
}

}
}


function file_resources (){

global $DB;
	
$myfile = fopen("resources.csv", "w") or die("Unable to open file!");
fwrite($myfile, "resourceid;name;courseid"."\r\n");

$resorces = $DB->get_records('moodle.resource', array());


foreach($resorces as $resorce){
	
	fwrite($myfile, $resorce->id.";".$resorce->name.";".$resorce->course."\r\n");
	
}
}

function file_students_course($courseid){

	global $DB;
	
	$myfile = fopen("alunos.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "alunos;courseid"."\r\n");

	$students = get_all_student_course($courseid);
	
	foreach($students as $student){
		fwrite($myfile, $student.",");
	}
	
	fwrite($myfile, ";".$courseid);
}

function file_teacher_course($courseid){

	global $DB;
	
	$myfile = fopen("professor.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "userid;courseid"."\r\n");

	$teachers = get_all_teacher_course($courseid);
	
	foreach($teachers as $teacher){
		fwrite($myfile, $teacher.",");
	}
	
	fwrite($myfile, ";".$courseid);
}

function file_students_use_resource(){
	
	global $DB;
	
	$myfile = fopen("accessed.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "userid;resourcesid;timesaccessed;timeunix;courseid;"."\r\n");
	
	$students = get_all_students();
	
	foreach($students as $student){
		
		fwrite($myfile, $student.";");
		
		
		
		$resourceinfo = get_all_resource_student($student);
		
		foreach($resourceinfo[0] as $resource){
			fwrite($myfile, $resource.",");
		}
		
		
		
		
		
		fwrite($myfile,";");
		
		foreach($resourceinfo[1] as $time){
			
				fwrite($myfile, $time.",");
			
		}
		fwrite($myfile,";");
		
		foreach($resourceinfo[2] as $timeunix){
			fwrite($myfile, $timeunix.",");
		}
		
		fwrite($myfile,";");
		
		foreach($resourceinfo[3] as $course){
			fwrite($myfile, $course.",");
		}
		fwrite($myfile,";");	
		fwrite($myfile,"\r\n");
	}
	
}


function get_all_resource_student($studentid){
	
	global $DB;
	
	$allresources = array();
	$timesaccessed = array();
	$timeunix = array();
	$courses = array();
	
	$resources = $DB->get_records('moodle.logstore_standard_log', array('objecttable'=>'resource','userid'=>$studentid));
	
	foreach ($resources as $resource){
		if(!in_array($resource->objectid,$allresources)) {
			$allresources []= $resource->objectid;
			$timesaccessed [$resource->objectid] = 1;
			$courses [] = $resource->courseid; 
		}
		else{
			$timesaccessed[$resource->objectid] = 1 + $timesaccessed[$resource->objectid];
		}
		$timeunix[] = $resource->timecreated; 
	}
	
	
	return array($allresources,$timesaccessed,$timeunix,$courses);
}

function file_user_resource_info(){

	global $DB;
	$myfile = fopen("resourceinfo.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "userid;resourcesid;timeunix"."\r\n");

	$resourceinfo = $DB->get_records_sql('SELECT DISTINCT l.timecreated,l.objecttable ,l.userid,l.objectid, r.roleid 	FROM moodle.logstore_standard_log l 
	JOIN moodle.role_assignments r 
	ON l.userid = r.userid
	WHERE objecttable = "resource" AND roleid = 5');

	

	foreach ($resourceinfo as $info){
		fwrite($myfile, $info->userid.";".$info->objectid.";".$info->timecreated."\r\n");
					}
		
	
}
	
function file_user_others_resources(){
	global $DB;
	$myfile = fopen("othersresources.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "name;courseid;resourceid;type"."\r\n");

	$choices = $DB->get_records('moodle.choice', array());
	foreach($choices as $choice)
		fwrite($myfile,$choice->name.";".$choice->course.";".$choice->id.";"."choice"."\r\n");

	$chats = $DB->get_records('moodle.chat', array());
	foreach($chats as $chat)
		fwrite($myfile,$chat->name.";".$chat->course.";".$chat->id.";"."chat"."\r\n");
	
	$urls = $DB->get_records('moodle.url', array());
	foreach($urls as $url)
		fwrite($myfile,$url->name.";".$url->course.";".$url->id.";"."url"."\r\n");

	$pages = $DB->get_records('moodle.page', array());
	foreach($pages as $page)
		fwrite($myfile,$page->name.";".$page->course.";".$page->id.";"."page"."\r\n");

	$forums = $DB->get_records('moodle.forum', array());
	foreach($forums as $forum)
		fwrite($myfile,$forum->name.";".$forum->course.";".$forum->id.";"."forum"."\r\n");

	$folders = $DB->get_records('moodle.folder', array());
	foreach($folders as $folder)
		fwrite($myfile,$folder->name.";".$folder->course.";".$folder->id.";"."folder"."\r\n");



	

}

function file_choice_info(){

	global $DB;
	$myfile = fopen("choices.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "choiceid;userid;optionid;timeunix"."\r\n");
	
	$choices = $DB->get_records('moodle.choice_answers', array());

	foreach($choices as $choice)
		fwrite($myfile,$choice->choiceid.";".$choice->userid.";".$choice->optionid.";".$choice->timemodified."\r\n");
	
	
}

function file_forum_info(){

	global $DB;
	$myfile = fopen("forums.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "forumid;discussionid;postid;courseid;userid;timeunix"."\r\n");

	$foruminfo = $DB->get_records_sql('SELECT  p.id as postid,p.discussion,p.userid,p.created,d.forum,d.course
FROM moodle.forum_posts p
JOIN moodle.forum_discussions d
ON d.id = p.discussion' );

	foreach($foruminfo as $forum)
		fwrite($myfile, $forum->forum.";".$forum->discussion.";".$forum->postid.";".$forum->course.";".$forum->userid.";".$forum->created."\r\n");

	

}

function file_chat_info(){

	global $DB;
	$myfile = fopen("chats.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "chatid;messageid;courseid;userid;timeunix"."\r\n");

	$chatinfo = $DB->get_records_sql('SELECT  m.id as messageid,m.chatid,m.userid,m.timestamp,c.id,c.course
FROM moodle.chat_messages m
JOIN moodle.chat c
ON m.chatid = c.id' );

	foreach($chatinfo as $chat)
		fwrite($myfile, $chat->chatid.";".$chat->messageid.";".$chat->course.";".$chat->userid.";".$chat->timestamp."\r\n");

	

}

function file_url_info(){

	global $DB;
	$myfile = fopen("urls.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "urlid;userid;timeunix"."\r\n");

	$urlinfo = $DB->get_records('moodle.logstore_standard_log', array('objecttable'=>'url'));


	foreach($urlinfo as $url)
		fwrite($myfile, $url->objectid.";".$url->userid.";".$url->timecreated."\r\n");

	

}

function file_page_info(){

	global $DB;
	$myfile = fopen("pages.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "pageid;userid;timeunix"."\r\n");

	$pageinfo = $DB->get_records('moodle.logstore_standard_log', array('objecttable'=>'page'));


	foreach($pageinfo as $page)
		fwrite($myfile, $page->objectid.";".$page->userid.";".$page->timecreated."\r\n");

	

}

function file_folder_info(){

	global $DB;
	$myfile = fopen("folders.csv", "w") or die("Unable to open file!");
	fwrite($myfile, "folderid;userid;timeunix"."\r\n");

	$folderinfo = $DB->get_records('moodle.logstore_standard_log', array('objecttable'=>'folder'));


	foreach($folderinfo as $folder)
		fwrite($myfile, $folder->objectid.";".$folder->userid.";".$folder->timecreated."\r\n");

	

}


define('CLI_SCRIPT', true);
require '../../var/www/moodle/config.php';

$coursetest = 9;
$studenttest = 34;


$studentgrade = get_student_grade($coursetest,$studenttest);

$studentsABCD = get_all_student_course_concept($coursetest);
var_dump($studentsABCD);

file_grades($coursetest);

file_students_use_resource();
file_resources();
file_courses ();
file_teachers ();
file_students ();
file_grades();
file_user_resource_info();

file_user_others_resources();
file_choice_info();
file_forum_info();
file_chat_info();
file_url_info();
file_page_info();
file_folder_info();
?>
