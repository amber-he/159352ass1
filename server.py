
import _thread
import socket
import json
import pycurl
from io import BytesIO

un="19029757"
pwd="19029757"

token = 'pk_96dbba451d054ffca639a2e2c4bc24e6'
resetable="<tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr>\r\n".encode()
origintable="<tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr>\r\n".encode()

researchtable="<tr><td></td></tr>\r\n".encode()
researchlinechart="var boo=0;\r\n".encode()
drawchart="var boo=1;\r\n".encode()

def GainiexStock():
    response_buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.SSL_VERIFYPEER, False)
    curl.setopt(curl.URL, 'https://cloud.iexapis.com/stable/ref-data/symbols?token=' + token)
    curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
    curl.perform()
    curl.close()
    body = response_buffer.getvalue().decode('UTF-8')
    dic_j = json.loads(body)
    filerdic_list = []
    stocklist = []
    for i in dic_j:
        if i["type"] != "cs":
            filerdic_list.append(i)
            stocklist.append(i["symbol"])
    with open("./stock.json", 'w') as f:
        json.dump(filerdic_list, f)
        f.close()
    s=""
    origin="<option id='loaddata'></option>"
    for i in stocklist:
        news="<option>"+i+"</option>"
        s=s+news


    f  = open('./template/portfolio.html',mode='rb')
    data=f.read()
    data=data.replace(origin.encode(),s.encode())
    f.close()
    thisf= open('./template/portfolio.html',mode='wb')
    thisf.write(data)
    thisf.close()

    f2=open('./template/research.html',mode='rb')
    data2=f2.read()
    data2=data2.replace(origin.encode(),s.encode())
    f2.close()
    thisf2=open('./template/research.html',mode='wb')
    thisf2.write(data2)
    thisf2.close()

    print("Load Data successfully")


def Stringtranmission(s):

    news=s
    if "&" in s:
        news = news.replace("&", " ")
    if "%3D" in s:
        news=news.replace("%3D","=")
    if "%2B" in s:
        news=news.replace("%2B","+")
    if "%23" in s:
        news=news.replace("%23","#")
    if "%26" in s:
        news=news.replace("%26","&")
    if "%40" in s:
        news=news.replace("%40","@")
    news=news.replace("'"," ")
    return news

def Authentication(s):
    username=s.split(" ")[0]
    password=s.split(" ")[1]
    index_N=username.find("Username=")+9
    index_P=password.find("Password=")+9
    if username[index_N:]==un and password[index_P:]==pwd:
        return True
    return False

def portfoliodata(s):
    stock=s.split(" ")[0]
    quantity=s.split(" ")[1]
    price=s.split(" ")[2]
    index_S=stock.find("stock=")+6
    index_Q=quantity.find("qu=")+3
    index_P=price.find("price=")+6

    return stock[index_S:],quantity[index_Q:],price[index_P:]

def Updateportfolio():
    with open("./table.json",'r') as load_f:
        load_dict = json.load(load_f)
        load_f.close()
    start="<tr>"
    middiletable=""
    end="</tr>"
    finalend="</tr>\r\n"
    for i in range(len(load_dict)):
        s = "<td>" + load_dict[i]["symbol"] + "</td>"

        q = "<td>" + str(load_dict[i]["quantity"]) + "</td>"
        p = "<td>" + "$" + str(load_dict[i]["price"]) + "</td>"
        if i!= len(load_dict)-1:
            middiletable=middiletable+start+s+q+p+end
        else:
            middiletable=middiletable+start+s+q+p+finalend

    addtable=middiletable.encode()
    # return byte type complete table
    return addtable

def cauculation(origiononq,nowq,origionp,nowp):
    quantityresult=0
    priceresult=0
    pop=""
    quantityresult=int(origiononq)+int(nowq)
    if int(nowq)<0 and int(nowq)+int(origiononq)>0:
        priceresult=int(origionp)
    elif int(nowq)<0 and int(nowq)+int(origiononq)<0:
        pop="wrongInput"
    elif int(nowq) < 0 and int(nowq) + int(origiononq)==0:
        return 0,0,False
    else:
        priceresult=(int(origiononq)*float(origionp)+int(nowq)*float(nowp))/quantityresult
    priceresult=round(priceresult,2)
    return quantityresult,priceresult,pop=="wrongInput"

def openjson(stock,quantity,price):
    global pop
    with open("./table.json",'r') as load_f:
        load_dict=json.load(load_f)
        load_f.close()
    renewdic=[]
    condition="no_exist"
    for i in load_dict:
        if i['symbol']==stock:
            q,p,pop=cauculation(i['quantity'],quantity,i['price'],price)
            if pop:
                break
            i['quantity']=str(q)
            i['price']=str(p)
            condition="exist"
            if(q!=0):
                renewdic.append(i)
    if condition=="no_exist" and not pop:
        if int(quantity)>0 and int(price)>0:
            with open("./table.json",'w') as f:
                newstock={"symbol":stock,"quantity":str(quantity),"price":str(price)}
                renewdic.append(newstock)
                json.dump(renewdic,f)
                f.close()
        else:
            pop="wrongInput"
    elif pop:
        with open("./table.json", 'w') as f:
            json.dump(load_dict, f)
            f.close()
    else:
        with open("./table.json", 'w') as f:
            json.dump(renewdic, f)
            f.close()

def firstpage():
    try:
        f  = open('./template/index.html',mode='rb')
        data = f.read()

        f.close()
        header=("HTTP/1.1 200 OK\r\n\r\n").encode()
        body=data
    except IOError:
        header = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        body = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode()

    return header,body

def getChartinfo(symbol):
    # symbol is string
    response_buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.SSL_VERIFYPEER, False)
    curl.setopt(curl.URL, 'https://cloud.iexapis.com/stable/stock/'+symbol+'/chart/5y?chartCloseOnly=true&token='+token)
    curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
    curl.perform()
    curl.close()
    body = response_buffer.getvalue().decode('UTF-8')
    dic_j=json.loads(body)
    filerdic_list=[]
    max=round(dic_j[0]["close"],2)
    min=round(dic_j[0]["close"],2)
    year="var year=["

    xlength="var xlong="+str(len(dic_j))+";\r\n"
    fornhtmls="var data=["
    for i in range(len(dic_j)):

        if dic_j[i]["date"][0:4]!=dic_j[i-1]["date"][0:4]:
            year=year+"["+str(i)+","+dic_j[i]["date"][0:4]+"]"+","

        newdic={}
        newdic["x"]=i
        newdic["y"]=round(dic_j[i]["close"],2)
        fornhtmls=fornhtmls+"{"+"x:"+str(i)+","+"y:"+str(round(dic_j[i]["close"],2))+"}"
        if i!=len(dic_j)-1:
            fornhtmls=fornhtmls+","
        if round(dic_j[i]["close"],2)>max:
            max=newdic["y"]
        if round(dic_j[i]["close"],2)<min:
            min=newdic["y"]

        filerdic_list.append(newdic)
    fornhtmls=fornhtmls+"];\r\n"
    year = year + "+"
    year = year.replace(",+", "];\r\n")
    minmaxlength="var mmin="+str(min)+";"+"var mmax="+str(max)+";"+xlength

    return minmaxlength,year,fornhtmls

def getStockinfo(s):
    response_buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.SSL_VERIFYPEER, False)
    curl.setopt(curl.URL, 'https://cloud.iexapis.com/stable/stock/' + s + '/stats?token=' + token)
    curl.setopt(curl.WRITEFUNCTION, response_buffer.write)

    curl.perform()
    curl.close()
    body = response_buffer.getvalue().decode('UTF-8')
    start = "<tr>"
    rowstart = "<td>"
    rowend = "</td>"
    middiletable = ""
    end = "</tr>"

    dic_j=json.loads(body)
    Symbol = start + rowstart + "Symbol: " + rowend + rowstart + s + rowend + end
    companyName = start + rowstart + "Company Name:" + rowend + rowstart + str(dic_j["companyName"]) + rowend + end
    peRatio = start + rowstart + "PE ratio:" + rowend + rowstart + str(dic_j["peRatio"]) + rowend + end
    marketcap = start + rowstart + "Market capitalization:" + rowend + rowstart + str(dic_j["marketcap"]) + rowend + end
    week52high = start + rowstart + "52 week high:" + rowend + rowstart + str(dic_j["week52high"])+ rowend + end
    week52low = start + rowstart + "52 week low:" + rowend + rowstart + str(dic_j["week52low"]) + rowend + end
    newtable =  Symbol + companyName + peRatio + marketcap + week52high + week52low + "\r\n"
    newtable= newtable.encode()

    return newtable

def portfoliopage(stock,quantity,price):
    global origintable,state
    try:
        f = open('template/portfolio.html', mode='rb')
        data = f.read()
        if stock!="" and quantity!="" and price !="":
            openjson(stock,quantity,price)
            addtable = Updateportfolio()
            data=data.replace(resetable,addtable)
            origintable=addtable

        f.close()

        header = ("HTTP/1.1 200 OK\r\n\r\n").encode()
        body = data
    except IOError:
        header = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        body = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode()

    return header,body

def researchpage(stock):
    try:
        f=open('template/research.html',mode='rb')
        data=f.read()
        if stock!="":
            # addinfo is byte type
            addinfo=getStockinfo(stock)
            minmaxlength,year,htmlstr=getChartinfo(stock)
            xydata="var data=[];\r\n".encode()
            orminmaxlen="var mmin=0;var mmax=0;var xlong=0;\r\n".encode()
            oryear="var year=[];\r\n".encode()

            rexydata=htmlstr.encode()
            reminmax=minmaxlength.encode()
            reyear=year.encode()

            data=data.replace(researchtable,addinfo)
            data=data.replace(xydata,rexydata)
            data=data.replace(orminmaxlen,reminmax)
            data=data.replace(oryear,reyear)
            data=data.replace(researchlinechart,drawchart)

        f.close()

        header = ("HTTP/1.1 200 OK\r\n\r\n").encode()
        body=data
    except IOError:
        header = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        body = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode()

    return header,body

def process(client):
    global state
    message=client.recv(1024).decode()
    reheader="".encode()
    rebody="".encode()
    stock=""
    quantity=""
    price=""
    locate=message.split()[1][1:]
    if len(message)>1:
        list1 = message.split()

        if "Username=" in list1[len(list1) - 1]:
            s = Stringtranmission(list1[len(list1) - 1])
            if Authentication(s):
                state = "Authentication"
                reheader = "HTTP/1.1 200 OK\r\n\r\n".encode()
                rebody = "<html><head></head><body><h1>Sign In successfully!</h1><br><h2>try those following pages!</h2><br><h3>localhost:8080/portfolio</h3><h3>localhost:8080/research</h3></body></html>\r\n".encode()

        if state=="Signin":
            reheader,rebody=firstpage()

        if locate=="portfolio" and state=="Authentication":
            if "stock=" in list1[len(list1) - 1]:
                s2=Stringtranmission(list1[len(list1)-1])
                stock,quantity,price=portfoliodata(s2)
            reheader,rebody=portfoliopage(stock,quantity,price)
        elif locate=="research" and state=="Authentication":
            if "stocksymbol=" in list1[len(list1) - 1]:

                s2=Stringtranmission(list1[len(list1)-1])
                stock=s2.split(" ")[0]
                index_S=stock.find("stocksymbol=")+12
                stock=stock[index_S:]
            reheader,rebody=researchpage(stock)

    client.send(reheader)
    client.send(rebody)

def main():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('localhost',8080)) #监听8000端口
    sock.listen(100)
    global state
    state = "Signin"
    with open("./table.json",'w') as f:
        a=[]
        json.dump(a,f)
        f.close()

    GainiexStock()
    while True:

        connection,address = sock.accept()
        # process(connection)
        _thread.start_new_thread(process,(connection,))


if __name__ == '__main__':
    main()

