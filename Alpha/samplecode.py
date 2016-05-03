# -*- coding: utf-8 -*-
from dataapi import Client
if __name__ == "__main__":
    try:
        client = Client()
        client.init('db087ed39012466cf5a797e6a150aaaf788a103423a9ec2b172cc0e55768aed2')
        url1='/api/macro/getChinaDataGDP.csv?field=&indicID=M010000002&indicName=&beginDate=&endDate='
        code, result = client.getData(url1)
        if code==200:
            print result
        else:
            print code
            print result
        url2='/api/subject/getThemesContent.csv?field=&themeID=&themeName=&isMain=1&themeSource='
        code, result = client.getData(url2)
        if(code==200):
            file_object = open('thefile.csv', 'w')
            file_object.write(result)
            file_object.close( )
        else:
            print code
            print result
    except Exception, e:
        #traceback.print_exc()
        raise e
