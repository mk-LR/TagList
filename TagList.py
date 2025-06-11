import os
import shutil
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from PIL import Image, ImageTk

LIST_FOLDER = os.path.join(os.path.dirname(__file__), "list")

class TagListApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TagList")
        self.geometry("500x500")
        self.current_file = None
        self.main_frame = None
        self.taglist_frame = None
        self.show_title()


    def show_title(self):
        if self.taglist_frame:
            self.taglist_frame.destroy()
        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.title_frame = tk.Frame(self.main_frame, bg="white")
        self.title_frame.pack(pady=10, fill=tk.X)
        lbl_title = tk.Label(self.title_frame, text="TagList", font=("MSゴシック",32, "bold"), fg="#003600", bg="white")
        lbl_title.pack(padx=10, side=tk.LEFT)
        btn_add_txt = tk.Button(self.title_frame, text="新規作成", command=self.textfile_create)
        btn_add_txt.pack(padx=5, side=tk.RIGHT)
        self.delete_mode = False
        self.confirm_frame = None
        self.delete_button = tk.Button(self.title_frame, text="削除", command=self.modechange_delete)
        self.delete_button.pack(side=tk.RIGHT, padx=5)

        self.scroll_frame = tk.Frame(self.main_frame)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox = tk.Listbox(self.scroll_frame, font=("MSゴシック",20, "bold"), yscrollcommand=scrollbar.set, height=200, width=200)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind("<Double-Button-1>", self.textfile_open)
        scrollbar.config(command=self.file_listbox.yview)
        self.file_listbox.bind("<MouseWheel>", lambda e: self.file_listbox.yview_scroll(-1 * int(e.delta / 120), "units"))
        self.textfile_load()

    def textfile_load(self):
        self.file_listbox.delete(0, tk.END)
        if not os.path.exists(LIST_FOLDER):
            os.makedirs(LIST_FOLDER)
        files = [f for f in os.listdir(LIST_FOLDER) if f.endswith(".txt")]
        for file in files:
            self.file_listbox.insert(tk.END, file[:-4])

    def textfile_create(self):
        filename = simpledialog.askstring("新規リスト", "リスト名を入力してください:")
        if filename:
            filepath = os.path.join(LIST_FOLDER, filename + ".txt")
            if os.path.exists(filepath):
                messagebox.showerror("エラー", "既に存在します。名前を変更して再度お試しください。")
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("")
                self.textfile_load()

    def textfile_open(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0])
            file_path = os.path.join(LIST_FOLDER, (filename+".txt"))
            if self.delete_mode:
                self.confirm_delete(file_path)
            else:
                self.current_file = file_path
                self.show_taglist(filename)

    def modechange_delete(self):
        self.delete_mode = not self.delete_mode
        if self.delete_mode:
            self.delete_button.config(relief=tk.SUNKEN, bg="red")
        else:
            self.delete_button.config(relief=tk.RAISED, bg="SystemButtonFace")
            if self.confirm_frame:
                self.confirm_frame.destroy()
                self.confirm_frame = None

    def confirm_delete(self, file_path):
        if self.confirm_frame:
            self.confirm_frame.destroy()
        self.confirm_frame = tk.Frame(self.main_frame, bg="pink")
        self.confirm_frame.place(x=50, y=80)
        file_name = os.path.basename(file_path)
        label = tk.Label(self.confirm_frame, text=f"{file_name[:-4]} を本当に削除しますか？", font=("MSゴシック",14, "bold"), bg="white")
        label.pack(padx=10, pady=5)
        yes_button = tk.Button(self.confirm_frame, text="はい", command=lambda: self.textfile_delete(file_path))
        yes_button.pack(side=tk.LEFT, padx=15, pady=5)
        no_button = tk.Button(self.confirm_frame, text="いいえ", command=self.cancel_delete)
        no_button.pack(side=tk.RIGHT, padx=15, pady=5)

    def textfile_delete(self, file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print("削除エラー:", e)
        self.confirm_frame.destroy()
        self.confirm_frame = None
        self.textfile_load()

    def cancel_delete(self):
        if self.confirm_frame:
            self.confirm_frame.destroy()
            self.confirm_frame = None


    def show_taglist(self, filename):
        self.main_frame.destroy()
        self.taglist_frame = tk.Frame(self, bg="white")
        self.taglist_frame.pack(fill=tk.BOTH, expand=True)
        self.top_frame = tk.Frame(self.taglist_frame, bg="white")
        self.top_frame.pack(pady=10, fill=tk.X)
        btn_back = tk.Button(self.top_frame, text="戻る", command=self.show_title)
        btn_back.pack(side=tk.LEFT, padx=5)
        lbl_title = tk.Label(self.top_frame, text=filename, font=("MSゴシック",24, "bold"), fg="#003600", bg="white")
        lbl_title.pack(side=tk.LEFT, padx=5)
        btn_add_line = tk.Button(self.top_frame, text="追加", command=self.select_image)
        btn_add_line.pack(side=tk.RIGHT, padx=5)
        self.edit_mode = False
        self.edit_button = tk.Button(self.top_frame, text="編集", command=self.modechange_edit)
        self.edit_button.pack(side=tk.RIGHT, padx=5)
        self.cut_mode = False
        self.cut_button = tk.Button(self.top_frame, text="削除", command=self.modechange_cut)
        self.cut_button.pack(side=tk.RIGHT, padx=5)
        self.sort_mode = False
        self.lbl_images = []
        self.sorting = None
        self.sort_button = tk.Button(self.top_frame, text="並替", command=self.modechange_sort)
        self.sort_button.pack(side=tk.RIGHT, padx=5)

        self.search_tags = []
        self.search_frame = tk.Frame(self.taglist_frame)
        self.search_frame.pack(fill=tk.X, pady=5)
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_button = tk.Button(self.search_frame, text="検索", command=self.taglist_search)
        self.search_button.pack(side=tk.RIGHT, padx=5)

        self.scroll_frame = tk.Frame(self.taglist_frame)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.scroll_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.scroll_y = tk.Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.inner_frame = tk.Frame(self.canvas,bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.image_refs = []
        self.taglist_load()

    def taglist_load(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.image_refs.clear()
        if not self.current_file:
            return
        with open(self.current_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.update_idletasks()
        window_width = self.winfo_width()
        image_cell_width = 200
        columns = max(1, window_width // image_cell_width)
        row = 0
        col = 0
        self.lbl_images = []
        for line in lines:
            element = line.strip().split(" ")
            if len(element) < 2:
                continue
            filename = element[0]
            title = element[1]
            tags = []
            if len(element) > 2:
                tags = element[2:]
            if self.search_tags:
                if not all(tag in tags for tag in self.search_tags):
                    continue
            image_path = os.path.join(LIST_FOLDER, filename)
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img = img.resize((120, 120))
                    img = ImageTk.PhotoImage(img)
                    label = tk.Label(self.inner_frame, image=img, text=title[:11], font=("MSゴシック",12, "bold"), compound=tk.TOP, bg="white")
                    label.image = img
                    self.image_refs.append(img)
                    label.grid(row=row, column=col, padx=20, pady=20)
                    label.bind("<Button-1>", lambda e, line=line, label=label: self.taglist_edit(line,label))
                    self.lbl_images.append(label)
                    col += 1
                    if col >= columns:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"画像読み込みエラー: {e}")

    def select_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filepath:
            self.taglist_register(filepath)

    def taglist_register(self, filepath):
        title = simpledialog.askstring("タイトル", "登録する名前を入力してください")
        if not title:
            return
        tags = simpledialog.askstring("タグ", "半角スペース区切りでタグを入力してください（例: 〇〇 △△）")
        ext = os.path.splitext(filepath)[1]
        safe_title = title.replace(" ", "_")
        filename = f"{safe_title}{ext}"
        dest_path = os.path.join(LIST_FOLDER, filename)
        counter = 1
        while os.path.exists(dest_path):
            filename = f"{safe_title}_{counter}{ext}"
            dest_path = os.path.join(LIST_FOLDER, filename)
            counter += 1
        shutil.copy(filepath, dest_path)
        line = f"{filename} {title}"
        tags = tags.strip().split(" ")
        for tag in tags:
            line += " #" + tag
        with open(self.current_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        self.taglist_load()

    def taglist_search(self):
        tags = self.search_entry.get().strip()
        self.search_tags = []
        if tags:
            word = tags.split(" ")
            for tag in word:
                if not tag.startswith("#"):
                    tag = "#" + tag
                self.search_tags.append(tag)
        self.taglist_load()

    def modechange_edit(self):
        self.edit_mode = not self.edit_mode
        if self.cut_mode:
            self.cut_mode = not self.cut_mode
            self.cut_button.config(relief=tk.RAISED, bg="SystemButtonFace")
        if self.sort_mode:
            self.sort_mode = not self.sort_mode
            self.sort_button.config(relief=tk.RAISED, bg="SystemButtonFace")
        if self.edit_mode:
            self.edit_button.config(relief=tk.SUNKEN, bg="#50AA50")
        else:
            self.edit_button.config(relief=tk.RAISED, bg="SystemButtonFace")

    def modechange_cut(self):
        self.cut_mode = not self.cut_mode
        if self.edit_mode:
            self.edit_mode = not self.edit_mode
            self.edit_button.config(relief=tk.RAISED, bg="SystemButtonFace")
        if self.sort_mode:
            self.sort_mode = not self.sort_mode
            self.sort_button.config(relief=tk.RAISED, bg="SystemButtonFace")
        if self.cut_mode:
            self.cut_button.config(relief=tk.SUNKEN, bg="red")
        else:
            self.cut_button.config(relief=tk.RAISED, bg="SystemButtonFace")

    def modechange_sort(self):
        self.sort_mode = not self.sort_mode
        if self.edit_mode:
            self.edit_mode = not self.edit_mode
            self.edit_button.config(relief=tk.RAISED, bg="SystemButtonFace")
        if self.cut_mode:
            self.cut_mode = not self.cut_mode
            self.cut_button.config(relief=tk.RAISED, bg="SystemButtonFace")
        if self.sort_mode:
            self.sort_button.config(relief=tk.SUNKEN, bg="#50AA50")
        else:
            self.sort_button.config(relief=tk.RAISED, bg="SystemButtonFace")

    def taglist_edit(self, line, label):
        parts = line.strip().split(" ")
        if self.edit_mode:
            if len(parts) < 2:
                return
            old_filename = parts[0]
            old_title = parts[1]
            old_tags = " ".join(parts[2:])
            edit_win = tk.Toplevel(app)
            edit_win.title("編集")
            tk.Label(edit_win, text="タイトル").pack()
            title_entry = tk.Entry(edit_win)
            title_entry.insert(0, old_title)
            title_entry.pack()
            tk.Label(edit_win, text="タグ（スペース区切り）").pack()
            tag_entry = tk.Entry(edit_win)
            tag_entry.insert(0, old_tags)
            tag_entry.pack()
            def save_changes():
                new_title = title_entry.get().strip()
                new_tags = tag_entry.get().strip()
                if not new_title or not new_title:
                    return
                old_path = os.path.join(LIST_FOLDER, old_filename)
                new_filename = new_title + os.path.splitext(old_filename)[1]
                new_path = os.path.join(LIST_FOLDER, new_filename)
                if old_filename != new_filename:
                    try:
                        os.rename(old_path, new_path)
                    except Exception as e:
                        print("リネーム失敗:", e)
                        return
                with open(self.current_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(self.current_file, "w", encoding="utf-8") as f:
                    for l in lines:
                        if l.strip() == line.strip():
                            f.write(f"{new_filename} {new_title} {' '.join(tag for tag in new_tags.split())}\n")
                        else:
                            f.write(l)
                edit_win.destroy()
                self.taglist_load()
            tk.Button(edit_win, text="保存", command=save_changes).pack(pady=10)
        if self.cut_mode:
            file_path = os.path.join(LIST_FOLDER, parts[0])
            try:
                os.remove(file_path)
            except Exception as e:
                print("削除エラー:", e)
            with open(self.current_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(self.current_file, "w", encoding="utf-8") as f:
                for l in lines:
                    if l.strip() == line.strip():
                        continue
                    else:
                        f.write(l)
            self.taglist_load()
        if self.sort_mode:
            if self.sorting:
                with open(self.current_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(self.current_file, "w", encoding="utf-8") as f:
                    for l in lines:
                        if l.strip() == line.strip():
                            f.write(self.sorting)
                        elif l.strip() == self.sorting.strip():
                            f.write(line)
                        else:
                            f.write(l)
                self.sorting = None
                for lbl in self.lbl_images:
                    lbl.config(bg="white")
                self.taglist_load()
            else:
                self.sorting = line
                label.config(bg="yellow")


if __name__ == "__main__":
    app = TagListApp()
    app.mainloop()