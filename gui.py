import threading, time
from tkinter import *
from tkinter import font as tkfont
from PIL import Image, ImageTk
from history import is_stale
from speech import recognize_speech


class PredictorApp:
    def __init__(self, root, config, trie, conn):
        self.root = root
        self.config = config
        self.trie = trie
        self.conn = conn

        self.root.title("Next Word Predictor")
        self.root.configure(bg="#2E2E2E")

        big_font = tkfont.Font(size=14)

        label_fg = "#FFFFFF"
        text_bg = "#1E1E1E"
        text_fg = "#FFFFFF"
        button_bg = "#3E3E3E"
        button_fg = "#FFFFFF"

        self.last_text = ""
        self.stop_flag = False

        self.label = Label(root, text="Type your text:", font=big_font,
                           bg=self.root["bg"], fg=label_fg)
        self.label.pack(pady=5)

        self.text_frame = Frame(root, bg=self.root["bg"])
        self.text_frame.pack(pady=5, fill=BOTH, expand=True)

        self.text = Text(self.text_frame, wrap=WORD, font=big_font, height=6,
                         bg=text_bg, fg=text_fg, insertbackground="white")
        self.text.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=5)

        self.scrollbar = Scrollbar(self.text_frame, command=self.text.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(yscrollcommand=self.scrollbar.set)

        self.button_frame = Frame(root, bg=self.root["bg"])
        self.button_frame.pack(pady=5)

        self.pred_buttons = []
        for _ in range(3):
            btn = Button(self.button_frame, text="", font=big_font, width=15,
                         bg=button_bg, fg=button_fg, activebackground="#555555")
            btn.pack(side=LEFT, padx=5)
            btn.pack_forget()
            self.pred_buttons.append(btn)

        # Mic icon
        mic_image = Image.open("mic.png").resize((24, 24))
        self.mic_icon = ImageTk.PhotoImage(mic_image)

        self.speech_btn = Button(root, text=" Speak", image=self.mic_icon, compound=LEFT,
                                 font=big_font, bg=button_bg, fg=button_fg,
                                 command=self.speech_to_text)
        self.speech_btn.pack(pady=5)

        self.history_label = Label(root, text="History:", font=big_font,
                                   bg=self.root["bg"], fg=label_fg)
        self.history_label.pack(pady=5)

        self.history_text = Text(root, wrap=WORD, font=big_font, height=6,
                                 bg="#2E2E2E", fg="#CCCCCC")
        self.history_text.pack(padx=10, pady=5, fill=BOTH, expand=True)

        self.clear_btn = Button(root, text="Clear", font=big_font, bg=button_bg, fg=button_fg,
                                command=self.clear_all)
        self.clear_btn.pack(pady=5)

        self.load_history()

        self.thread = threading.Thread(target=self.predict_loop)
        self.thread.daemon = True
        self.thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def speech_to_text(self):
        text = recognize_speech()
        if text:
            self.text.insert(END, f" {text}")
            self.last_text = ""  # force update

    def append_word(self, word):
        current_text = self.text.get("1.0", END).strip()
        if not current_text:
            self.text.insert(END, word)
        else:
            self.text.insert(END, f" {word}")
        self.cursor().execute("INSERT INTO history (text) VALUES (?)", (word,))
        self.conn.commit()
        self.load_history()
        self.last_text = ""  # force update

    def clear_all(self):
        self.text.delete("1.0", END)
        self.cursor().execute("DELETE FROM history")
        self.conn.commit()
        self.load_history()
        self.last_text = ""  # force update

    def load_history(self):
        self.history_text.delete("1.0", END)
        for row in self.cursor().execute("SELECT text, timestamp FROM history ORDER BY id DESC LIMIT 20"):
            self.history_text.insert(END, f"{row[0]}  [{row[1]}]\n")
        self.history_text.see(END)

    def cursor(self):
        return self.conn.cursor()

    def predict_loop(self):
        while not self.stop_flag:
            current_text = self.text.get("1.0", END).strip()
            if current_text != self.last_text:
                words = current_text.split()
                context = words[-2:] if len(words) >= 2 else words[-1:]
                if context:
                    preds = self.trie.predict(context)
                    if preds:
                        for i, (word, prob) in enumerate(preds):
                            color = self.get_color(prob)
                            self.pred_buttons[i].config(
                                text=f"{word}",
                                bg=color,
                                command=lambda w=word: self.append_word(w)
                            )
                            self.pred_buttons[i].pack(side=LEFT, padx=5)
                    else:
                        self.hide_buttons()
                else:
                    self.hide_buttons()
                self.last_text = current_text
            time.sleep(0.3)

    def hide_buttons(self):
        for btn in self.pred_buttons:
            btn.pack_forget()

    def get_color(self, prob):
        if prob >= 0.5: return "#064A05"
        elif prob >= 0.2: return "#A69107"
        else: return "#9C2F05"

    def on_close(self):
        self.stop_flag = True
        self.conn.close()
        self.root.destroy()
