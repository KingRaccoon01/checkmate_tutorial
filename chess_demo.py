# chess_demo.py
import tkinter as tk
from tkinter import messagebox
import chess

# Unicode haritası: python-chess'teki piece.symbol() dönüşüne göre eşleme
UNICODE_PIECES = {
    'P': '\u2659', 'N': '\u2658', 'B': '\u2657', 'R': '\u2656', 'Q': '\u2655', 'K': '\u2654',
    'p': '\u265F', 'n': '\u265E', 'b': '\u265D', 'r': '\u265C', 'q': '\u265B', 'k': '\u265A'
}

class ChessDemoApp:
    def __init__(self, root):
        self.root = root
        root.title("Satranç Mat Öğretici — Örnek: Çoban Matı")
        self.sq_size = 60  # bir kare piksel boyutu
        self.board_px = self.sq_size * 8

        # python-chess Board nesnesi
        self.board = chess.Board()

        # Canvas: tahtayı çizmek için
        self.canvas = tk.Canvas(root, width=self.board_px, height=self.board_px)
        self.canvas.grid(row=0, column=0, rowspan=8, padx=10, pady=10)

        # Bilgi etiketi (şu anki hamle vs.)
        self.info_label = tk.Label(root, text="Hazır", anchor="w", justify="left")
        self.info_label.grid(row=0, column=1, sticky="nw", padx=10)

        # Butonlar: mat örnekleri ve kontrol
        tk.Button(root, text="Çoban Matı (Örnek)", command=self.start_scholars_mate).grid(row=1, column=1, sticky="ew", padx=10, pady=3)
        tk.Button(root, text="Adım Adım İlerle", command=self.step_once).grid(row=2, column=1, sticky="ew", padx=10, pady=3)
        tk.Button(root, text="Otomatik Oynat", command=self.play_auto).grid(row=3, column=1, sticky="ew", padx=10, pady=3)
        tk.Button(root, text="Sıfırla", command=self.reset_board).grid(row=4, column=1, sticky="ew", padx=10, pady=3)

        # İç durumlar
        self.move_sequence = []   # gösterilecek UCI hamleleri
        self.move_index = 0
        self.is_auto_play = False

        self.draw_board()

    def draw_board(self, highlight=None):
        """
        highlight: None veya (from_square, to_square) şeklinde int-square değerleri
        """
        self.canvas.delete("all")
        light = "#F0D9B5"
        dark = "#B58863"
        for rank in range(7, -1, -1):          # yukarıdan aşağıya: 8'den 1'e
            for file in range(8):              # soldan sağa: a'dan h'ye
                x0 = file * self.sq_size
                y0 = (7 - rank) * self.sq_size
                x1 = x0 + self.sq_size
                y1 = y0 + self.sq_size
                color = light if (file + rank) % 2 == 0 else dark
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)

                sq = chess.square(file, rank)  # python-chess kare indeksi
                piece = self.board.piece_at(sq)
                if piece:
                    symbol = piece.symbol()
                    glyph = UNICODE_PIECES.get(symbol, '?')
                    self.canvas.create_text(x0 + self.sq_size/2, y0 + self.sq_size/2,
                                            text=glyph, font=("Arial", int(self.sq_size*0.7)))

        # Highlight varsa (kaynak -> hedef)
        if highlight:
            f, t = highlight
            fx = chess.square_file(f); fr = chess.square_rank(f)
            tx = chess.square_file(t); tr = chess.square_rank(t)
            # dönüşüm: canvas y koordinatı için 7 - rank kullandık
            x0 = fx * self.sq_size; y0 = (7 - fr) * self.sq_size
            x1 = x0 + self.sq_size; y1 = y0 + self.sq_size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="yellow", width=3)

            x0 = tx * self.sq_size; y0 = (7 - tr) * self.sq_size
            x1 = x0 + self.sq_size; y1 = y0 + self.sq_size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=3)

    # Örnek: Çoban Matı hamleleri (UCI formatı)
    def start_scholars_mate(self):
        # Çoban matı (örnek): 1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#
        self.reset_board()
        self.move_sequence = ['e2e4', 'e7e5', 'd1h5', 'b8c6', 'f1c4', 'g8f6', 'h5f7']
        self.move_index = 0
        self.info_label.config(text="Çoban Matı yüklendi. 'Otomatik Oynat' veya 'Adım Adım İlerle' ile başlat.")

    def step_once(self):
        if self.move_index >= len(self.move_sequence):
            self.info_label.config(text="Tüm hamleler gösterildi.")
            return
        uci = self.move_sequence[self.move_index]
        move = chess.Move.from_uci(uci)
        # hamlenin SAN gösterimi için önce san alıyoruz
        try:
            san = self.board.san(move)
        except Exception:
            san = uci
        self.board.push(move)
        self.draw_board(highlight=(move.from_square, move.to_square))
        self.move_index += 1
        self.info_label.config(text=f"Hamle {self.move_index}: {san}")

    def play_auto(self, delay=800):
        if not self.move_sequence:
            messagebox.showinfo("Bilgi", "Önce bir mat seçin (ör. 'Çoban Matı').")
            return
        if self.move_index >= len(self.move_sequence):
            self.info_label.config(text="Tüm hamleler zaten gösterildi. Sıfırla sonra tekrar deneyin.")
            return
        self.is_auto_play = True
        self._auto_step(delay)

    def _auto_step(self, delay):
        if not self.is_auto_play:
            return
        if self.move_index < len(self.move_sequence):
            self.step_once()
            self.root.after(delay, lambda: self._auto_step(delay))
        else:
            self.is_auto_play = False
            self.info_label.config(text="Otomatik oynatma bitti.")

    def reset_board(self):
        self.board = chess.Board()
        self.move_sequence = []
        self.move_index = 0
        self.is_auto_play = False
        self.info_label.config(text="Tahta sıfırlandı.")
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessDemoApp(root)
    root.mainloop()
