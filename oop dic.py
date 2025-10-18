import sqlite3
import json
from tkinter import *
import pyttsx3
class Database:
    def __init__(self):
        name="dictionary.db"
        self.con=sqlite3.connect(name)
        self.cur=self.con.cursor()
    def show_info(self):
        print(self.cur.execute("select * from sqlite_master").fetchall())
    def english_translate(self,word):
        q=self.cur.execute("SELECT persian FROM words WHERE english=?",(word,))
        list_of_words=q.fetchone()
        meanings=json.loads(list_of_words[0])
        return meanings
    def persian_translate(self,word):
        query=self.cur.execute("SELECT english From words WHERE persian=?",(word))
        meaning=query.fetchall()
        return meaning
    def all_english(self):
        english_words=self.cur.execute("SELECT english FROM words").fetchall()
        return english_words
    def all_persian(self):
        persian_words=self.cur.execute("SELECT persian FROM words").fetchall()
        return persian_words
    def execute_query(self,query,p):
        return self.cur.execute(query,p)
    def commit_query(self):
        self.con.commit()
class Manage_favorites:
    def __init__(self,db:Database):
        self.db=db
    def is_favorite(self,word):
        res=self.db.execute_query("SELECT favorite FROM words WHERE english=?",(word,)).fetchone()
        return res[0]==1
    def remove_favorite(self,word,add_btn):
        self.db.execute_query("UPDATE words SET favorite=0 WHERE english=?",(word,))
        self.db.commit_query()
        add_btn
    def add_to_favorites(self,word,del_btn):
        self.db.execute_query("UPDATE words SET favorite=1 WHERE english=?",(word,))
        self.db.commit_query()
        del_btn
    def all_favorites(self):
        all_fav=self.db.execute_query("SELECT english FROM words WHERE favorite=?",(1,)).fetchall()
        return all_fav
class Process_word:
    def __init__(self,db:Database):
        self.db=db
    def is_english(self,word):
        english_words=self.db.all_english()
        return (word,) in english_words
    def get_persian(self,word):
        if "ي" in word:
            i='ي'
            word=word.replace(i,'ی')
        persian_words=self.db.all_persian()
        for persian in persian_words:
            if word in json.loads(persian[0]) or (word+'\u200c') in json.loads(persian[0]):
                return persian
        return False     
    def talafoz(self,word):
        self.word=word
        engine=pyttsx3.init()
        engine.say(word)
        engine.runAndWait()      
class Ui:
    def __init__(self,db:Database,pr:Process_word,fav:Manage_favorites):
        self.db=db
        self.pr=pr
        self.fav=fav
        self.widgets_list=[]
        self.widget_exist=False
    def make_window(self,size,title):
        self.window=Tk()
        self.window.title(title)
        self.window.geometry(size)
        for i in range(20):
            self.window.columnconfigure(i,weight=1)
        menu=Menu(self.window)
        menu.add_cascade(label='FAVORITES',command=self.show_favorites)
        self.window.config(menu=menu)
    def run(self):
        self.window.mainloop()
    def get_entry(self,r,c):
        self.entry=Entry(self.window,font=('Arial',14))
        self.entry.grid(row=r,column=c)
        btn=Button(self.window,text='Translate',width=8,height=2,command=self.show_translate)
        btn.grid(row=4,column=9)
        word=self.entry.get()  
    def make_add_button(self):
        word=self.entry.get()
        add_btn=Button(self.window,text='ADD TO FAVORITES',width=18,height=3,command=lambda:self.fav.add_to_favorites(word,self.make_remove_button()))
        add_btn.grid(row=4,column=10)
    def make_remove_button(self):
        word=self.entry.get()
        remove_btn=Button(self.window,text='REMOVE\nFROM FAVORITES',bg='red',width=18,height=3,command=lambda:self.fav.remove_favorite(word,self.make_add_button()))
        remove_btn.grid(row=4,column=10) 
    def get_word(self):
        self.make_remove_button()
        return self.entry.get()
    def show_translate(self):
        if self.widget_exist:
            for widget in self.widgets_list:
                widget.grid_forget()
        word=self.entry.get()
        if self.pr.is_english(word):
            meanings=self.db.english_translate(word)
            r=6
            for i in meanings:
                self.label=Label(self.window,text=i)
                self.label.grid(row=r,column=9)
                self.widgets_list.append(self.label)
                r+=1
            sound_btn=Button(self.window,text='تلفظ صوتی',width=18,height=3,command=lambda:self.pr.talafoz(word))
            sound_btn.grid(row=5,column=9)
            self.widgets_list.append(sound_btn)
            self.widget_exist=True
            favorite=self.fav.is_favorite(word)
            if not favorite:
                add_btn=Button(self.window,text='ADD TO FAVORITES',width=18,height=3,command=lambda:self.fav.add_to_favorites(word,self.make_remove_button()))
                add_btn.grid(row=4,column=10)
            else:
                btn=self.make_remove_button()
                self.fav.add_to_favorites(word,btn)
        elif self.pr.get_persian(word):
            persian_tuple=self.pr.get_persian(word)
            self.widget_exist=True
            meaning=self.db.persian_translate(persian_tuple)
            lb=Label(self.window,text=meaning,width=20,height=5)
            lb.grid(row=5,column=9)
            self.widgets_list.append(lb)
        else:
            widget_exist=True
            label=Label(self.window,text='No Result!',width=7,height=3)
            label.grid(row=5,column=9)
            self.widgets_list.append(label)
    def hide_widget(self,widget_1,widget_2):
        widget_1.place_forget()
        widget_2.place_forget()
    def show_favorites(self):
        box=Listbox(self.window,width=40,height=20)
        box.place(x=5,y=5)
        favorite_words=self.fav.all_favorites()
        for word in favorite_words:
            box.insert(END,f"{word[0]}:{self.db.english_translate(word[0])[0]}")
        close_btn=Button(self.window,text='close',width=5,height=2,command=lambda:self.hide_widget(box,close_btn))
        close_btn.place(x=10,y=330)      
d=Database()
prw=Process_word(d)
fav=Manage_favorites(d)
ui=Ui(d,prw,fav)
ui.make_window('1000x900','DICTIONARY')
ui.get_entry(3,9)
ui.run()