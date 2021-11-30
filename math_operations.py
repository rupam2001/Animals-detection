

def isTwoRectangeOverlap(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    coords_rect1 = {"x1": x1, "y1": y1, "x2": x1 + w1, "y2": y1, "x3": x1 + w1, "y3": y1 + h1, "x4": x1, "y4": y1 + h1 } #main rect
    coords_rect2 = {"x1": x2, "y1": y2, "x2": x2 + w2, "y2": y2, "x3": x2 + w2, "y3": y2 + h2, "x4": x2, "y4": y2 + h2 } #to compare

    if (coords_rect1["x1"] > coords_rect2["x1"] and coords_rect1["x1"] < coords_rect2["x2"]) and (coords_rect1["y1"] > coords_rect2["y2"] and coords_rect1["y1"] < coords_rect2["y3"]):
        # print("top left")
        return True
    if (coords_rect1["x2"] > coords_rect2["x1"] and coords_rect1["x2"] < coords_rect2["x2"]) and (coords_rect1["y2"] > coords_rect2["y1"] and coords_rect1["y2"] < coords_rect2["y4"]):
        # print("top right")
        return True
    if (coords_rect1["x3"] > coords_rect2["x1"] and coords_rect1["x3"] < coords_rect2["x2"]) and (coords_rect1["y3"] > coords_rect2["y1"] and coords_rect1["y3"] < coords_rect2["y4"]):
        # print("bottom right")
        return True
    if (coords_rect1["x4"] > coords_rect2["x1"] and coords_rect1["x4"] < coords_rect2["x2"]) and (coords_rect1["y4"] > coords_rect2["y2"] and coords_rect1["y4"] < coords_rect2["y3"]):
        # print("bottom left")
        return True
    return False

def getUnionOfTwoRects(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    all_x_list = [  x1, x1 + w1, x2, x2 + w2]
    all_y_list = [  y1, y1 + h1, y2, y2 + h2]

    x_min = min(all_x_list)
    y_min = min(all_y_list)

    x_max = max(all_x_list)
    y_max = max(all_y_list)

    w = x_max - x_min
    h = y_max - y_min
    x = x_min
    y = y_min

    return x, y, w, h


def getUnionOfRects(rect_list=[]):
    overlaped_rects = []
    overlaped_rects_indexs = []
    uniooned_rects = None
    for i in range(len(rect_list) - 1):
        r1, r2 = rect_list[i], rect_list[i + 1]
        if isTwoRectangeOverlap(r1, r2):
            overlaped_rects.append(r1)
            overlaped_rects.append(r2)
            overlaped_rects_indexs.append(i)
            overlaped_rects_indexs.append(i + 1)
            rect_list[i + 1] = getUnionOfTwoRects(r1, r2)
            uniooned_rects = rect_list[ i + 1]
    if uniooned_rects is not None and all(i <= 0 for i in uniooned_rects):
        return None
    
    return uniooned_rects, overlaped_rects_indexs
    