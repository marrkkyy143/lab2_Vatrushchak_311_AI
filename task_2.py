
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw


class HopfieldHammingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Завдання 2: Мережі Хопфілда та Хемінга")
        self.root.geometry("1250x900")

        self.class_names = ["Клас 1", "Клас 2", "Клас 3"]

        self.raw_vectors = {}
        self.normalized_vectors = {}
        self.bipolar_vectors = {}

        self.template_photos = {}
        self.unknown_photo = None
        self.unknown_raw = None
        self.unknown_normalized = None
        self.unknown_bipolar = None

        self._build_ui()


    def _draw_grid(self, pil_img):
        preview = pil_img.copy().convert("RGB")
        preview.thumbnail((130, 130))

        draw = ImageDraw.Draw(preview)
        w, h = preview.size

        for i in range(1, 5):
            draw.line(
                [(int(i * w / 5), 0), (int(i * w / 5), h)],
                fill="red", width=2
            )
            draw.line(
                [(0, int(i * h / 5)), (w, int(i * h / 5))],
                fill="red", width=2
            )

        return preview



    def _extract_absolute(self, pil_img):
        img_gray = pil_img.convert("L")
        w, h = img_gray.size

        step_x = w / 5
        step_y = h / 5

        abs_vector = []

        for r in range(5):
            for c in range(5):

                sx = int(c * step_x)
                sy = int(r * step_y)

                ex = int((c + 1) * step_x) if c < 4 else w
                ey = int((r + 1) * step_y) if r < 4 else h

                count = 0

                for y in range(sy, ey):
                    for x in range(sx, ex):
                        if img_gray.getpixel((x, y)) < 128:
                            count += 1

                abs_vector.append(count)

        return abs_vector



    def _normalize_vector(self, vector):
        max_value = max(vector)

        if max_value == 0:
            return [0.0 for _ in vector]

        return [round(value / max_value, 3) for value in vector]


    def _to_bipolar(self, normalized_vector):
        return [
            1 if value >= 0.5 else -1
            for value in normalized_vector
        ]


    def _build_ui(self):



        tpl_frame = tk.LabelFrame(
            self.root,
            text="1. Еталонні образи (3 класи)",
            font=("Arial", 10, "bold")
        )

        tpl_frame.pack(fill=tk.X, padx=10, pady=5)

        self.tpl_labels = {}
        self.tpl_texts = {}

        for cname in self.class_names:

            col = tk.Frame(
                tpl_frame,
                relief=tk.GROOVE,
                borderwidth=1,
                padx=5,
                pady=5
            )

            col.pack(
                side=tk.LEFT,
                fill=tk.BOTH,
                expand=True,
                padx=4
            )

            tk.Label(
                col,
                text=cname,
                font=("Arial", 10, "bold")
            ).pack()

            box = tk.Frame(
                col,
                width=130,
                height=130,
                bg="#f0f0f0"
            )

            box.pack_propagate(False)
            box.pack(pady=3)

            lbl = tk.Label(box, text="Немає фото", bg="#f0f0f0")
            lbl.pack(expand=True)

            self.tpl_labels[cname] = lbl

            tk.Button(
                col,
                text=f"Завантажити {cname}",
                command=lambda cn=cname: self.load_template(cn)
            ).pack(fill=tk.X, pady=2)

            tbox = tk.Text(
                col,
                height=5,
                width=35,
                font=("Consolas", 8)
            )

            tbox.pack(fill=tk.X)
            self.tpl_texts[cname] = tbox



        test_frame = tk.LabelFrame(
            self.root,
            text="2. Класифікація невідомого образу",
            font=("Arial", 10, "bold")
        )

        test_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )

        left_test = tk.Frame(test_frame)
        left_test.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        t_box = tk.Frame(
            left_test,
            width=140,
            height=140,
            bg="#f0f0f0"
        )

        t_box.pack_propagate(False)
        t_box.pack(pady=5)

        self.lbl_unknown = tk.Label(
            t_box,
            text="Тестовий образ",
            bg="#f0f0f0"
        )

        self.lbl_unknown.pack(expand=True)

        tk.Button(
            left_test,
            text="Завантажити невідомий",
            command=self.load_unknown
        ).pack(fill=tk.X, pady=3)

        right_test = tk.Frame(test_frame)

        right_test.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5
        )

        ctrl = tk.Frame(right_test)
        ctrl.pack(fill=tk.X, pady=3)

        tk.Label(ctrl, text="Тип мережі:").pack(side=tk.LEFT, padx=5)

        self.net_var = tk.StringVar(value="Хопфілд")

        cb = ttk.Combobox(
            ctrl,
            textvariable=self.net_var,
            values=["Хопфілд", "Хемінг"],
            state="readonly",
            width=12
        )

        cb.pack(side=tk.LEFT, padx=5)

        tk.Button(
            ctrl,
            text="Запустити розпізнавання",
            bg="#d4efdf",
            font=("Arial", 10, "bold"),
            command=self.run_classification
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            ctrl,
            text="Очистити результати",
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=5)


        log_frame = tk.Frame(right_test)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.txt_log = tk.Text(
            log_frame,
            font=("Consolas", 9),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )

        self.txt_log.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.txt_log.yview)


    def load_template(self, cname):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Зображення", "*.bmp *.png *.jpg *.jpeg")
            ]
        )

        if not path:
            return

        try:
            img = Image.open(path)

            abs_vector = self._extract_absolute(img)

            normalized = self._normalize_vector(abs_vector)

            bipolar = self._to_bipolar(normalized)

            self.raw_vectors[cname] = abs_vector
            self.normalized_vectors[cname] = normalized
            self.bipolar_vectors[cname] = bipolar

            self.template_photos[cname] = ImageTk.PhotoImage(
                self._draw_grid(img)
            )

            self.tpl_labels[cname].config(
                image=self.template_photos[cname],
                text=""
            )

            self.tpl_texts[cname].delete("1.0", tk.END)

            self.tpl_texts[cname].insert(
                tk.END,
                f"Абсолютний вектор:\n{abs_vector}\n\n"
                f"Нормований вектор:\n{normalized}\n\n"
                f"Біполярний вектор:\n{bipolar}"
            )

            self.txt_log.insert(
                tk.END,
                f"\nЗавантажено еталон: {cname}\n"
                f"Абсолютний вектор: {abs_vector}\n"
                f"Нормований вектор: {normalized}\n"
                f"Біполярний вектор: {bipolar}\n"
            )

            self.txt_log.see(tk.END)

        except Exception as e:
            messagebox.showerror("Помилка", str(e))



    def load_unknown(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Зображення", "*.bmp *.png *.jpg *.jpeg")
            ]
        )

        if not path:
            return

        try:
            img = Image.open(path)

            self.unknown_raw = self._extract_absolute(img)

            self.unknown_normalized = self._normalize_vector(
                self.unknown_raw
            )

            self.unknown_bipolar = self._to_bipolar(
                self.unknown_normalized
            )

            self.unknown_photo = ImageTk.PhotoImage(
                self._draw_grid(img)
            )

            self.lbl_unknown.config(
                image=self.unknown_photo,
                text=""
            )

            self.txt_log.insert(
                tk.END,
                "\nЗАВАНТАЖЕНО НЕВІДОМИЙ ОБРАЗ\n"
                f"Абсолютний вектор:\n{self.unknown_raw}\n"
                f"Нормований вектор:\n{self.unknown_normalized}\n"
                f"Біполярний вектор:\n{self.unknown_bipolar}\n"
            )

            self.txt_log.see(tk.END)

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

  

    def clear_log(self):
        self.txt_log.delete("1.0", tk.END)

    def run_classification(self):

        if len(self.bipolar_vectors) != 3:
            messagebox.showerror(
                "Помилка",
                "Завантажте всі три еталонні образи!"
            )
            return

        if self.unknown_bipolar is None:
            messagebox.showerror(
                "Помилка",
                "Завантажте невідомий образ!"
            )
            return

        if self.net_var.get() == "Хопфілд":
            self._classify_hopfield()

        else:
            self._classify_hamming()

    #хопфілд

    def _classify_hopfield(self):

        self.txt_log.insert(
            tk.END,
            "\n\n========== МЕРЕЖА ХОПФІЛДА ==========\n"
        )

        N = 25
        patterns = [
            self.bipolar_vectors[c]
            for c in self.class_names
        ]

        K = len(patterns)



        W = [[0.0 for _ in range(N)] for _ in range(N)]

        for i in range(N):
            for j in range(N):

                if i != j:

                    W[i][j] = sum(
                        patterns[k][i] * patterns[k][j]
                        for k in range(K)
                    ) / N

        self.txt_log.insert(
            tk.END,
            "\nМатриця ваг Хопфілда W (25x25):\n"
        )

        for row in W:
            self.txt_log.insert(
                tk.END,
                " ".join(f"{v:6.2f}" for v in row) + "\n"
            )


        Y = list(self.unknown_bipolar)

        max_iter = 100
        stabilized = False

        self.txt_log.insert(
            tk.END,
            "\nПочатковий стан мережі:\n"
            f"{Y}\n"
        )

        for it in range(max_iter):

            Y_next = []

            for j in range(N):

                S = sum(
                    W[i][j] * Y[i]
                    for i in range(N)
                )

                Y_next.append(1 if S >= 0 else -1)

            if Y_next == Y:

                stabilized = True

                self.txt_log.insert(
                    tk.END,
                    f"\nМережа стабілізувалася за {it + 1} ітерацій.\n"
                )

                break

            Y = Y_next

        if not stabilized:

            self.txt_log.insert(
                tk.END,
                "\nДосягнуто максимальної кількості ітерацій.\n"
            )

        self.txt_log.insert(
            tk.END,
            f"\nВідновлений вектор:\n{Y}\n"
        )


        diffs = {}

        for cname, vec in self.bipolar_vectors.items():

            distance = sum(
                1 for a, b in zip(Y, vec)
                if a != b
            )

            diffs[cname] = distance

        best_class = min(diffs, key=diffs.get)

        self.txt_log.insert(
            tk.END,
            "\nВідстані до еталонів:\n"
        )

        for cname, distance in diffs.items():

            self.txt_log.insert(
                tk.END,
                f"{cname}: {distance} відмінностей\n"
            )

        self.txt_log.insert(
            tk.END,
            "\nРЕЗУЛЬТАТ ХОПФІЛДА:\n"
            f"Об'єкт належить до -> {best_class}\n"
        )

        self.txt_log.see(tk.END)

    #хемінг

    def _classify_hamming(self):

        self.txt_log.insert(
            tk.END,
            "\n\n========== МЕРЕЖА ХЕМІНГА ==========\n"
        )

        N = 25
        K = 3

        patterns = [
            self.bipolar_vectors[c]
            for c in self.class_names
        ]


        W1 = [
            [patterns[k][i] / 2.0 for i in range(N)]
            for k in range(K)
        ]

        b1 = N / 2.0

        self.txt_log.insert(
            tk.END,
            "\nМатриця ваг першого шару W1 (3x25):\n"
        )

        for k in range(K):

            self.txt_log.insert(
                tk.END,
                f"{self.class_names[k]}: "
                + " ".join(
                    f"{v:5.1f}" for v in W1[k]
                )
                + "\n"
            )

        self.txt_log.insert(
            tk.END,
            f"\nПорогове зміщення b = {b1}\n"
        )


        Y1 = []

        for k in range(K):

            s = sum(
                W1[k][i] * self.unknown_bipolar[i]
                for i in range(N)
            ) + b1

            Y1.append(s)

        self.txt_log.insert(
            tk.END,
            "\nВиходи першого шару:\n"
        )

        for k in range(K):

            self.txt_log.insert(
                tk.END,
                f"{self.class_names[k]}: {Y1[k]:.2f}\n"
            )


        eps = 1.0 / (K + 1)

        Y2 = list(Y1)

        self.txt_log.insert(
            tk.END,
            f"\nКоефіцієнт гальмування eps = {eps:.3f}\n"
        )

        max_iter = 100
        stabilized = False

        for it in range(max_iter):

            Y2_next = []

            for k in range(K):

                inhibition = eps * sum(
                    Y2[j]
                    for j in range(K)
                    if j != k
                )

                value = Y2[k] - inhibition

                Y2_next.append(max(0.0, value))

            non_zero = sum(
                1 for v in Y2_next if v > 0
            )

            Y2 = Y2_next

            if non_zero <= 1:

                stabilized = True
                break

        self.txt_log.insert(
            tk.END,
            f"\nMAXNET завершив роботу за {it + 1} ітерацій.\n"
        )

        if not stabilized:

            self.txt_log.insert(
                tk.END,
                "Увага: не вдалося отримати єдиний активний нейрон.\n"
            )


        max_val = max(Y2)
        winner_idx = Y2.index(max_val)

        best_class = self.class_names[winner_idx]

        self.txt_log.insert(
            tk.END,
            "\nСтан другого шару після гальмування:\n"
        )

        for k in range(K):

            self.txt_log.insert(
                tk.END,
                f"{self.class_names[k]}: {Y2[k]:.4f}\n"
            )



        self.txt_log.insert(
            tk.END,
            "\nВідстані Хемінга до еталонів:\n"
        )

        for cname, vec in self.bipolar_vectors.items():

            distance = sum(
                1 for a, b in zip(
                    self.unknown_bipolar, vec
                )
                if a != b
            )

            self.txt_log.insert(
                tk.END,
                f"{cname}: {distance} відмінностей\n"
            )

        self.txt_log.insert(
            tk.END,
            "\nРЕЗУЛЬТАТ ХЕМІНГА:\n"
            f"Об'єкт належить до -> {best_class}\n"
        )

        self.txt_log.see(tk.END)


if __name__ == "__main__":

    root = tk.Tk()

    app = HopfieldHammingApp(root)

    root.mainloop()
