from neo4j import GraphDatabase,Transaction




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
            student = None
            courses = []
            for record in response:
                if(student is None):
                    student = record['student']
                
                 
                courses.append(record['course'])
                
            print(student['name'])
            print(courses[0].keys())
           

    
    def get_people(self):
        with self._driver.session() as session:
            response = session.write_transaction(self.query_people)
            for record in response:
                print(record["p"])
                
    
    def async_tx(self,tx,message):
        tx.run(message)
        
    @staticmethod
    def query_courses(tx):
        return( tx.run("match (student:Student {userid : '55'})-[r]-(course:Courses) return student,course"))    
            
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
