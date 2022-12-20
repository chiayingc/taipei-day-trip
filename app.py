from flask import *

from mysql.connector import Error
from mysql.connector import pooling

import json,re,jwt
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()
jwtKey="**************"


connection_pool=pooling.MySQLConnectionPool(pool_name="pynative_pool",
											pool_size=5,
											pool_reset_session=True,
											host="localhost",
											database="tpidaytrip",
											user="root",
											password="********"
											)


app=Flask(__name__,
    static_folder="static",
    static_url_path="/")
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["JSON_SORT_KEYS"] = False

# Pages
	
@app.route("/")
def index():
	return render_template("index.html")

@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")

@app.route("/booking")
def booking():
	return render_template("booking.html")

@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

# API

@app.route("/api/attractions")
def attractionsapi():
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)

		else:
			print("Error while connecting to MySQL using Connection pool",Error)

		page=request.args.get("page","0")
		page=int(page)
		count=page*12
		sql=""

		keyword=request.args.get("keyword")
		
		if keyword!=None and keyword!="": 
			keyword=re.sub("<","&lt;",keyword)
			keyword=re.sub(">","&gt;",keyword)
			sql='SELECT * FROM attractions WHERE CAT=%s OR name LIKE  %s LIMIT %s,%s'
			val=(keyword,"%"+keyword +"%",count,12)
		else:
			sql="SELECT * FROM attractions LIMIT %s,%s"
			val=(count,12)

		cursor.execute(sql,val)
		pageData=cursor.fetchall()
		for i in range(len(pageData)):
			pageData[i]=list(pageData[i])
			pageData[i][9]=json.loads(pageData[i][9])

		sql="SELECT COUNT(*) FROM attractions"
		cursor.execute(sql)
		qunt=cursor.fetchone()
		qunt=int(qunt[0])

		result={}
		result["nextpage"]=page+1
		result["data"]=[]
		
		for i in range(len(pageData)):
			result["data"].append({"id":pageData[i][0],\
							   "name":pageData[i][1],\
							   "category":pageData[i][2],\
							   "description":pageData[i][3],\
							   "address":pageData[i][4],\
							   "transport":pageData[i][5],\
							   "mrt":pageData[i][6],\
							   "lat":pageData[i][7],\
							   "lng":pageData[i][8],\
							   "images":pageData[i][9]})

		if len(pageData)<12 or (qunt-count-12)<=0:
			result["nextpage"]=None
		
		return jsonify(result),200
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500
	
	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")



@app.route("/api/attraction/<id>")
def attractionapi(id):
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)

		else:
			print("Error while connecting to MySQL using Connection pool",Error)

		attId=int(id)
		sql = "SELECT count(*) FROM attractions"
		cursor.execute(sql)
		qut=cursor.fetchone()
		qut=int(qut[0])

		if attId not in range(1,qut+1):
			result={}
			result["error"]=True
			result["message"]="景點編號不正確"
			return jsonify(result),400

		sql = "SELECT * FROM attractions WHERE id= %s"
		cursor.execute(sql, (attId,))
		attData=cursor.fetchone()
		attData=list(attData)
		attData[9]=json.loads(attData[9])

		result={}
		result["data"]={}
		result["data"]["id"]=attId
		result["data"]["name"]=attData[1]
		result["data"]["category"]=attData[2]
		result["data"]["description"]=attData[3]
		result["data"]["address"]=attData[4]
		result["data"]["transport"]=attData[5]
		result["data"]['mrt']=attData[6]
		result["data"]["lat"]=attData[7]
		result["data"]["lng"]=attData[8]
		result["data"]["images"]=attData[9]

		return jsonify(result),200
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500
	
	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")


@app.route("/api/categories")
def categories():
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)

		else:
			print("Error while connecting to MySQL using Connection pool",Error)

		sql = "SELECT DISTINCT CAT FROM attractions"
		cursor.execute(sql)
		catList=cursor.fetchall()
		for i in range(len(catList)):
			catList[i]=str(catList[i][0])

		result={}
		result["data"]=catList
		return jsonify(result),200
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500
	
	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")


@app.route("/api/user",methods=["post"])
def apiuser():
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)

			userdata=request.json
			username=userdata["username"]
			email=userdata["email"]
			password=userdata["password"]

			##檢查email是否重複
			sql="SELECT id FROM member WHERE email LIKE %s"
			cursor.execute(sql,(email,))
			result=cursor.fetchone()
			if result == None:
				encrypt_password=bcrypt.generate_password_hash(password).decode('utf-8')
				sql="INSERT INTO member(username,email,password)VALUES(%s,%s,%s)"
				val=(username,email,encrypt_password)
				cursor.execute(sql,val)
				connection_object.commit()
				# print("commited")
				result={}
				result["ok"]=True
				return jsonify(result)
			else:
				result={}
				result["error"]=True
				result["message"]="註冊失敗，重複的 Email或其他原因"
				return jsonify(result)
		else:
			print("Error while connecting to MySQL using Connection pool",Error)
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500

	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")


@app.route("/api/user/auth",methods=["GET"])
def apiuserauth_get():
	try:
		token_jwt=request.cookies.get("token")
		data=jwt.decode(token_jwt,jwtKey,algorithms="HS256")
		result={}
		result["data"]={"id":data["id"],
						"name":data["name"],
						"email":data["email"],
						}
		return jsonify(result)
	except:
		result={}
		result["data"]=None
		return jsonify(result)


@app.route("/api/user/auth",methods=["PUT"])
def apiuserauth_put():
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)

			signindata=request.json
			email=signindata["email"]
			password=signindata["password"]
			print("email:",email,"password:",password)

			##檢查email是否存在
			sql="SELECT id,username,email,password FROM member WHERE email LIKE %s"
			cursor.execute(sql,(email,))
			result=cursor.fetchone()
			print(result)
			if result == None:
				result={}
				result["error"]=True
				result["message"]="登入失敗，Email尚未註冊"
				return jsonify(result)
			else:
				#檢查密碼是否正確
				check_password=bcrypt.check_password_hash(result[3], password)

				if(check_password==True):
					encoded_jwt=jwt.encode({"id":result[0],"name":result[1],"email":result[2]},jwtKey,algorithm="HS256")
					result={}
					result["ok"]=True
					response=make_response(jsonify(result))
					response.set_cookie(key="token", value=encoded_jwt, max_age=604800)
					return response
				else:
					result={}
					result["error"]=True
					result["message"]="信箱或密碼錯誤"
					return jsonify(result),400
		else:
			print("Error while connecting to MySQL using Connection pool",Error)
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500

	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")


@app.route("/api/user/auth",methods=["DELET"])
def apiuserauth_delet():
	result={}
	result["ok"]=True
	response=make_response(jsonify(result))
	response.set_cookie(key="token", value="",max_age=-1)
	return response


app.run(host="0.0.0.0",port=3000)