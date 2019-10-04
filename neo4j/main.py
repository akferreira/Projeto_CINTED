from neo4j import GraphDatabase,Transaction
from collections import defaultdict
from collections import Counter
from itertools import groupby
from time import time
import operator
from datetime import datetime


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
    def __init__(self,unixtime,student,resource):
        self.unixtime = int(unixtime)
        self.resource = resource
        self.student = student
        
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
            
            
    def get_resource_access_ordered(self,session,course_id,student_id):
        query = f"match (student:Student {{userid: '{student_id}'}})-[access:Accessed]-(resource) where resource.courseid = '{course_id}' return student,access,resource"
    
        print(query)
    
        result = session.write_transaction(self.query_database,query)
        
        resources_access = []
        
        
        
        
        
        for record in result:
            student = record['student']
            resource = record['resource']
            unixtimes = record['access']['timeunix']
            
            if(type(unixtimes) is str):
                unixtimes = [unixtimes]
                
            resources_access.extend([ResourceAccess(unixtime,student,resource) for unixtime in unixtimes])
            
            
    
            
            
            
        
        
        #resources_access = [ResourceAccess(unixtime = record['access']['timeunix'],student = record['student'], resource = record['resource']) for record in result]
        
        
        
        
        sorted_access = sorted(resources_access, key = lambda resource : resource.unixtime)
        
        print("sorted")
        
        session.run("match (A)-[r:ACCESS_ORDER]-(B) delete r")
        
        
        #create (s)-[:MATRICULADO {{empty: ''}}]->(c)
        
        first_resource_id_query = sorted_access[0].get_id_match_query()
        query = f" match (student:Student {{userid :'{student_id}'}})-[access:Accessed {{timeunix : '{sorted_access[0].unixtime}'}}]-(resource: Resources {first_resource_id_query}) create (student)-[:ACCESS_ORDER {{empty: ''}}]->(resource)"
        
        print(query)
        session.run(query)
        
        
        for index in range(0, len(sorted_access)-1):
            
            
            
            resource_1_id_query = sorted_access[index].get_id_match_query()
            resource_2_id_query = sorted_access[index+1].get_id_match_query()
            
            query = f"match (resource1 : Resources {resource_1_id_query}),(resource2 : Resources {resource_2_id_query})  create (resource1)-[:ACCESS_ORDER {{empty: ''}}]->(resource2)"
            print(query)
            session.run(query)
            
            #print(sorted_access[index].get_id_match_query())
            #print(sorted_access[index+1].get_id_match_query())
            
        
        print(len(resources_access))
        
        
        
        
        
        return sorted_access
            
    def create_simple_trajectory_graph(self,sorted_enrol):
        with self._driver.session() as session:
            student_id = sorted_enrol[0].get_student_id()
            course_id = sorted_enrol[0].get_course_id()
            grade = sorted_enrol[0].grade
            trajectory_name = f"ID: {course_id:03d}   Nota:{grade:.2f}"
            
            
            session.run("match (A)-[r:MATRICULADO]-(B) delete r")
            
            query_string = f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:MATRICULADO {{empty: ''}}]->(c) set c.trajectory_name = '{trajectory_name}' set s.trajectory_name = 'Aluno {student_id}'"
            
            print(query_string)
            session.run(query_string)
            for index in range(0,len(sorted_enrol)-1):
                
                first_course_index = sorted_enrol[index].get_course_id()
                second_course_index = sorted_enrol[index+1].get_course_id()
                grade1 = sorted_enrol[index].grade
                trajectory1_name = f"ID: {first_course_index:03d}   Nota:{grade1:.2f}"
                
                grade2 = sorted_enrol[index+1].grade
                trajectory2_name = f"ID:{second_course_index:03d}   Nota:{grade2:.2f}"
                
                query_string = f"match (c1:Courses {{courseid : '{first_course_index}'}}),(c2:Courses {{courseid: '{second_course_index}'}}) create (c1)-[:MATRICULADO {{empty: ''}}]->(c2) set c1.trajectory_name = '{trajectory1_name}' set c2.trajectory_name = '{trajectory2_name}'"
                
                
                print(query_string)
                session.run(query_string)
        
        
        return
    def create_by_semester_trajectory_graph(self,sorted_enrol):
        
        
        return
    
    def get_student_courses(self):
        with self._driver.session() as session:
            response = session.write_transaction(self.query_courses)
            
            self.get_resource_access_ordered(session,5,55)
            
            
            #students = None
            enrolments = []
            for record in response:
                enrol_date =  record['enrolment']['enrol_date']
                enrol_grade = record['enrolment']['grade']
                student = record['student']
                course = record['course']
                                        
                enrolments.append(Enrolment(enrol_date,student,course,enrol_grade))
                
                
                
           
            sorted_enrol = sorted(enrolments, key = lambda enrol : enrol.get_semester())
            
            
            for enrol in sorted_enrol:
                print(datetime.ctime(datetime.utcfromtimestamp(enrol.enrol_date)))
                print(enrol.get_semester())
                

            #print(enrolments_by_semester(sorted_enrol).items())
            
            
            student_id = sorted_enrol[0].get_student_id()
            course_id = sorted_enrol[0].get_course_id()
            grade = sorted_enrol[0].grade
            trajectory_name = f"ID: {course_id:03d}   Nota:{grade:.2f}"
            
            
            session.run("match (A)-[r:MATRICULADO]-(B) delete r")
            
            query_string = f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:MATRICULADO {{empty: ''}}]->(c) set c.trajectory_name = '{trajectory_name}' set s.trajectory_name = 'Aluno {student_id}'"
            
            print(query_string)
            session.run(query_string)
            #session.run(f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:GRADE]->(c)")
            #session.run("match(s:Student {userid : })")
            for index in range(0,len(sorted_enrol)-1):
                
                first_course_index = sorted_enrol[index].get_course_id()
                second_course_index = sorted_enrol[index+1].get_course_id()
                grade1 = sorted_enrol[index].grade
                trajectory1_name = f"ID: {first_course_index:03d}   Nota:{grade1:.2f}"
                
                grade2 = sorted_enrol[index+1].grade
                trajectory2_name = f"ID:{second_course_index:03d}   Nota:{grade2:.2f}"
                
                query_string = f"match (c1:Courses {{courseid : '{first_course_index}'}}),(c2:Courses {{courseid: '{second_course_index}'}}) create (c1)-[:MATRICULADO {{empty: ''}}]->(c2) set c1.trajectory_name = '{trajectory1_name}' set c2.trajectory_name = '{trajectory2_name}'"
                
                
                print(query_string)
                session.run(query_string)
           

    
    def get_people(self):
        with self._driver.session() as session:
            response = session.write_transaction(self.query_people)
            for record in response:
                print(record["p"])
                
    
    def async_tx(self,tx,message):
        tx.run(message)
        
    @staticmethod
    def query_courses(tx):
        return( tx.run("match (student:Student {userid : '55'})-[enrolment:Enrolled]-(course:Courses) return student,enrolment,course"))    
            
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
        print("finished")
            
            
            
        cinted_db._driver.close()
