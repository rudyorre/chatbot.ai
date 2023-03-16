# Chatbot.ai

Chatbot.ai is an application that interfaces with the JPL Firesat dataset in order to provide an simpler way to query information from the database. The application is easy to use; just type in a query in one of our specified query formats, and the chatbot will do its best to return you the requested data in a readable format.

## Setup

1. Clone the repository
2. Install Docker Desktop
3. Run `git submodule init` followed by `git submodule update` to make sure you have pulled the firesat repo
4. Run the ./start.sh script to start the backend server on port 8080 and the database server on port 3030
5. Go to localhost:8080 to access the web application

# Tutorial

Our chatbot takes in a number of different query types. 

1. Query for the domain and range of a property:
"What is the domain and/or range of property_name"?  
Ex: What is the domain of "system has base unitary quantity"?    
Ex: What is the domain and range of "system has base unitary quantity"?    

<img width="543" alt="Screen Shot 2023-03-14 at 12 51 25 PM" src="https://user-images.githubusercontent.com/105709104/225120779-0e05d5d9-709f-4384-8a90-9b5732d7a255.png">

2. Query for the properties of a domain/range
"What are the properties of domain/range name?"   
Ex: What are the properties of range "general unitary quantity"?

<img width="534" alt="Screen Shot 2023-03-14 at 12 53 24 PM" src="https://user-images.githubusercontent.com/105709104/225121200-d720049c-738a-4661-bb72-5c4dc5893836.png">

3. Query for subclass/superclasses
What are the subclasses/superclasses of class_name?    
Ex: What are the superclasses of "http://bipm.org/jcgm/vim4#InherentOrdinalQuantity"?

<img width="652" alt="Screen Shot 2023-03-14 at 12 54 24 PM" src="https://user-images.githubusercontent.com/105709104/225121441-53207e49-462e-4d13-bacd-7afcf4d94fb0.png">

4. Query for mass/function of an assembly object
What is the mass and/or function of assembly object obj_id?   
Ex: What is the mass and function of assembly object id 500000?

<img width="653" alt="Screen Shot 2023-03-14 at 12 56 26 PM" src="https://user-images.githubusercontent.com/105709104/225121877-a5c35e19-60e3-4737-8dac-2971a65f7899.png">

5. Filter assembly objects
Which subjects are heavier than x and or lighter than y?    
Ex: Which subjects are heavier than 10 kg? 

<img width="653" alt="Screen Shot 2023-03-14 at 1 01 45 PM" src="https://user-images.githubusercontent.com/105709104/225122999-d6a0baed-d93b-45a2-bdcb-a33f66f2d081.png">
<img width="473" alt="Screen Shot 2023-03-14 at 1 02 19 PM" src="https://user-images.githubusercontent.com/105709104/225123133-978fa839-5b2d-4d34-b884-85a2cd4edff3.png">

6. General "What" queires
Query in the form of "What JPL_subject ... predicate?"   
Ex: What is the mission description?

<img width="656" alt="Screen Shot 2023-03-14 at 1 03 40 PM" src="https://user-images.githubusercontent.com/105709104/225123474-c32588d4-88fb-4530-b058-78957775c104.png">





