import cv2


def show_image_foreground(window_name, image, mouse_callback):
    cv2.imshow(window_name, image)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    if mouse_callback is not None:
        cv2.setMouseCallback(window_name, mouse_callback)


def on_mouse_event(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('  mouse click: x = %d, y = %d' % (x, y))
