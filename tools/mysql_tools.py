# 数据库工具
# 1. list_sql_tables: 列出数据库中所有可用的表，这是了解数据库结构的第一步。
# 2. get_table_data: 读取指定表的前100行数据，用于快速预览数据内容。
# 3. execute_sql_query: 执行自定义SQL查询。当需要复杂的筛选、联接或聚合时使用此工具。
import os

from mysql.connector import connect

from utils.logger_utils import logger


def get_table_config():
    config = {
        "host":os.getenv("MYSQL_HOST"),
        "port":os.getenv("MYSQL_PORT"),
        "user":os.getenv("mysql_user"),
        "password":os.getenv("mysql_password"),
        "database":os.getenv("mysql_database"),
        "charset":os.getenv("MYSQL_CHARSET","utf-8")
    }
    #过滤调config中为空的项
    config = {k:v for k,v in config.items() if v}
    #必须的key列表
    required_keys = ["user","password","database"]
    # 得到缺少的Key列表
    missing_keys = [item for item in config if item  not in required_keys]
    #如果他有值，说明缺少必须的key，抛出错误提示缺少哪些key
    if not missing_keys:
        raise ValueError(f"缺少必须的配置项:{missing_keys}")
    return config


#得到连接配置
db_config = get_table_config()
# 1. list_sql_tables: 列出数据库中所有可用的表，这是了解数据库结构的第一步。
def list_sql_tables()->str:
    """
            列出数据库中所有可用的表
        :return:   有表： 可用的表：a,b,c  没表：没有可用的表
        """
    logger.info("=====获取表名列表========")
    try:
        #链接数据库，获取链接对象
        with connect(**db_config) as conn:
            #通过连接获取游标
            with conn.cursor() as cursor:
                #通过游标执行查询表信息的sql
                cursor.execute("show tables;")
                #获取结果数据
                rows = cursor.fetchall()
                # 如果没有表，返回： “没有可用的表”
                if not rows:
                    return "没有可用的表"
                # 有表， 返回： “可用的表：a,b,c”
                # print(rows) # [('drugs',), ('inventory',), ('sales_records',)]
                table_names_str = ",".join([row[0] for row in rows])
                result = f"可用的表：{table_names_str}"
                logger.info(result)
                return result
    except Exception as e:
        return f"操作数据库失败: {str(e)}"

# 2. get_table_data: 读取指定表的前100行数据，用于快速预览数据内容。
def get_table_data(table_name):
    """
            获取指定表名的前至多100条数据列表，同时带字段名列表
            :param table_name: 表名
            :return:

             表数据
            id   name    age
            1  二狗子    18
            2  驴蛋蛋    19

            返回的结果数据： "id,name,age\n1,二狗子,18\n2,驴蛋蛋,19"
        """
    logger.info(f"======获取{table_name}表的前100行数据========")
    try:
        #链接数据库，获取链接对象
        with connect(**db_config) as conn:
            #通过连接获取游标
            with conn.cursor() as cursor:
                #通过游标执行查询表信息的sql
                cursor.execute(f"select * from {table_name} limit 100;")
                #获取结果数据
                rows = cursor.fetchall()
                # 如果没有，返回： “没有可用的数据”
                if not rows:
                    return f"{table_name}表中没有任何数据"
                # 有数据， 返回： "id,name,age\n1,二狗子,1\n2,驴蛋蛋,19"
                column_name_str = ",".join(cursor.colume_names)
                # map(str, row) 将列表中的所有元素都转换为str类型
                row_values_str = "\n".join( [",".join(map(str,row)) for row in rows])
                result = column_name_str + "\n" + row_values_str
                logger.info(f"查询{table_name}表的信息：{result}")
                return result

    except Exception as e:
        return f"操作数据库失败: {str(e)}"


# 3. execute_sql_query: 执行自定义SQL查询。当需要复杂的筛选、联接或聚合时使用此工具。
def execute_sql_query(sql:str):
    """
            根据指定sql执行，返回查询的结果
            :param sql: 由大模型生成的sql
            :return:  字段列表和数据列表的字符串
        """
    logger.info(f"======正在执行sql语句:{sql}========")
    try:
        # 链接数据库，获取链接对象
        with connect(**db_config) as conn:
            # 通过连接获取游标
            with conn.cursor() as cursor:
                # 通过游标执行查询表信息的sql
                cursor.execute(sql)
                # 获取结果数据
                rows = cursor.fetchall()
                ## 如果没有数据，返回： “xxx表中没有任何数据”
                if not rows:
                    return f"执行语句{sql}, 没有任何数据"
                # 有数据， 返回： "id,name,age\n1,二狗子,1\n2,驴蛋蛋,19"
                column_name_str = ",".join(cursor.colume_names)
                # map(str, row) 将列表中的所有元素都转换为str类型
                row_values_str = "\n".join([",".join(map(str, row)) for row in rows])
                result = column_name_str + "\n" + row_values_str
                logger.info(f"查询{sql}的数据列表：{result}")
                return result

    except Exception as e:
        return f"操作数据库失败: {str(e)}"