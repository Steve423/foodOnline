from django.shortcuts import redirect
from django.test import TestCase
import winrt.windows.devices.geolocation as wdg, asyncio


# Create your tests here.
     
async def getCoords():
        locator = wdg.Geolocator()
        pos = await locator.get_geoposition_async()
        
        return [pos.coordinate.latitude, pos.coordinate.longitude]
    
def getLoc():
    return asyncio.run(getCoords())

def search():
    myGet = getLoc()
    vender_newlat = ""
    vender_2newlat = ""
    intLoop =0
    for xmyGet in myGet:
        if intLoop == 0:
             myLat = xmyGet
        if intLoop == 1:
             myLng = xmyGet

        intLoop = intLoop +1
    print("__myLat_=_" + str(myLat))
    print("__myLng_=_" + str(myLng))

search()
