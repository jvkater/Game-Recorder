import requests
from time import sleep,time
from threading import Thread
from tkinter import Tk, filedialog, Label, Radiobutton, Button, IntVar

def starter():
    global game
    game = recording_thread()
    game.start_recording()


class recording_thread(object):
    def __init__(self):
        self.core_thread = Thread(target = core)

    def start_recording(self):
        self.core_thread.start()
        self.record_state = True

    def get_state(self):
        return self.record_state

    def set_state(self, state):
        self.record_state = state

    def stop_recording(self):
        self.core_thread.join()

def get_streams(link):
    playlist_content = requests.get(link).content
    files = [x.decode() for x in playlist_content.split() if '.ts' in x.decode()]
    return files

def select_folder():
    folder = filedialog.askdirectory()
    return folder

def core():
    start_time = time()

    if quality_type.get() == 0:
        stream_page = requests.get('https://rtsp.me/embed/7QXWYZf6/') #6fZYWXQ7
        filename = select_folder() + '/game_stream_reg.avi'
    else:
        stream_page = requests.get('https://rtsp.me/embed/6fZYWXQ7/') #7QXWYZf6
        filename = select_folder() + '/game_stream_HD.avi'

    placeholder.config(text='Ведется запись', fg='red')
    root.update()

    quality_links = [x for x in stream_page.content.split() if '23b.ru' in x.decode()]
    temp_link = quality_links[1][16:-20].decode()
    quality_db = {'regular': quality_links[0][16:-2].decode(), 'HD': quality_links[1][16:-2].decode()}

    media_link = 'https://n1.ru.rtsp.me/' + temp_link + '/hls/'
    playlist_link = 'https://n1.ru.rtsp.me/' + quality_db['HD']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; '
                      'WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 '
                      'Safari/537.36'}

    checker = []
    open(filename, 'w').close()
    progress = True
    while progress:
        playlist = get_streams(playlist_link)
        while playlist == checker:
            sleep(2)
            playlist = get_streams(playlist_link)
        for i in playlist:
            tsurl = media_link + i
            stream_data = requests.get(tsurl, stream=True, headers=headers)
            if (stream_data.status_code == 200):
                with open(filename, 'ab') as f:
                    for chunk in stream_data.iter_content(chunk_size=1024):
                        f.write(chunk)
                break
            else:
                print('smth wrong')
        checker = playlist
        if time()-start_time>=7200: #7200 для 2 часов записи
            progress=False
        if game.get_state() == False:
            break
            progress=False
    placeholder.config(text = "Запись завершена", fg = 'green')

def stopper(): #не работает! пофиксить
    game.set_state(False)
    sleep(5)
    root.destroy()


root = Tk()
root.title('Game recorder')
w =350 # ширина окна
h = 350 # высота окна

# параметры экрана
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()


# нахождение центра
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# расчёт геометрии
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

#делаем отступ для шапки и первой колонки
root.grid_columnconfigure(0, minsize = 50)
root.grid_columnconfigure(2, minsize = 20)
root.grid_rowconfigure(0, minsize = 50)
root.grid_rowconfigure(2, minsize = 20)
root.grid_rowconfigure(4, minsize = 15)
root.grid_rowconfigure(7, minsize = 20)
root.grid_rowconfigure(9, minsize = 20)

greetings = Label(root, text = 'Привет!')
greetings.grid(row = 1, column = 1, columnspan = 3)

camera_selection_label = Label(root, text = 'Выберите камеру:')
camera_selection_label.grid(row = 3, column = 1 )

quality_selection_label = Label(root, text = 'Выберите качество:')
quality_selection_label.grid(row = 3, column = 3)

camera_type = IntVar()
quality_type = IntVar()

radio_home = Radiobutton(root, text = 'В поле', variable = camera_type, value = 1)
radio_field = Radiobutton(root, text = 'В дом', variable = camera_type, value = 2, state='disabled')

radio_home.grid(row = 5, column =1)
radio_field.grid(row =6, column = 1)

radio_quality_regular = Radiobutton(root, text = 'Обычное', variable = quality_type, value = 0)
radio_quality_hd = Radiobutton(root, text = 'HD', variable = quality_type, value = 1)

radio_quality_regular.grid(row = 5, column =3)
radio_quality_hd.grid(row = 6, column =3)

placeholder = Label(root, text = '')
placeholder.grid(row = 8, column =1, columnspan = 3)


start_button = Button(root, text = 'Начать запись',command = starter)
start_button.grid(row = 10, column = 1)

quit_button = Button(root, text = 'Выход', command = stopper)
quit_button.grid(row = 10, column =3)

root.mainloop()

