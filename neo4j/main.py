from neo4j import GraphDatabase,Transaction
from collections import defaultdict
from collections import Counter
from itertools import groupby
import operator
from datetime import datetime


def get_semester(unix_time):
    date = datetime.utcfromtimestamp(unix_time)
    month_to_semester = {
            1:1,
            0:1,
            2:2
    }
    
    semesters = date.year*2 + month_to_semester[date.month/6]
    return semesters

def enrolments_by_semester(enrolments):
    enrolments_semester = defaultdict(list)
    
    [enrolments_semester[enrol.get_semester()].append(enrol) for enrol in enrolments]
    
    
    
    
    
    return enrolments_semester


class Enrolment():
    def __init__(self,enrol_date,student,course):
        self.enrol_date = int(enrol_date)
        self.course = course
        self.student = student
    
    def get_semester(self):
        date = datetime.utcfromtimestamp(self.enrol_date)
        month_to_semester = {
                1:1,
                0:1,
                2:2
        }
        
        semesters = date.year*2 + month_to_semester[int(date.month/6)]
        return semesters
 
        
    


class Database:

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()
        
    def get_people_no_wait(self):
        with self._driver.session() as session:
            session.write_transaction(self.async_tx,"match (p:Person) where p.born > 1981 return p")
    
    def get_student_courses(self):
        with self._driver.session() as session:
            response = session.write_transaction(self.query_courses)
            #students = None
            enrolments = []
            for record in response:
                #if(student is None):
                    #student = record['student']
                
                
                enrolments.append(Enrolment(record['enrolment']['enrol_date'],record['student'],record['course']))
                #enrolments.append( (record['enrolment']['enrol_date'],record['student'],record['course']))
                
                
                
            #print(student['name'])
            #enrol_dates = enrolments.values()
            #print(enrol_dates)
            sorted_enrol = sorted(enrolments, key = lambda enrol : enrol.get_semester())
            
            
            for enrol in sorted_enrol:
                print(datetime.ctime(datetime.utcfromtimestamp(enrol.enrol_date)))
                print(enrol.get_semester())
                
            #grouped = [list(g) for k, g in groupby(L, lambda s: s.partition('_')[0])]
            grouped_enrol = [list(g) for k,g in groupby(sorted_enrol, lambda enrol : enrol.get_semester())]
                
            
            
            course_id = sorted_enrol[0].course['courseid']
            student_id = sorted_enrol[0].student['userid']
            
            first_semester_courses = [enrol.course for enrol in grouped_enrol[0]]
            for course in first_semester_courses:
                course_id = course['courseid']
                print(f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:GRADE]->(c)")
                session.run(f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:GRADE]->(c)")
            
            
            #return
            
            #print(f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:GRADE]->(c)")
            #session.run(f"match (s:Student {{userid : '{student_id}'}})-[r]-(c:Courses {{courseid: '{course_id}'}}) create (s)-[:GRADE]->(c)")
            ##session.run("match(s:Student {userid : })")
            for index in range(0,len(grouped_enrol)-1):
                print(index)
                print(f"create (m : INTERMEDIARY {{aluno : {student_id} , semestre : {grouped_enrol[index][0].get_semester()} }})")
                session.run(f"create (m : INTERMEDIARY {{aluno : {student_id} , semestre : {grouped_enrol[index][0].get_semester()} }})")
                
                
                for course in [enrol.course for enrol in grouped_enrol[index]]:
                    course_id = course['courseid']
                    
                    print(f"match (c1:Courses {{courseid : '{course_id}'}}),(m : INTERMEDIARY {{aluno : {student_id} , semestre : {grouped_enrol[index][0].get_semester()} }}) create (c1)-[:SEMESTRE]->(m)")
                    session.run(f"match (c1:Courses {{courseid : '{course_id}'}}),(m : INTERMEDIARY {{aluno : {student_id} , semestre : {grouped_enrol[index][0].get_semester()} }}) create (c1)-[:SEMESTRE]->(m)")
                    
                    
                
                print("second")
                for course in [enrol.course for enrol in grouped_enrol[index+1]]:
                    course_id = course['courseid']
                    
                    print(f"match (c2:Courses {{courseid : '{course_id}'}}),(m : INTERMEDIARY {{aluno : {student_id} , semestre : {grouped_enrol[index][0].get_semester()} }}) create (m)-[:GRADE]->(c2)")
                    session.run(f"match (c2:Courses {{courseid : '{course_id}'}}),(m : INTERMEDIARY {{aluno : {student_id} , semestre : {grouped_enrol[index][0].get_semester()} }}) create (m)-[:GRADE]->(c2)")
                
                
                #first_course_index = sorted_enrol[index][2]['courseid']
                #second_course_index = sorted_enrol[index+1][2]['courseid']
                #print(f"match (c1:Courses {{courseid : '{first_course_index}'}}),(c2:Courses {{courseid: '{second_course_index}'}}) create (c1)-[:GRADE]->(c2)")
                #session.run(f"match (c1:Courses {{courseid : '{first_course_index}'}}),(c2:Courses {{courseid: '{second_course_index}'}}) create (c1)-[:GRADE]->(c2)")
                #print(first_course_index )
                #print(second_course_index)
            return
            for enrol in enrolments[1:]:
                print(enrol[0])
            #print(courses[0].keys())
           

    
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
    def query_people(tx):
        return( tx.run("match (p:Person) where p.born > 1981 return p"))    

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
