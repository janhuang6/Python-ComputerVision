import json

if __name__=="__main__":
    print("God is with me.")
    with open('/Users/touchage/Downloads/tracks.json') as data_file:
        data= json.load(data_file)

    with open('/Users/touchage/Downloads/tracks_output.csv','w') as csv_file:
        headers= ["item_id", "cam_name","frame_id","frame_timetamp","item_type","item_descrtion","sub_items","detection_type","detection_array1", "detection_array2", "detection_array3","detection_array4","detection_confidence","prediction_type","prediction_array1","prediction_array2","prediction_array3","prediction_array4","prediction_confidence","correction_type",	"correction_array1", "correction_array2","correction_array3","correction_array4","correction_confidence"]
        headers = ', '.join(headers)
        csv_file.write(headers+'\n')
        item_rois_list = ["DETECTION","PREDICTION","CORRECTION"]
        data_point= ''
        count =0
        for item in data:
            for multi_view_track in item['multi_views_track']:
                for camera_track in multi_view_track['camera_track']:
                    data_point = ''
                    data_point = data_point + item['item_id'] + ','
                    data_point = data_point + multi_view_track['cam_name'] + ','
                    data_point = data_point + camera_track['frame_id']+','+camera_track['frame_timestamp']+','

                    track_description= camera_track['track_description']
                    data_point = data_point+track_description['item_type']+','+track_description['item_description']+','

                    sub_items=','.join(track_description['sub_items'])
                    data_point = data_point + sub_items+','

                    # handle item_rois
                    item_rois = track_description['item_rois']
                    # number of item_rois
                    item_rois_no = len(item_rois)

                    # map of "DETECTION,PREDICTION,CORRECTION" and position
                    existingTypes= {}
                    for k in range(0,item_rois_no):
                        existingTypes[item_rois[k]['type']] = k

                    item_rois_str = ''
                    for type in item_rois_list:
                        # not exist, NA value for array and confidence values
                        if type not in existingTypes.keys():
                            NA_temp=['NA']*5
                            NA_temp=', '.join(NA_temp)
                            item_rois_str = item_rois_str + type+',' +NA_temp+','
                        else:
                            item_rois_temp = item_rois[(existingTypes.get(type))]
                            array_temp= ', '.join(str(x) for x in item_rois_temp['array'])
                            item_rois_str = item_rois_str + type+',' + array_temp +','+str(item_rois_temp['confidence'])+','
                    item_rois_str =item_rois_str[0:-1]

                    data_point = data_point+item_rois_str+"\n"
                    # write each data point- each frame into file
                    print (data_point)
                    csv_file.write(data_point)
                    count = count+1

    print(count)
    print("Holy Spirit.")