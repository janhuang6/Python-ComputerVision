import json

if __name__=="__main__":
    input_json = '/Users/janhuang/Downloads/Video_Tracking/2-20180801-1540/1533164470000/tracks.json'
    with open(input_json) as data_file:
        data= json.load(data_file)

    count =0
    IOU = 0
    max_iou = -100.0
    min_iou = 100.0
    for item in data:
        for multi_view_track in item['multi_views_track']:
            for camera_track in multi_view_track['camera_track']:
                track_description= camera_track['track_description']

                # handle item_rois
                item_rois = track_description['item_rois']
                # number of item_rois
                item_rois_no = len(item_rois)

                if item_rois_no < 2: # Need both "PREDICTION" and "DETECTION" to calculate IOU
                    continue

                # map of "PREDICTION,DETECTION,CORRECTION" and position
                existingTypes= {}
                for k in range(0,item_rois_no):
                    existingTypes[item_rois[k]['type']] = k

                if "PREDICTION" not in existingTypes.keys():
                    continue
                if "DETECTION" not in existingTypes.keys():
                    continue

                item_rois_temp = item_rois[(existingTypes.get("PREDICTION"))]
                #print(item_rois_temp['array'])
                y1=item_rois_temp['array'][0]
                x1=item_rois_temp['array'][1]
                y2=y1 +item_rois_temp['array'][2]
                x2=x1 +item_rois_temp['array'][3]
                bb_prediction={'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2}
                bb_prediction_confidence = item_rois_temp['confidence']

                item_rois_temp = item_rois[(existingTypes.get("DETECTION"))]
                y1=item_rois_temp['array'][0]
                x1=item_rois_temp['array'][1]
                y2=y1 +item_rois_temp['array'][2]
                x2=x1 +item_rois_temp['array'][3]
                bb_detection={'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2}
                bb_detection_confidence = item_rois_temp['confidence']

                iou = get_iou(bb_prediction, bb_detection)

                if max_iou < iou:
                    max_iou = iou
                elif min_iou > iou:
                    min_iou = iou
                IOU += iou
                count += 1

    if count > 0:
        IOU = IOU/float(count)
    print("Minimum IOU=", min_iou)
    print("Maximum IOU=", max_iou)
    print("Average IOU=", IOU, "over", count, "iterations.")


def get_iou(bb1, bb2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    bb1 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner
    bb2 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x, y) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner

    Returns
    -------
    float
        in [0, 1]
    """
    assert bb1['x1'] < bb1['x2']
    assert bb1['y1'] < bb1['y2']
    assert bb2['x1'] < bb2['x2']
    assert bb2['y1'] < bb2['y2']

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1['x1'], bb2['x1'])
    y_top = max(bb1['y1'], bb2['y1'])
    x_right = min(bb1['x2'], bb2['x2'])
    y_bottom = min(bb1['y2'], bb2['y2'])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
    bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou
