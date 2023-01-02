from flask import *

from mysql.connector import Error
from mysql.connector import pooling

import json,re,jwt
from flask_bcrypt import Bcrypt
import datetime
import requests

bcrypt=Bcrypt()
jwtKey="*********"


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
@app.route("/test")
def test():
	return render_template("test_booking.html")
	
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
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500

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
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500

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
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500

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
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500
	
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
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500
	
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


#booking

@app.route("/api/booking",methods=["GET"])
def apibooking_get():
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)
			token_jwt=request.cookies.get("token")
			if token_jwt == None:
				result={}
				result["error"]=True
				result["message"]="未登入系統，拒絕存取。"
				return jsonify(result),403
			else:
				memberData=jwt.decode(token_jwt,jwtKey,algorithms="HS256")
				memberId=memberData["id"]
				sql="SELECT attractions.id, attractions.name, attractions.address, attractions.file, booking.date, booking.time, booking.price, booking.status FROM booking INNER JOIN attractions ON attraction_id = attractions.id WHERE booking.member_id = %s"
				cursor.execute(sql,(memberId,))
				bookedData=cursor.fetchall()
				if bookedData==[]:
					result={}
					result["data"]=None
					return jsonify(result),200
					
				result={}
				result["data"]={}
				for i in range(len(bookedData)):
					images=json.loads(bookedData[i][3])
					result["data"][i]={"attraction":{"id":bookedData[i][0],"name":bookedData[i][1],"address":bookedData[i][2],"image":images[0]},"date":bookedData[i][4],"time":bookedData[i][5],"price":bookedData[i][6],"status":bookedData[i][7]}
				return jsonify(result),200

		else:
			print("Error while connecting to MySQL using Connection pool",Error)
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500
	
	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")


@app.route("/api/booking",methods=["POST"])
def apibooking_post():
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)
			token_jwt=request.cookies.get("token")
			if token_jwt == None:
				result={}
				result["error"]=True
				result["message"]="未登入系統，拒絕存取。"
				return jsonify(result),403
			else:
				try:
					booked_data=request.json
					booked_att_id=booked_data["attractionId"]
					booked_date=booked_data["date"]
					booked_time=booked_data["time"]
					booked_price=booked_data["price"]

					if booked_date=="" or booked_time=="":
						result={}
						result["error"]=True
						result["message"]="資料不完整，預定失敗"
						return jsonify(result),400
				except:
					result={}
					result["error"]=True
					result["message"]="資料不正確或其他原因，預定失敗"
					return jsonify(result),400

				memberData=jwt.decode(token_jwt,jwtKey,algorithms="HS256")
				memberId=memberData["id"]
				sql="SELECT * FROM booking WHERE member_id=%s AND attraction_id=%s AND date=%s AND time=%s"
				val=(memberId,booked_att_id,booked_date,booked_time)
				cursor.execute(sql,val)
				check_repeat=cursor.fetchone()
				if(check_repeat != None):
					result={}
					result["error"]=True
					result["message"]="重複預定"
					return jsonify(result),400

				sql="INSERT INTO booking(member_id,attraction_id,date,time,price,status)VALUES(%s,%s,%s,%s,%s,%s)"
				val=(memberId,booked_att_id,booked_date,booked_time,booked_price,"N")
				cursor.execute(sql,val)
				connection_object.commit()
				result={}
				result["ok"]=True
				return jsonify(result),200

		else:
			print("Error while connecting to MySQL using Connection pool",Error)
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500
	
	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")


@app.route("/api/booking",methods=["DELETE"])
def apibooking_delete():
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)
			token_jwt=request.cookies.get("token")
			if token_jwt == None:
				result={}
				result["error"]=True
				result["message"]="未登入系統，拒絕存取。"
				return jsonify(result),403
			else:
				memberData=jwt.decode(token_jwt,jwtKey,algorithms="HS256")
				memberId=memberData["id"]
				booked_data=request.json
				booked_att_id=booked_data["attraction_id"]
				booked_date=booked_data["date"]
				booked_time=booked_data["time"]

				sql="DELETE FROM booking WHERE member_id=%s AND attraction_id=%s AND date=%s AND time=%s"
				val=(memberId,booked_att_id,booked_date,booked_time)
				cursor.execute(sql,val)
				connection_object.commit()
				result={}
				result["ok"]=True
				return jsonify(result),200

		else:
			print("Error while connecting to MySQL using Connection pool",Error)
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500
	
	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")


#order####################################################

@app.route("/api/order",methods=["POST"])
def apiorder_post():
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)
			token_jwt=request.cookies.get("token")
			if token_jwt == None:
				result={}
				result["error"]=True
				result["message"]="未登入系統，拒絕存取。"
				return jsonify(result),403
			else:
				try:
					memberData=jwt.decode(token_jwt,jwtKey,algorithms="HS256")
				except:
					result={}
					result["error"]=True
					result["message"]="未登入系統，拒絕存取。"
					return jsonify(result),403

				try:	
					memberId=memberData["id"]
					order_data=request.json

					current_time=datetime.datetime.now()
					orderNumber=current_time.strftime("%Y%m%d%H%M%S")+str(memberId)
					status="N"

					sql="INSERT INTO `orderList` (member_id,order_no,name,email,phone,order_price,order_status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
					val=(memberId,
						 orderNumber,
						 order_data["order"]["contact"]["name"],
						 order_data["order"]["contact"]["email"],
						 order_data["order"]["contact"]["phone"],
						 order_data["order"]["price"],
						 status)
					cursor.execute(sql,val)
					connection_object.commit()

					for x in range(len(order_data["order"]["trip"])):
						sql="INSERT INTO `orderDetail` (order_no,attraction_id,attraction_name,attraction_address,attraction_image,date,time,price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
						val=(orderNumber,
							 order_data["order"]["trip"][x]["attraction"]["id"],
							 order_data["order"]["trip"][x]["attraction"]["name"],
							 order_data["order"]["trip"][x]["attraction"]["address"],
							 order_data["order"]["trip"][x]["attraction"]["image"],
							 order_data["order"]["trip"][x]["date"],
							 order_data["order"]["trip"][x]["time"],
							 order_data["order"]["trip"][x]["price"],
							 )
						cursor.execute(sql,val)
						connection_object.commit()
					
				except:
					result={}
					result["error"]=True
					result["message"]="訂單建立失敗，輸入不正確或其他原因。"
					return jsonify(result),400
				
				##付款
				# // *** 格式 ***
				# // 測試環境 URL: https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime
				# // 正式環境 URL: https://prod.tappaysdk.com/tpc/payment/pay-by-prime
				# // Header:
				# //   Content-Type: application/json
				# //   x-api-key: YourPartnerKey

				tappay_url="https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
				tappay_request_header = {
								"content-type":"application/json",
								"x-api-key":"***********"
							  	}

				tappay_request_body = {
					"prime": order_data["prime"],
					"partner_key": "*************",
					"merchant_id": "chiayingc_ESUN",
					"details":"TapPay Test",
					"amount": order_data["order"]["price"],
					"cardholder": {
						"phone_number": order_data["order"]["contact"]["phone"],
						"name": order_data["order"]["contact"]["name"],
						"email": order_data["order"]["contact"]["email"]
						}
				}

				response = requests.post(tappay_url, headers = tappay_request_header, json = tappay_request_body)
				data = response.json()

				#付款失敗
				if data["status"]!=0:
					sql="UPDATE `orderList` SET order_status = %s WHERE order_no = %s"
					val=("F",orderNumber)
					cursor.execute(sql,val)
					connection_object.commit()

					result={}
					result["error"]=True
					result["message"]="付款失敗。"
					return jsonify(result),400
				
				else:
					#付款成功
					sql="UPDATE orderList SET order_status= %s WHERE order_no= %s"
					val=("S",orderNumber)
					cursor.execute(sql,val)
					connection_object.commit()
					sql="DELETE FROM `booking` WHERE member_id = %s"
					cursor.execute(sql,(memberId,))
					connection_object.commit()

					result={}
					result["data"]={}
					result["data"]["number"]=orderNumber
					result["data"]["payment"]={}
					result["data"]["payment"]["status"]=0
					result["data"]["payment"]["message"]="付款成功"
					return jsonify(result),200
				

		else:
			print("Error while connecting to MySQL using Connection pool",Error)
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500
	
	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")


@app.route("/api/order/<ordernumber>",methods=["GET"])
def apiorder_get(ordernumber):
	try:
		connection_object=connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info=connection_object.get_server_info()
			print("Connected to MySQL database using connection pool... MySQ Server version on",db_Info)

			cursor=connection_object.cursor()
			cursor.execute("select database();")
			record=cursor.fetchone()
			print("Your connected to-",record)
			token_jwt=request.cookies.get("token")
			if token_jwt == None:
				result={}
				result["error"]=True
				result["message"]="未登入系統，拒絕存取。"
				return jsonify(result),403
			else:
				try:
					memberData=jwt.decode(token_jwt,jwtKey,algorithms="HS256")
				except:
					result={}
					result["error"]=True
					result["message"]="未登入系統，拒絕存取。"
					return jsonify(result),403

				try:	
					sql="SELECT name,email,phone,order_price,order_status FROM `orderList` WHERE order_no=%s"
					val=(ordernumber,)
					cursor.execute(sql,val)
					data_list=cursor.fetchall()
					if data_list==[]:
						result={}
						result["data"]=None
						return jsonify(result)

					name=data_list[0][0]
					email=data_list[0][1]
					phone=data_list[0][2]
					price=data_list[0][3]
					status=data_list[0][4]
					if status!="S":
						result_status=1
					else:
						result_status=0
						
					sql="SELECT attraction_id,attraction_name,attraction_address,attraction_image,date,time,price FROM `orderDetail` WHERE order_no=%s"
					val=(ordernumber,)
					cursor.execute(sql,val)
					data_deatil=cursor.fetchall()
					trips=[]
					for x in range(len(data_deatil)):
						trip = {
							"attraction":{
								"id": data_deatil[x][0],
								"name": data_deatil[x][1],
								"address": data_deatil[x][2],
								"image": data_deatil[x][3]
							},
							"date": data_deatil[x][4],
							"time": data_deatil[x][5],
							"price": data_deatil[x][6]
						}
						trips.append(trip)
					
					result={}
					result["data"]={}
					result["data"]["number"]=ordernumber
					result["data"]["price"]=price
					result["data"]["trip"]=trips
					result["data"]["contact"]={}
					result["data"]["contact"]["name"]=name
					result["data"]["contact"]["email"]=email
					result["data"]["contact"]["phone"]=phone
					return jsonify(result),200
					
				except:
					print("Error while connecting to MySQL using Connection pool",Error)
					result={}
					result["error"]=True
					result["message"]="伺服器內部錯誤"
					return jsonify(result),500
				
		else:
			print("Error while connecting to MySQL using Connection pool",Error)
			result={}
			result["error"]=True
			result["message"]="伺服器內部錯誤"
			return jsonify(result),500
	
	except:
		result={}
		result["error"]=True
		result["message"]="伺服器內部錯誤"
		return jsonify(result),500
	
	finally:
		cursor.close()
		connection_object.close()
		print("connection closed.")

app.run(host="0.0.0.0",port=3000)
