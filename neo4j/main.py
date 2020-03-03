from neo4j import GraphDatabase,Transaction
from collections import defaultdict
from collections import Counter
from itertools import groupby
from time import time
import operator
from datetime import datetime
import re

regex_unixtime = re.compile(r"\[([0-9])+\]")

def get_semester(unix_time):
    date = datetime.utcfromtimestamp(unix_time)
    month_to_semester = {
            1:1,
            0:1,
            2:2
    }
    
    print(date.month)
    semesters = date.year*2 + month_to_semester[(date.month/6)]
    return semesters

def enrolments_by_semester(enrolments):
    enrolments_semester = defaultdict(list)
    
    [enrolments_semester[enrol.get_semester()].append(enrol) for enrol in enrolments]
    
    
    
    
    
    return enrolments_semester

class ResourceAccess():
    
    
    def __init__(self,unixtime,student,resource,timesacessed_resource):
        if(type(unixtime) is not int and regex_unixtime.match(unixtime)):
            unixtime = unixtime.strip('[').strip(']')
        
        
        self.unixtime = int(unixtime)
        self.resource = resource
        self.student = student
        self.timesacessed_resource = timesacessed_resource
        
    def get_course_id(self):
        return int(self.resource['courseid'])
    
    
    def get_id_match_query(self):
        
        return f"{{resourceid : '{self.get_resource_id()}',type:'{self.get_resource_type()}' }}"
    
    def get_resource_id(self):
        return int(self.resource['resourceid'])
    
    def get_resource_type(self):
        return self.resource['type']
    
    def get_student_id(self):
        return int(self.student['userid'])
    
    def print_info(self):
        print(f"Time:{self.unixtime} student : {self.get_student_id()} course : {self.get_course_id()} resource : {self.get_resource_id()}/{self.get_resource_type()}")
    
    

        
    
    
    


class Enrolment():
    def __init__(self,enrol_date,student,course,grade = None):
        self.enrol_date = int(enrol_date)
        self.course = course
        self.student = student
        self.grade = float(grade)
        
    def get_course_id(self):
        return int(self.course['courseid'])
    
    def get_student_id(self):
        return int(self.student['userid'])
    
    def get_semester(self):
        date = datetime.utcfromtimestamp(self.enrol_date)
        month_to_semester = {
                1:2,
                0:1,
                2:2
        }
        
        semesters = date.year*2 + month_to_semester[int((date.month-1)/6)]
        return semesters
 
        
    


class Database:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()
        
    def get_people_no_wait(self):
        with self._driver.session() as session:
            session.write_transaction(self.async_tx,"match (p:Person) where p.born > 1981 return p")
            
    def parse_student_access_data_into_graph(self,session,student_id):
        query_string = f"LOAD CSV WITH HEADERS FROM 'file:///accessed.csv' AS row FIELDTERMINATOR ';'  with row  where row.userid = '{student_id}' return row.userid as userid,split(row.timeunix,\",\") as timeunix,split(row.timesaccessed,\",\") as timesaccessed,split(row.resourcesid,\",\") as resourcesid , split(row.courseid,\",\") as courseid"
    
        result = session.write_transaction(self.query_database,query_string)
        result = result.single()
        
        if(result is None or result['timeunix'] is None):
            return
        
        timesunix = [timeunix for timeunix in result['timeunix'] if timeunix ]
        timesaccessed = [times for times in result['timesaccessed'] if times]
        resourcesid = [int(resourceid) for resourceid in result['resourcesid'] if resourceid]
        coursesid = [courseid for courseid in result['courseid'] if courseid]
        
        total_timesaccessed = 0
        #print(resourcesid)
        #print(coursesid)
        
        
        
        
        for timesacessed_resource,resourceid,courseid in zip(timesaccessed,resourcesid,coursesid) :
                timesacessed_resource = int(timesacessed_resource) 
                
                timesunix_query_parameter = f"{timesunix[total_timesaccessed]}"
                timeunxix_list = timesunix[total_timesaccessed:total_timesaccessed+timesacessed_resource]
                timeunxix_list = [int(timeunix) for timeunix in timeunxix_list]
                timesaccessed = len(timeunxix_list)
                
                
                #query_string = f"MATCH (A : Student {{userid: '{student_id}'}})-[r:Accessed]->(B: Resources {{resourceid : '{resourceid}',type: 'file'}}) set r.timeunix = {timesunix_query_parameter} return r,B.courseid as courseid"
                
                query_string = f"match (A : Student {{userid: '{student_id}'}}), (B: Resources {{resourceid : '{resourceid}', courseid : '{courseid}'}}) CREATE UNIQUE (A)-[r:Accessed {{timeunix : {timeunxix_list} , timesaccessed : {timesaccessed} }}]->(B)"
                print(query_string)
                result = session.write_transaction(self.query_database,query_string)
                
                print(f"accessed student {student_id}//{resourceid}//{timeunxix_list}")
                #courseid = result.peek()['courseid']
                
                #print(f"Course id {courseid}// {resourceid}")
                
                
                #print(query_string)
                
                #if(resourceid == 32):
                    #print(resourceid)
                    #print(f"{timesunix[total_timesaccessed:total_timesaccessed+timesacessed_resource]}")
                total_timesaccessed+= timesacessed_resource
                
        #print(total_timesaccessed)         
        
        #print(len(result['resourcesid']))
        
        
        #print(f"{result['row.userid']} : \n\n{result['row.resourcesid']}\n\n {result['row.timeunix']}")
        
        #print(query_string)
        
        
        return
            
            
    def get_resource_access_ordered(self,session,course_id,student_id):
        #self.parse_student_access_data_into_graph(session,student_id)
    
        query = f"match (student:Student {{userid: '{student_id}'}})-[access:Accessed]-(resource) where resource.courseid = '{course_id}' return student,access,resource,access.timesaccessed"
    
        
        #print(f"Resource acess order of course {course_id}")
    
        result = session.write_transaction(self.query_database,query)
        
        resources_access = []
        
        
        
        
        
        for record in result:
            student = record['student']
            resource = record['resource']
            unixtimes = record['access']['timeunix']
            timesacessed_resource = record['access.timesaccessed']
            
            if(student is None and resource is None and unixtimes is None):
                continue
            
            if(type(unixtimes) is str or type(unixtimes) is int):
                unixtimes = [unixtimes]
            
            #print(f"{student_id} {unixtimes}")
                
            if(unixtimes is not None) : 
                resources_access.extend([ResourceAccess(unixtime,student,resource,timesacessed_resource) for unixtime in unixtimes])
            
        if(len(resources_access) == 0):
            return
            
            
        sorted_access = sorted(resources_access, key = lambda resource : resource.unixtime)
        
        
        unixtime_query = sorted_access[0].unixtime
        if(type(unixtime_query) is int):
            unixtime_query = [unixtime_query]
        
        
        first_resource_id_query = sorted_access[0].get_id_match_query()
        
        if(sorted_access[0].timesacessed_resource is None or sorted_access[0].timesacessed_resource == 1):
            query = f" match (student:Student {{userid :'{student_id}'}})-[access:Accessed {{timeunix : {unixtime_query}}}]-(resource: Resources {first_resource_id_query}) create (student)-[:ACCESS_ORDER {{count: 1, timedeltas : [0],userid :'{student_id}'}}]->(resource)"
        else:
            query = f" match (student:Student {{userid :'{student_id}'}})-[access:Accessed]-(resource: Resources {first_resource_id_query}) create (student)-[:ACCESS_ORDER {{count: 1, timedeltas : [0],userid :'{student_id}'}}]->(resource)"
        
        print(f"query order {query}")
        session.run(query)
        
        
        for index in range(0, len(sorted_access)-1):
            
            
            
            resource_1_id_query = sorted_access[index].get_id_match_query()
            resource_2_id_query = sorted_access[index+1].get_id_match_query()
            
            timedelta = sorted_access[index+1].unixtime -sorted_access[index].unixtime
            if(course_id == 10):
                print(timedelta)
            
            query_check_existence = f"match (resource1 : Resources {resource_1_id_query})-[r:ACCESS_ORDER {{userid :'{student_id}'}}]->(resource2 : Resources {resource_2_id_query}) return r,r.count" 
            
            result_check = session.write_transaction(self.query_database,query_check_existence)
            
            if(result_check.peek() is None):
                
                
                
                query = f"match (resource1 : Resources {resource_1_id_query}),(resource2 : Resources {resource_2_id_query})  create (resource1)-[:ACCESS_ORDER {{count: 1, timedeltas : [{timedelta}],userid :'{student_id}' }}]->(resource2)"
                #print(f"{resource_1_id_query}//{resource_2_id_query}\n")
                #print(query)
                session.run(query)
                
            else:
                
                count = int(result_check.single()['r.count']) + 1
                query_update_count = f"match (resource1 : Resources {resource_1_id_query})-[r:ACCESS_ORDER {{userid :'{student_id}'}}]->(resource2 : Resources {resource_2_id_query}) set r.count = {count} set r.timedeltas = r.timedeltas + [{timedelta}] return r" 
                #print(query_update_count)
                session.run(query_update_count)
            
            #print(sorted_access[index].get_id_match_query())
            #print(sorted_access[index+1].get_id_match_query())
            
        
        #print(len(resources_access))
        
        
        
        
        
        return sorted_access
            
    def create_simple_trajectory_graph(self,sorted_enrol):
        with self._driver.session() as session:
            student_id = sorted_enrol[0].get_student_id()
            course_id = sorted_enrol[0].get_course_id()
            grade = sorted_enrol[0].grade
            trajectory_name = f"ID: {course_id:03d}   Nota:{grade:.2f}"
            
            
            session.run("match (A)-[r:MATRICULADO]-(B) delete r")
            
            query_string = f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:MATRICULADO {{empty: ''}}]->(c) set c.trajectory_name = '{trajectory_name}' set s.trajectory_name = 'Aluno {student_id}'"
            
            #print(query_string)
            session.run(query_string)
            for index in range(0,len(sorted_enrol)-1):
                
                first_course_index = sorted_enrol[index].get_course_id()
                second_course_index = sorted_enrol[index+1].get_course_id()
                grade1 = sorted_enrol[index].grade
                trajectory1_name = f"ID: {first_course_index:03d}   Nota:{grade1:.2f}"
                
                grade2 = sorted_enrol[index+1].grade
                trajectory2_name = f"ID:{second_course_index:03d}   Nota:{grade2:.2f}"
                
                query_string = f"match (c1:Courses {{courseid : '{first_course_index}'}}),(c2:Courses {{courseid: '{second_course_index}'}}) create (c1)-[:MATRICULADO {{empty: ''}}]->(c2) set c1.trajectory_name = '{trajectory1_name}' set c2.trajectory_name = '{trajectory2_name}'"
                
                
                #print(query_string)
                session.run(query_string)
        
        
        return
    
    
    def create_by_semester_trajectory_graph(self,sorted_enrol):
        return
    
    def get_student_courses(self):
        with self._driver.session() as session:
            session.run("match (A)-[r:ACCESS_ORDER]-(B) delete r")
            session.run("match (A)-[r:MATRICULADO]-(B) delete r")
            
            
            query_string = "match (s:Student) return s.userid as student_id"
            response = session.write_transaction(self.query_database,query_string)
            
            for record in response:
                student_id = record['student_id']
                print(student_id)
                query_string = f"match (student:Student {{userid : '{student_id}'}})-[enrolment:Enrolled]-(course:Courses) return student,enrolment,course order by enrolment.enrol_date"
                response_enrol = session.write_transaction(self.query_database,query_string)
                enrolments = []
                
                for record in response_enrol:
                    enrol_date =  record['enrolment']['enrol_date']
                    enrol_grade = record['enrolment']['grade']
                    student = record['student']
                    course = record['course']
                                            
                    enrolments.append(Enrolment(enrol_date,student,course,enrol_grade))
                
                
                
           
                sorted_enrol = sorted(enrolments, key = lambda enrol : enrol.get_semester())
                course_id = sorted_enrol[0].get_course_id()
                grade = sorted_enrol[0].grade
                query_string = f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:MATRICULADO {{userid: '{student_id}',grade: '{grade}'}}]->(c)"
                session.run(query_string)
                
                for index in range(0,len(sorted_enrol)-1):
                
                    first_course_index = sorted_enrol[index].get_course_id()
                    second_course_index = sorted_enrol[index+1].get_course_id()
                    grade1 = sorted_enrol[index].grade
                    grade2 = sorted_enrol[index+1].grade
                    
                    query_string = f"match (c1:Courses {{courseid : '{first_course_index}'}}),(c2:Courses {{courseid: '{second_course_index}'}}) create (c1)-[:MATRICULADO {{userid: '{student_id}',grade: '{grade2}'}}]->(c2)"
                    session.run(query_string)
                    
                for enrol in sorted_enrol:
                    self.get_resource_access_ordered(session,course_id = enrol.get_course_id(),student_id = student_id)

    
    def get_people(self):
        with self._driver.session() as session:
            response = session.write_transaction(self.query_people)
            for record in response:
                print(record["p"])
                
    
    def async_tx(self,tx,message):
        tx.run(message)
        
    @staticmethod
    def query_courses(tx,student_id):
        return( tx.run(f"match (student:Student {{userid : '{student_id}'}})-[enrolment:Enrolled]-(course:Courses) return student,enrolment,course order by enrolment.enrol_date"))    
            
    @staticmethod
    def query_database(tx,query):
        return( tx.run(query))    

    def print_greeting(self, message):
        with self._driver.session() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, message)
            print(greeting)
            

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]
    
    
if __name__ == "__main__":
        cinted_db = Database("bolt://localhost:7687","neo4j","cinted")
        cinted_db.get_student_courses()
        #cinted_db.parse_student_access_data_into_graph(55)
        
        print("finished")
            
            
            
        cinted_db._driver.close()
