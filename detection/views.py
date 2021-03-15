from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Client , Medical_Record
from django.urls import reverse
from django.http import HttpResponseRedirect , HttpResponse
from django.contrib.auth import authenticate , logout , login as d_login
from django.views import View
import qrcode
from PIL import Image
import json
from django.conf import settings
import requests
from geopy.geocoders import Nominatim
from tensorflow.keras import models
from base64 import b64encode 
import cv2 as cv
# from keras.preprocessing.image import img_to_array  , load_img , ImageDataGenerator
# import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from skimage import transform
# from django.contrib.gis.geoip2 import GeoIP2
import time
import json
from pyzbar.pyzbar import decode

# Create your views here.
model = models.load_model('wound_aug.h5')
def Signup(request):
    if request.method == 'POST':
        res = request.POST
        myfile = request.FILES.get('profile' , False)
        print(myfile)
        try:
            user= User.objects.get(username=res['username'])
        except:
            user = None    
        print(user)
        if user is  None:
            user =  User.objects.create(username = res['username'] , password = res['password'] , email = res['email'])
            print(user)
            user.save()
            print(myfile)
            Client_instance  = Client(user=user , email = res['email'] , fullname=res['fullname'] , age=res['age'] , personal_contact=res['pcontact'] ,relative_contact = res['rcontact'] , address = res['address'] , blood_group = res['bgroup'] ,image=myfile)
            Client_instance.save()
            d_login(request , user)
            return HttpResponseRedirect(reverse('Dashboard'))
        else:
            return render(request , 'detection/signup.html' , {'message':'User Already Exist'})
    return render(request , 'detection/signup.html' , {'message':''})

def Profile_View(request):
    if request.user.is_authenticated:
        cl = Client.objects.get(user = request.user)
        return render(request , 'detection/profile.html' , {'user':cl })
    else:
        return HttpResponseRedirect('/login')    



def Edit_Profile(request):
    if request.user.is_authenticated:
        cl = Client.objects.get(user = request.user)
        if request.method == 'POST':
            res = request.POST
            user = request.user
            myfile = request.FILES.get('profile' , False)
            print(myfile)
            if myfile == False:
                myfile = cl.image
            cl.fullname = res['fullname']
            cl.age = res['age']
            cl.personal_contact = res['pcontact']
            cl.relative_contact = res['rcontact']
            cl.email = res['email']
            cl.address = res['address']
            cl.blood_group = res['bgroup']
            cl.image = myfile
            cl.save()
            return render(request , 'detection/profile.html' , {'user':cl})

        return render(request , 'detection/edit_profile.html' , {'user':cl})
    else:
        return HttpResponseRedirect('/login')  


def Login(request):
    # g = GeoIP2()
    # print(g.city('192.168.42.48'))
    if request.method == 'POST':
        res = request.POST
        user = authenticate(username = res['username'] , password = res['password'])
        print(user , res)
        if user is not None:
            d_login(request , user)
            return HttpResponseRedirect(reverse('Dashboard'))
        else:
            return render(request , 'detection/login.html' , {'message':'Invalid Username Or Password'}) 
    return render(request , 'detection/login.html' , {'message':''})    


def Dashboard(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            res = request.POST
            print(res)
            myfile = request.FILES.get('report_3' , False)
            print(myfile)
            cl = Client.objects.get(user = request.user)
            rp = Medical_Record(title=res['Name'], image = myfile , date = res['date']  , amount = res['Value'], description = res['description'] , hospital = res['hos_name'] ,client = cl )
            rp.save()
            All_report = Medical_Record.objects.filter(client = cl)
            Report =[]
            for report in All_report:
                Report.append(report)
            return render(request , 'detection/dashboard.html' ,  {'user':cl , 'Report':Report})
        else:
            cl = Client.objects.get(user = request.user)
            All_report = Medical_Record.objects.filter(client = cl)
            Report =[]
            for report in All_report:
                Report.append(report)
            return render(request , 'detection/dashboard.html' , {'user':cl , 'Report':Report})
    else:
        return HttpResponseRedirect('/login')        

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/login')


def Prediction(request):
    if request.user.is_authenticated:
        cl = Client.objects.get(user = request.user)
        All_report = Medical_Record.objects.filter(client = cl)
        mes = "None"
        if request.method == 'POST':
            print(request.POST)
            file = request.FILES.get('myfile' , False)
            if file == False:
                mes = "None"
                return render(request , 'detection/predict.html' ,  {'user':cl , 'prediction':mes})
            inImg = request.FILES["myfile"].read()
            encoded = b64encode(inImg).decode('ascii')
            mime = "image/jpg"
            mime = mime + ";" if mime else ";"
            input_image = "data:%sbase64,%s" % (mime, encoded)
            # print(input_image , "%55555%%%%%%%%%%%%%555555")
            np_image = Image.open(file)
            np_image = np.array(np_image).astype('float32')/255
            np_image = transform.resize(np_image, (150, 150, 3))
            np_image = np.expand_dims(np_image, axis=0)
            print(np_image.shape)
            p = model.predict(np_image)  
            mes = "None"
            if p > 0.5:
                mes = "Severe"
            else:
                mes = "Non_Severe"    
            print(p)
            time.sleep(1)
            return render(request , 'detection/predict.html' ,  {'user':cl , 'prediction':mes , "input_image": input_image})
    
        
        return render(request , 'detection/predict.html' ,  {'user':cl , 'prediction':mes})
    else:
            return HttpResponseRedirect('/login') 


def View_Report(request , id):
    if request.user.is_authenticated:
        cl = Client.objects.get(user = request.user)
        report =Medical_Record.objects.get(id = id , client=cl)
        print(report)
        return render(request , 'detection/view_report.html' ,  {'user':cl , 'report':report})
    else:
        return HttpResponseRedirect('/login') 

def Delete_Report(request , id):
    cl = Client.objects.get(user = request.user)
    report =Medical_Record.objects.get(id = id , client=cl)
    report.delete()
    return HttpResponseRedirect('/dashboard')




def Edit_Report(request , id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            cl = Client.objects.get(user = request.user)
            report =Medical_Record.objects.get(id = id , client=cl)
            res = request.POST
            if res['date'] == '':
                date =  report.date  
            else:
                date = res['date']      
            myfile = request.FILES.get('report_pic' , False)
            print(myfile)
            if myfile == False:
                myfile= report.image
            # Uodate all 
            report = Medical_Record.objects.get(id = id , client = cl)
            # update(title=res['Name'], image = myfile , date = date , amount = res['Value'], description = res['description'] , hospital = res['hos_name'])
            report.image = myfile
            report.title = res['Name']
            report.amount = res['Value']
            report.description = res['description']
            report.hospital = res['hos_name']
            report.save()
            return HttpResponseRedirect('/view_report/'+str(id))
        cl = Client.objects.get(user = request.user)
        report =Medical_Record.objects.get(id = id , client=cl)
        return render(request , 'detection/update_report.html' ,  {'user':cl , 'report':report})
    else:
        return HttpResponseRedirect('/login') 



def GenerateQr(request):
    if request.user.is_authenticated:
        user = Client.objects.get(user = request.user)
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=6,
        )
        data = {
            'Name':user.fullname,
            'Email':user.email,
            'Age':user.age,
            'Relative_Contact':user.relative_contact,
            'Phone':user.personal_contact,
            'Blood_Group':user.blood_group,
            'Address':user.address,
        }
        details = json.dumps(data)
        print(details)

        qr.add_data(details)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        filename = str(request.user) + '.png'

        img.save(str(settings.MEDIA_ROOT)+str('/qrcode_pic/')+str(filename))
        # img.save('save.png')
        # return HttpResponse("ds")
        return HttpResponseRedirect('qrcode_pic/'+str(filename))
    else:
        return HttpResponseRedirect('/login') 


def Decode_qr(request):
    if request.user.is_authenticated:
        cl = Client.objects.get(user = request.user)
    
        if request.method == 'POST':
            print(request.POST)
            file = request.FILES.get('myfile' , False)
            print(file)
            if file == False:
                return render(request , 'detection/decode.html' ,  {'user':cl})


            np_image = Image.open(file)
            print(file)
            
            c = decode(Image.open(file))
            data = c[0].data
            y  = json.loads(data)

            print(data , type(data) , y)
        
            return render(request , 'detection/decode.html' ,  {'user':cl , 'detail':y})
        return render(request , 'detection/decode.html' ,  {'user':cl})
    else:
        return HttpResponseRedirect('/login') 

def view_map(request):
    return render(request , 'detection/view_map.html')


def Medical(request):
    if request.user.is_authenticated:

        cl = Client.objects.get(user = request.user)
        if request.method == 'POST':
            print(request.POST)
            res = request.POST
            address = res['address']
            geolocator = Nominatim(user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0")
            location = geolocator.geocode(address)
            if location == None:
                message = "Please add Proper address (Place Name , City , State )"
                return render(request , 'detection/near_by.html' , {'user':cl , 'mes':message})    
            lat = location.latitude
            lng = location.longitude
            url ="https://discover.search.hereapi.com/v1/discover"
            apikey='izgWHNR9NrmVLDKm7HzZlCLT5zE6Qb7Y-XWQCKA23pE'
            query='medicals' #hospitals
            PARAMS = {
                        'apikey':apikey,
                        'q':query,
                        'limit': 5,
                        'at':'{},{}'.format(lat,lng)
                    } 
            r = requests.get(url = url, params = PARAMS) 
            data = r.json()
            y = data['items']
            
            # print(y)
            tittle = []
            address =[]
            loc = []
            for x  in y:
                tittle.append(x['title'])
                address.append( x['address']['label'])
                url = "https://www.google.com/maps/dir/?api=1&origin="+str(lat)+","+str(lng) +"&destination="+str(x['access'][0]['lat'])+","+str(x['access'][0]['lng'])
                loc.append(url)
                # print(url)
                # print(x['title'] , x['address']['label'] , x['access'])
            
            return render(request , 'detection/near_by.html' , {'user':cl , 'detail':zip(tittle , address , loc)}) 
        return render(request , 'detection/near_by.html'  ,{'user':cl})    
    else:
        return HttpResponseRedirect('/login')   

def Hospital(request):
    if request.user.is_authenticated:
        cl = Client.objects.get(user = request.user)
        if request.method == 'POST':
            print(request.POST)
            res = request.POST
            address = res['address']
            geolocator = Nominatim(user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0")
            location = geolocator.geocode(address)
            if location == None:
                message = "Please add Proper address (Place Name , City , State )"
                return render(request , 'detection/near_by.html' , {'user':cl , 'mes':message})    
            lat = location.latitude
            lng = location.longitude
            url ="https://discover.search.hereapi.com/v1/discover"
            apikey='izgWHNR9NrmVLDKm7HzZlCLT5zE6Qb7Y-XWQCKA23pE'
            query='hospitals' #hospitals
            PARAMS = {
                        'apikey':apikey,
                        'q':query,
                        'limit': 5,
                        'at':'{},{}'.format(lat,lng)
                    } 
            r = requests.get(url = url, params = PARAMS) 
            data = r.json()
            y = data['items']
            # print(y)
            tittle = []
            address =[]
            loc = []
            for x  in y:
                tittle.append(x['title'])
                address.append( x['address']['label'])
                url = "https://www.google.com/maps/dir/?api=1&origin="+str(lat)+","+str(lng) +"&destination="+str(x['access'][0]['lat'])+","+str(x['access'][0]['lng'])
                loc.append(url)
                # print(url)
                # print(x['title'] , x['address']['label'] , x['access'])
            
            return render(request , 'detection/near_by.html' , {'user':cl , 'detail':zip(tittle , address , loc)})  
        return render(request , 'detection/near_by.html' , {'user':cl})        
    else:
        return HttpResponseRedirect('/login')   




# https://www.google.com/maps/dir/?api=1&origin=23.6513358,86.1563967&destination=23.66642, 86.15159