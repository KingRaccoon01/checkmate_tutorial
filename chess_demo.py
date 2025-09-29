# chess_demo_full.py
# Çalıştırmak için: pip install python-chess
import tkinter as tk
from tkinter import messagebox
import chess

# ----------------------------------------------------------
# Unicode haritası: python-chess'in piece.symbol() çıktısına göre
# ----------------------------------------------------------
UNICODE_PIECES = {
    'P': '\u2659', 'N': '\u2658', 'B': '\u2657', 'R': '\u2656', 'Q': '\u2655', 'K': '\u2654',
    'p': '\u265F', 'n': '\u265E', 'b': '\u265D', 'r': '\u265C', 'q': '\u265B', 'k': '\u265A'
}

# ----------------------------------------------------------
# Ana uygulama sınıfı
# ----------------------------------------------------------
class ChessDemoApp:
    def __init__(self, root):
        # Pencere ayarları
        self.root = root
        root.title("Satranç Mat Öğretici — Örnekler: Çoban Matı ve Kale Matı")
        self.sq_size = 60  # bir kare boyutu (piksel)
        self.board_px = self.sq_size * 8

        # Satranç tahtası mantığı için python-chess Board
        self.board = chess.Board()

        # Canvas: satranç tahtasını çizeceğimiz yer
        self.canvas = tk.Canvas(root, width=self.board_px, height=self.board_px)
        self.canvas.grid(row=0, column=0, rowspan=10, padx=10, pady=10)

        # Bilgi etiketi: kullanıcıya şu an ne olduğunu gösterir
        self.info_label = tk.Label(root, text="Hazır", anchor="w", justify="left")
        self.info_label.grid(row=0, column=1, sticky="nw", padx=10)

        # Butonlar: mat örnekleri ve kontrol düğmeleri
        tk.Button(root, text="Çoban Matı (Örnek)", command=self.start_scholars_mate).grid(row=1, column=1, sticky="ew", padx=10, pady=3)
        tk.Button(root, text="Kale Matı (Örnek)", command=self.start_rook_mate).grid(row=2, column=1, sticky="ew", padx=10, pady=3)
        tk.Button(root, text="Adım Adım İlerle", command=self.step_once).grid(row=3, column=1, sticky="ew", padx=10, pady=3)
        tk.Button(root, text="Otomatik Oynat", command=self.play_auto).grid(row=4, column=1, sticky="ew", padx=10, pady=3)
        tk.Button(root, text="Durdur", command=self.stop_auto).grid(row=5, column=1, sticky="ew", padx=10, pady=3)
        tk.Button(root, text="Sıfırla (Başlangıç Pozisyonu)", command=self.reset_board).grid(row=6, column=1, sticky="ew", padx=10, pady=3)

        # İç durumlar: gösterilecek hamleler, index, otomatik oynatma flag'i
        self.move_sequence = []   # UCI formatında hamleler listesi
        self.move_index = 0
        self.is_auto_play = False

        # Başlangıçta tahtayı çiz
        self.draw_board()

    # ----------------------------------------------------------
    # Tahtayı çizme fonksiyonu — kareler ve taşlar
    # ----------------------------------------------------------
    def draw_board(self, highlight=None):
        """
        highlight: None veya (from_square, to_square) şeklinde python-chess kare indeksleri
        """
        self.canvas.delete("all")
        light = "#F0D9B5"
        dark = "#B58863"

        # Rankleri 8'den 1'e, file'ları a'dan h'ye dönecek şekilde çiziyoruz
        for rank in range(7, -1, -1):
            for file in range(8):
                x0 = file * self.sq_size
                y0 = (7 - rank) * self.sq_size
                x1 = x0 + self.sq_size
                y1 = y0 + self.sq_size
                color = light if (file + rank) % 2 == 0 else dark
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)

                sq = chess.square(file, rank)
                piece = self.board.piece_at(sq)
                if piece:
                    symbol = piece.symbol()
                    glyph = UNICODE_PIECES.get(symbol, '?')
                    # Taşı kare ortasına Unicode metin olarak yazıyoruz
                    self.canvas.create_text(x0 + self.sq_size/2, y0 + self.sq_size/2,
                                            text=glyph, font=("Arial", int(self.sq_size*0.7)))

        # Eğer highlight verilmişse kaynak ve hedef kareleri vurgula
        if highlight:
            f, t = highlight
            fx = chess.square_file(f); fr = chess.square_rank(f)
            tx = chess.square_file(t); tr = chess.square_rank(t)
            # kaynak kare (sarı)
            x0 = fx * self.sq_size; y0 = (7 - fr) * self.sq_size
            x1 = x0 + self.sq_size; y1 = y0 + self.sq_size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="yellow", width=3)
            # hedef kare (kırmızı)
            x0 = tx * self.sq_size; y0 = (7 - tr) * self.sq_size
            x1 = x0 + self.sq_size; y1 = y0 + self.sq_size
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=3)

    # ----------------------------------------------------------
    # Çoban Matı örneğini yükleyen fonksiyon
    # ----------------------------------------------------------
    def start_scholars_mate(self):
        """
        Çoban Matı örneği için UCI hamle dizisi yüklüyoruz.
        Örnek hamleler: 1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#
        Bu liste uygulamada adım adım veya otomatik oynatma ile gösterilecek.
        """
        self.reset_board()  # önce tahtayı başlangıca al
        # UCI formatında hamle listesi
        self.move_sequence = ['e2e4', 'e7e5', 'd1h5', 'b8c6', 'f1c4', 'g8f6', 'h5f7']
        self.move_index = 0
        self.is_auto_play = False
        self.info_label.config(text="Çoban Matı yüklendi. 'Adım Adım İlerle' veya 'Otomatik Oynat' ile göster.")

    # ----------------------------------------------------------
    # Kale Matı örneğini yükleyen fonksiyon (FEN kullanarak pozisyon kurma)
    # ----------------------------------------------------------
    def start_rook_mate(self):
        """
        Kale Matı örneği için spesifik bir pozisyon (FEN) yüklüyoruz.
        Bu pozisyonda beyazın g7 -> g8 hamlesi (kale) mate verir.
        """
        # Bu FEN şu pozisyonu kurar (kısa açıklama kodun üstünde vardı):
        fen = "7k/5KRp/8/8/8/8/8/8 w - - 0 1"
        try:
            self.board = chess.Board(fen)
        except Exception as e:
            messagebox.showerror("Hata", f"FEN yüklenemedi: {e}")
            return

        # Gerekli tek hamle: kale g7'den g8'e
        self.move_sequence = ['g7g8']
        self.move_index = 0
        self.is_auto_play = False
        self.draw_board()
        self.info_label.config(text="Kale Matı pozisyonu yüklendi. 'Adım Adım İlerle' veya 'Otomatik Oynat' ile göster.")

    # ----------------------------------------------------------
    # Bir adım ilerletme: move_sequence'den bir hamleyi uygular
    # ----------------------------------------------------------
    def step_once(self):
        # Eğer hamle listesi boşsa kullanıcıyı uyar
        if not self.move_sequence:
            self.info_label.config(text="Önce bir mat seçin (ör. Çoban Matı veya Kale Matı).")
            return

        if self.move_index >= len(self.move_sequence):
            self.info_label.config(text="Tüm hamleler gösterildi.")
            return

        uci = self.move_sequence[self.move_index]
        move = chess.Move.from_uci(uci)
        try:
            # SAN (örn: Qxf7#) almak istiyoruz; hata olursa UCI göster
            san = self.board.san(move)
        except Exception:
            san = uci

        # Hamleyi tahtaya uygula
        try:
            self.board.push(move)
        except Exception as e:
            # Eğer hamle yasal değilse kullanıcıya bildir
            messagebox.showerror("Hata", f"Hamle uygulanamadı: {e}")
            return

        # Tahtayı çiz ve vurgula (kaynak -> hedef)
        self.draw_board(highlight=(move.from_square, move.to_square))
        self.move_index += 1
        self.info_label.config(text=f"Hamle {self.move_index}/{len(self.move_sequence)}: {san}")

    # ----------------------------------------------------------
    # Otomatik oynatma: her hamle arasında gecikme ile ilerler
    # ----------------------------------------------------------
    def play_auto(self, delay=800):
        # Eğer hamleler yoksa uyar
        if not self.move_sequence:
            messagebox.showinfo("Bilgi", "Önce bir mat seçin (ör. 'Çoban Matı' veya 'Kale Matı').")
            return
        if self.move_index >= len(self.move_sequence):
            self.info_label.config(text="Tüm hamleler zaten gösterildi. Sıfırla sonra tekrar deneyin.")
            return
        self.is_auto_play = True
        # İlk adımı başlat
        self._auto_step(delay)

    def _auto_step(self, delay):
        # Eğer otomatik oynatma iptal edilmişse dur
        if not self.is_auto_play:
            return
        if self.move_index < len(self.move_sequence):
            self.step_once()
            # after ile GUI'yi bloke etmeden tekrar çağırıyoruz
            self.root.after(delay, lambda: self._auto_step(delay))
        else:
            self.is_auto_play = False
            self.info_label.config(text="Otomatik oynatma bitti.")

    def stop_auto(self):
        # Otomatik oynatmayı durdurur
        self.is_auto_play = False
        self.info_label.config(text="Otomatik oynatma durduruldu.")

    # ----------------------------------------------------------
    # Tahtayı başlangıç pozisyonuna al ve tüm iç durumları sıfırla
    # ----------------------------------------------------------
    def reset_board(self):
        self.board = chess.Board()  # standard başlangıç pozisyonu
        self.move_sequence = []
        self.move_index = 0
        self.is_auto_play = False
        self.info_label.config(text="Tahta sıfırlandı (başlangıç pozisyonu).")
        self.draw_board()

# ----------------------------------------------------------
# Programı başlatma
# ----------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ChessDemoApp(root)
    root.mainloop()
