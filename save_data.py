# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import session


from mysql.connector import Error
from mysql.connector import pooling

import json

try:
    connection_pool=pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                                pool_size=5,
                                                pool_reset_session=True,
                                                host="localhost",
                                                database="tpidaytrip",
                                                user="root",
                                                password="meowmeow"
                                                )
    connection_object=connection_pool.get_connection()

    if connection_object.is_connected():
        db_Info=connection_object.get_server_info()
        print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

    cursor=connection_object.cursor()
    cursor.execute("select database();")
    record=cursor.fetchone()
    print("Your connected to-",record)

    sql = "CREATE TABLE attractions(id INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(50) NOT NULL,CAT VARCHAR(20) NOT NULL,description VARCHAR(3500),address VARCHAR(100) NOT NULL,direction VARCHAR(1000) NOT NULL,MRT VARCHAR(10),latitude FLOAT(8,6),longitude FLOAT (9,6),file JSON NOT NULL,rate INT NOT NULL,date VARCHAR(10) NOT NULL,SERIAL_NO VARCHAR(40) NOT NULL,Idpt VARCHAR(10) NOT NULL,MEMO_TIME VARCHAR(600),`RowNumber` INT,REF_WP INT NOT NULL,langinfo INT NOT NULL,POI VARCHAR(5) NOT NULL,avBegin VARCHAR(10) NOT NULL,avEnd VARCHAR(10) NOT NULL);"
    cursor.execute(sql)
    connection_object.commit()
    print("create Table 'attrations' successed! ")

    with open("./data/taipei-attractions.json",mode="r",encoding="utf-8")as file:
        data=json.load(file)

    for i in range(len(data["result"]["results"])):
        files=data["result"]["results"][i]["file"].split('http')
        itemPics=[]    
        for j in range(len(files)):
            if files[j][-3:].upper()=="JPG"  or files[j][-3:].upper=="PNG" :
                itemPics=itemPics+["http"+files[j]]
        data["result"]["results"][i]["file"]=""
        data["result"]["results"][i]["file"]=json.dumps(data["result"]["results"][i]["file"])
        data["result"]["results"][i]["file"]=json.dumps(itemPics)

        name=data["result"]["results"][i]["name"]
        cat=data["result"]["results"][i]["CAT"]
        desc=data["result"]["results"][i]["description"]
        address=data["result"]["results"][i]["address"]
        dirt=data["result"]["results"][i]["direction"]
        mrt=data["result"]["results"][i]["MRT"]
        latitude=data["result"]["results"][i]["latitude"]
        longitude=data["result"]["results"][i]["longitude"]
        rate=data["result"]["results"][i]["rate"]
        date=data["result"]["results"][i]["date"]
        serialNo=data["result"]["results"][i]["SERIAL_NO"]
        idpt=data["result"]["results"][i]["idpt"]
        memoTime=data["result"]["results"][i]["MEMO_TIME"]
        rownum=data["result"]["results"][i]["RowNumber"]
        refWp=data["result"]["results"][i]["REF_WP"]
        langinfo=data["result"]["results"][i]["langinfo"]
        poi=data["result"]["results"][i]["POI"]
        avB=data["result"]["results"][i]["avBegin"]
        avE=data["result"]["results"][i]["avEnd"]
        images=data["result"]["results"][i]["file"]

        sql = "INSERT INTO attractions(`name`,`CAT`,`description`,`address`,`direction`,`MRT`,`latitude`,`longitude`,`file`,`rate`,`date`,`SERIAL_NO`,`idpt`,`MEMO_TIME`,`RowNumber`,`REF_WP`,`langinfo`,`POI`,`avBegin`,`avEnd`)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        val = (name,cat,desc,address,dirt,mrt,latitude,longitude,images,rate,date,serialNo,idpt,memoTime,rownum,refWp,langinfo,poi,avB,avE)
        cursor.execute(sql, val)
        connection_object.commit()
    print("data inserted!")


except Error as e:
    print("Error while connecting to MySQL using Connection pool",e)

finally:
    if connection_object.is_connected():
        cursor.close()
        connection_object.close()
        print("MySQL connection is closed")






