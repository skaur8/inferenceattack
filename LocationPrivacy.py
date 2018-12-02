import pandas as pd
import numpy as np
import sys
import datetime
from math import sin, cos, sqrt, atan2, radians
import random
import folium
import folium.plugins
folium.plugins.MarkerCluster()
from folium.plugins import MarkerCluster
MarkerCluster()

folium_map=None
marker_cluster=None
def map_generation():
    global folium_map,marker_cluster
    folium_map = folium.Map(location=[39.984702,116.318417],
                        zoom_start=11,
                        tiles='cartodbpositron')

    marker_cluster = MarkerCluster().add_to(folium_map)


	
def random_obfuscation(start,end,name):
    global folium_map,marker_cluster
    removal_list=[]
	#Approx Radius of Earth
    R = 6373.0
	#Radius for Spatial Cloaking 0.1km=100m
    radius=0.1
	#Granularity for Rounding
    granularity=3
	#Mean and Standard Deviation for Noise
    mu=0
    sd=0.001
	#Methods are applied if the difference between the time of two Latitude and longitude records is greater than threshold
    threshold=10
	#Random selection of Method
    method =random.randint(start,end)
	#Precious Latitude and longitude record time
    previous_date_time=None
	#Latitude and longitude csv
    clean_signal_data= pd.read_csv("lat_long.csv")
    final_data=[]
	#Method name applied to Latitude and longitude records
    comment=None
	
    for index, row in clean_signal_data.iterrows():
        #Map the original Latitude and longitude
        folium.Marker([row['LAT'],row['LON']],popup=str(row['ID'])+str([row['LAT'],row['LON']]),icon=folium.Icon(color='green')).add_to(marker_cluster)
		# Select method
        method =random.randint(start,end)
        comment="NOCHANGE"
        updated_lon=row['LON']
        updated_lat=row['LAT']
        latest_datetime=datetime.datetime.strptime("{}, {}".format(row['Date'].strip(),row['Time'].strip()), "%m/%d/%Y, %H:%M:%S")
		#for first record
        if(previous_date_time==None):
            previous_date_time=latest_datetime
            final_data.append([row['ID'],row['LAT'],row['LON'],updated_lat,updated_lon,row['Date'],row['Time'],'FirstEntry'])
            continue
		#Calculate time difference
        elasped=latest_datetime-previous_date_time
		#Comapare time
        if(elasped > datetime.timedelta(seconds=10)):
		
            if(method==1):
			    # Spatial CLOAKING
                center_lat=radians(row['LAT'])
                center_long=radians(row['LON'])
                l=[]
				#Removing all records within the given radius of cloaking
                for index1, row1 in clean_signal_data.iterrows():
                    obs_lat=radians(row1['LAT'])
                    obs_long=radians(row1['LON'])
                    if(row['ID']!=row1['ID']):
                        dlat=center_lat-obs_lat
                        dlon=center_long-obs_long
                        a = sin(dlat / 2)**2 + cos(center_lat) * cos(obs_lat) * sin(dlon / 2)**2
                        c = 2 * atan2(sqrt(a), sqrt(1 - a))
                        distance = R * c # in km
                  
                        if(distance<0.1):
                            l.append(row1['ID'])
							#Creating a list of points to be removed as they fall in the given radius
                            removal_list.append(row1['ID'])
                comment="CLOAKING"+str(l)
                updated_lon=row['LON']
                updated_lat=row['LAT']
                                        
            elif (method==2):
			    #Gaussian Noise
                x=np.random.normal(mu, sd)
                y=np.random.normal(mu, sd)
				#Add Noise
                updated_lon=row['LON']+y
                updated_lat=row['LAT']+x
                comment="GAUSSIAN"
                #if(row['ID']==5):
                #    folium.Marker([updated_lat,updated_lon],icon=folium.Icon(color='green')).add_to(marker_cluster)	               
            elif(method==3):
			    #Laplace Noise
                x=np.random.laplace(mu, sd)
                y=np.random.laplace(mu, sd)
				#Add noise
                updated_lon=row['LON']+y
                updated_lat=row['LAT']+x  
                comment="LAPLACE"

				
            elif(method==4):
			    #Rounding the Latitude and longitude to 3rd decimal.Ref https://gis.stackexchange.com/questions/8650/measuring-accuracy-of-latitude-and-longitude for accuracy
                updated_lon=round(row['LON'],granularity)
                updated_lat=round(row['LAT'],granularity)
                comment="ROUNDING"	
		
                
		#Entry in Excel the original and updated Latitude and longitude
        final_data.append([row['ID'],row['LAT'],row['LON'],updated_lat,updated_lon,row['Date'],row['Time'],comment])
        
		#Updating previous time
        previous_date_time=latest_datetime

		
	# Remove duplicates from Spatial Cloaking removal list 
    removal_list=set(removal_list)
	#Display the count of removed co-ordinates
    if((start==end and start==1 )or (start!=end)):
        print('Number of elements removed due to Spatial clocking')
        print(len(removal_list))			
	
    df = pd.DataFrame(final_data,columns=['ID','LAT','LON','UPDATED_LAT','UPDATED_LON','Date','Time','Comment'])   
    update_data=[]
	#Remove spatial cloaking removal co-ordinates from the final csv to be genrated
    for index,row in df.iterrows():
        if(row['ID'] not in removal_list):
            if('CLOAKING' in row['Comment']):
                folium.Marker([row['LAT'],row['LON']],popup=str(row['ID']),icon=folium.Icon(color='grey')).add_to(folium_map)
            update_data.append(row)
    
    new_df= pd.DataFrame(update_data,columns=['ID','LAT','LON','UPDATED_LAT','UPDATED_LON','Date','Time','Comment'])
	# get updated lat and long 
    locations=new_df[["UPDATED_LAT","UPDATED_LON"]]
    l=locations.values.tolist()
    rowid=new_df['ID']
    rowidlist=rowid.values.tolist()
    
	#Draw each co-ordinate of final csv to folium map
    for point in range(0,len(l)):
        if(start==end and start==1):
            #Representing Spatial Cloaking co-ordinates with circle
            folium.Circle(l[point],radius=100,popup=str(rowidlist[point])+str(l[point])).add_to(marker_cluster)
        else:
            folium.Marker(l[point],popup=str(rowidlist[point])+str(l[point]),icon=folium.Icon(color='blue')).add_to(marker_cluster)

    folium_map.save(name+".html")
    #Generate CSV
    new_df.to_csv(name+'.csv')
    print('Complete')



#Menu display 
name=None
start=None
end=None
print("Select from below options:")
print("1. Spatial Cloaking")
print("2. Gaussian")
print("3. Laplace")
print("4. Rounding")
print("5. Random Obfuscation")

user_choice=int(input("Enter your choice: "))
if(user_choice==1):
   start=1
   end=1
   print('Method Spatial Cloaking')
   name="Spatial Cloaking"
elif(user_choice==2):
    start=2
    end=2
    print('Method Gaussian')
    name="Gaussian"
elif(user_choice==3):
    start=3
    end=3
    print('Method Laplace')
    name="Laplace"	
elif(user_choice==4):
    start=4
    end=4
    print('Method Rounding')
    name='Rounding'
elif(user_choice==5):
    start=1
    end=4
    print('Method Random Obfuscation')
    name='Random Obfuscation'

#print(start,end)
map_generation()
random_obfuscation(start,end,name)
	
	