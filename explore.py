import json
import psycopg2
from sql_metadata import Parser

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

def get_query_plan_visualizer(cursor, query):
    query_plan_list = []
    modified_query = f"explain (analyze,buffers,verbose, format json) {query}"
    cursor.execute(modified_query)
    plan = cursor.fetchall()
    
    plan = plan[0][0][0]
    return plan


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

# Returns all blocks from SQL query result
def get_blocks(cursor, table_names, query):
    blocks_dict = {}
    parse_query = Parser(query)
    table_alias = parse_query.tables_aliases
    #Swap key and value to usage later
    table_alias = dict((v, k) for k, v in table_alias.items())
    #print(table_alias)
    tokens = [token.value for token in parse_query.tokens]
    #print(tokens)

    select_index = find_index_case_insensitive (tokens, 'select')
    from_index = find_index_case_insensitive (tokens, 'from')
    #print(select_index, from_index)
    
    # Remove select attributes and replace it with ctid
    index_to_remove = [i for i in range(select_index+1, from_index)]
    values_to_remove = []
    for index in index_to_remove:
        values_to_remove.append(tokens[index])
    
    for values in values_to_remove:
        tokens.remove(values)

    for table in table_names:
        copy_token = tokens.copy()
        # Use alias if exists
        if table in table_alias:
            copy_token.insert(1, f"{table_alias[table]}.ctid")
        else:
            copy_token.insert(1, f"{table}.ctid")
        
        modified_query =' '.join(copy_token)
        #print(modified_query)
        cursor.execute(modified_query)
        blocks_list = cursor.fetchall()
        blocks_list = [value[0].split(',')[0] for value in blocks_list]
        blocks_list = [value.split('(')[-1] for value in blocks_list]
        
        #Eliminate duplicate blocks
        blocks_list = list(dict.fromkeys(blocks_list))
        #print(blocks_list)
        blocks_dict[table] = blocks_list
    
    return blocks_dict

# Returns contents inside of a block & tuple counts
def get_block_content(cursor, block_num, table):
    #print(block_num, table)
    query = f"SELECT ctid, * FROM {table} WHERE (ctid::text::point)[0] = {block_num};"
    cursor.execute(query)
    contents = cursor.fetchall()

    query = f'SELECT count(*) FROM {table} WHERE (ctid::text::point)[0] = {block_num};'
    cursor.execute(query)
    tuple_count = cursor.fetchall()
    tuple_count = tuple_count[0][0]
    #print(tuple_count)
    return contents, tuple_count

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
            
# Reutrns an index of a keyword regardless of case
def find_index_case_insensitive(query, keyword):
    #print(query, keyword)
    for index, key in enumerate(query):
        if key.lower() == keyword.lower():
            return index
    
    return -1