import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import random

class PerceptronApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x800")

        self.num_features = 25  # Сітка 5х5
        self.weights = [round(random.uniform(-0.1, 0.1), 3) for _ in range(self.num_features)]
        self.bias = round(random.uniform(-0.1, 0.1), 3)
        self.learning_rate = 0.1
        self.step_count = 0

        self.current_vector = None
        self.current_img = None

        self._build_ui()

    def _extract_features(self, pil_img):
        img_gray = pil_img.convert("L")
        w, h = img_gray.size
        step_x, step_y = w / 5, h / 5
        abs_v = []

        for r in range(5):
            for c in range(5):
                sx, sy = int(c * step_x), int(r * step_y)
                ex = int((c + 1) * step_x) if c < 4 else w
                ey = int((r + 1) * step_y) if r < 4 else h
                count = sum(1 for y in range(sy, ey) for x in range(sx, ex) if img_gray.getpixel((x, y)) < 128)
                abs_v.append(count)

        m = max(abs_v) if max(abs_v) > 0 else 1
        norm_v = [round(v / m, 3) for v in abs_v]
        return abs_v, norm_v

    def _draw_grid(self, pil_img):
        preview = pil_img.copy().convert("RGB")
        preview.thumbnail((140, 140))
        draw = ImageDraw.Draw(preview)
        w, h = preview.size
        for i in range(1, 5):
            draw.line([(int(i * w / 5), 0), (int(i * w / 5), h)], fill="red", width=2)
            draw.line([(0, int(i * h / 5)), (w, int(i * h / 5))], fill="red", width=2)
        return preview

    def _build_ui(self):
        #налаштувань ваг
        cfg_frame = tk.LabelFrame(self.root, text="Стан та ваги перцептрона", font=("Arial", 10, "bold"))
        cfg_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(cfg_frame, text=f"Швидкість навчання r: {self.learning_rate}").pack(side=tk.LEFT, padx=10)
        self.lbl_step = tk.Label(cfg_frame, text="Крок навчання: 0")
        self.lbl_step.pack(side=tk.LEFT, padx=10)

        btn_init = tk.Button(cfg_frame, text="Скинути ваги", command=self.reset_weights)
        btn_init.pack(side=tk.LEFT, padx=10)

        self.txt_weights = tk.Text(cfg_frame, height=3, width=70, font=("Consolas", 8))
        self.txt_weights.pack(side=tk.LEFT, padx=10, pady=5)
        self._show_weights()

        #завантаження зображення
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_frame = tk.LabelFrame(main_frame, text="2. Тестовий образ", font=("Arial", 10, "bold"))
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        img_box = tk.Frame(left_frame, width=150, height=150, bg="#f0f0f0", relief=tk.SUNKEN, borderwidth=1)
        img_box.pack_propagate(False)
        img_box.pack(pady=10, padx=10)

        self.lbl_img = tk.Label(img_box, text="Немає фото", bg="#f0f0f0")
        self.lbl_img.pack(expand=True)

        tk.Button(left_frame, text="Завантажити образ", command=self.load_image).pack(fill=tk.X, padx=10, pady=5)

        #навчання з учителем
        right_frame = tk.LabelFrame(main_frame, text="3. Класифікація та корекція (Навчання з учителем)", font=("Arial", 10, "bold"))
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.txt_log = tk.Text(right_frame, height=12, font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ctrl_box = tk.Frame(right_frame)
        ctrl_box.pack(fill=tk.X, pady=5)

        tk.Button(ctrl_box, text="Обчислити вихід", bg="#cce5ff", font=("Arial", 10, "bold"), command=self.predict).pack(side=tk.LEFT, padx=5)

        tk.Label(ctrl_box, text="Бажаний клас (d):").pack(side=tk.LEFT, padx=5)
        self.target_var = tk.StringVar(value="1")
        cb_target = ttk.Combobox(ctrl_box, textvariable=self.target_var, values=["1 (Клас 1)", "0 (Клас 2)"], width=12, state="readonly")
        cb_target.pack(side=tk.LEFT, padx=5)

        tk.Button(ctrl_box, text="Корекція ваг (у разі помилки)", bg="#fdebd0", command=self.correct_weights).pack(side=tk.LEFT, padx=5)

    def _show_weights(self):
        self.txt_weights.delete("1.0", tk.END)
        self.txt_weights.insert(tk.END, f"W: {self.weights}\nBias: {self.bias}")

    def reset_weights(self):
        self.weights = [round(random.uniform(-0.1, 0.1), 3) for _ in range(self.num_features)]
        self.bias = round(random.uniform(-0.1, 0.1), 3)
        self.step_count = 0
        self.lbl_step.config(text="Крок навчання: 0")
        self._show_weights()
        self.txt_log.insert(tk.END, " Ваги перцептрона скинуто\n")

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Зображення", "*.bmp;*.png;*.jpg")])
        if not path:
            return
        img = Image.open(path)
        preview = self._draw_grid(img)
        self.photo = ImageTk.PhotoImage(preview)
        self.lbl_img.config(image=self.photo, text="")

        abs_v, norm_v = self._extract_features(img)
        self.current_vector = norm_v

        self.txt_log.insert(tk.END, f"\nЗавантажено образ.\nAbs: {abs_v}\nNorm: {norm_v}\n")
        self.txt_log.see(tk.END)

    def predict(self):
        if not self.current_vector:
            messagebox.showerror("Помилка", "Завантажте образ!")
            return
        # S = sum(w_i * x_i) + bias
        s = sum(w * x for w, x in zip(self.weights, self.current_vector)) + self.bias
        y = 1 if s >= 0 else 0

        self.last_y = y
        self.txt_log.insert(tk.END, f"Сума S = {s:.4f} -> Вихід y = {y} (Клас {1 if y==1 else 2})\n")
        self.txt_log.see(tk.END)

    def correct_weights(self):
        if not hasattr(self, 'last_y'):
            messagebox.showerror("Помилка", "Спочатку обчисліть вихід!")
            return

        d = 1 if "1" in self.target_var.get() else 0
        y = self.last_y
        error = d - y

        if error == 0:
            self.txt_log.insert(tk.END, ">> Рішення правильне! Ваги не коригуються.\n")
        else:
            self.step_count += 1
            # w_i(t+1) = w_i(t) + r * (d - y) * x_i
            self.weights = [round(w + self.learning_rate * error * x, 3) for w, x in zip(self.weights, self.current_vector)]
            self.bias = round(self.bias + self.learning_rate * error, 3)
            self.lbl_step.config(text=f"Крок навчання: {self.step_count}")
            self._show_weights()
            self.txt_log.insert(tk.END, f">> Помилка e = {error}. Ваги прокориговано (Крок {self.step_count}).\n")

        self.txt_log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PerceptronApp(root)
    root.mainloop()