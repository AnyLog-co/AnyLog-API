# The following code 
# Stop processes 
exit mqtt 
exit operator 


# remove from blockchain 
run client (!master_node) blockchain drop by host !ip 
run client (!master_node) blockchain pull to json !!blockchain_file 
run client (!master_node) file get !!blockchain_file !blockchain_file 

# Drop database 
disconnect dbms !default_dbms 
if !db_type == "psql" then connect dbms psql !db_user !db_port postgres 
drop dbms !default_dbms from !db_type
if !db_type == "psql" then disconnect dbms postgres  

exit 
