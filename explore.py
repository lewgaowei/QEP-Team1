import json
import psycopg2

# Load database credentials from JSON file
with open('db_config.json') as json_file:
    db_credentials = json.load(json_file)


# Connect to database and return a cursor
def connect_to_db():
    try:
        db_connection = psycopg2.connect(
            host=db_credentials['host'],
            dbname=db_credentials['db_name'],
            user=db_credentials['user'],
            password=db_credentials['password'],
        )
        cursor = db_connection.cursor()
        return db_connection, cursor
    
    except psycopg2.OperationalError as e:
        return False, False


# Close connection
def close_db_connection(db_connection, cursor):
    cursor.close()
    db_connection.close()

# Return Query Execution Plan
def get_query_plan(cursor, query):
    query_plan_list = []
    modified_query = f"EXPLAIN (FORMAT JSON) {query}"
    cursor.execute(modified_query)
    plan = cursor.fetchall()
    recursive_plan_processor(plan[0][0][0], query_plan_list)
    return query_plan_list


# Return Block/Buffer Hits
def get_buffer_hits(cursor, query):
    buffer_hit_list=[]
    save_buffer_hit_count_flag = False
    query_plan_list = []
    modified_query = f"EXPLAIN (FORMAT JSON, analyze, buffers, costs off) {query}"
    cursor.execute(modified_query)
    plan = cursor.fetchall()
    recursive_plan_processor(plan[0][0][0], query_plan_list)
    for plan in query_plan_list:
        if isinstance(plan, dict):
            for key, value in plan.items():
                if key == 'Node Type':
                    save_buffer_hit_count_flag = True
                if key == 'Shared Hit Blocks' and save_buffer_hit_count_flag:
                    #print(key, value)
                    buffer_hit_list.append({key : value})
                    save_buffer_hit_count_flag = False
    
    return buffer_hit_list

# return a block size of database
def get_block_size(cursor):
   cursor.execute('show block_size;')
   return cursor.fetchall()[0][0]


######################
## Helper Functions ##
######################

# recursively extract key-vlaue pairs from a query plan and add to the list
def recursive_plan_processor(qplan, result_list):
    #print("recursive is called^^^^^^^^^^^^^^^^^")
    #print(f'type of {type(qplan)}')
    #print(qplan)
    if isinstance(qplan, list):
        for item in qplan:
            recursive_plan_processor(item, result_list)
    else:
        for key, value in qplan.items():
            if isinstance(value, dict) or isinstance(value, list):
                recursive_plan_processor(value, result_list)
            else:
                #print(f"{key} : {value}")
                result_list.append({key : value})
            
