import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

class TextToVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("テキスト動画作成アプリ")
        self.root.geometry("700x750")
        
        # テキストファイルパス
        self.text_file_path = tk.StringVar()
        
        # 設定変数
        self.duration_per_line = tk.DoubleVar(value=3.0)
        self.fps = tk.IntVar(value=30)
        self.font_size = tk.IntVar(value=60)
        self.selected_font = tk.StringVar()
        self.bg_color = tk.StringVar(value="#000000")
        self.text_color = tk.StringVar(value="#FFFFFF")
        
        # 新機能：動画サイズ
        self.video_width = tk.IntVar(value=1920)
        self.video_height = tk.IntVar(value=1080)
        self.preset_size = tk.StringVar(value="1920x1080")
        
        # 新機能：フォント読み込み設定
        self.load_all_fonts = tk.BooleanVar(value=False)
        
        # 新機能：自動改行
        self.auto_wrap = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_available_fonts()
    
    def create_widgets(self):
        # テキストファイル選択
        file_frame = tk.LabelFrame(self.root, text="テキストファイル選択", padx=10, pady=10)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Entry(file_frame, textvariable=self.text_file_path, width=50).pack(side="left", padx=5)
        tk.Button(file_frame, text="参照", command=self.select_text_file).pack(side="left")
        

        
        # 設定
        settings_frame = tk.LabelFrame(self.root, text="設定", padx=10, pady=10)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 動画サイズ設定（新機能）
        video_size_frame = tk.LabelFrame(settings_frame, text="動画サイズ", padx=10, pady=5)
        video_size_frame.pack(fill="x", pady=5)
        
        preset_frame = tk.Frame(video_size_frame)
        preset_frame.pack(fill="x", pady=2)
        tk.Label(preset_frame, text="プリセット:").pack(side="left")
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_size, 
                                    values=["1920x1080 (Full HD)", "1280x720 (HD)", 
                                           "3840x2160 (4K)", "640x480 (SD)", "カスタム"],
                                    width=20, state="readonly")
        preset_combo.pack(side="left", padx=5)
        preset_combo.bind("<<ComboboxSelected>>", self.on_preset_change)
        
        size_frame = tk.Frame(video_size_frame)
        size_frame.pack(fill="x", pady=2)
        tk.Label(size_frame, text="幅:").pack(side="left")
        tk.Spinbox(size_frame, from_=320, to=7680, increment=10, 
                   textvariable=self.video_width, width=8).pack(side="left", padx=5)
        tk.Label(size_frame, text="高さ:").pack(side="left", padx=(10, 0))
        tk.Spinbox(size_frame, from_=240, to=4320, increment=10, 
                   textvariable=self.video_height, width=8).pack(side="left", padx=5)
        
        # 表示秒数
        duration_frame = tk.Frame(settings_frame)
        duration_frame.pack(fill="x", pady=5)
        tk.Label(duration_frame, text="1行あたりの表示秒数:").pack(side="left")
        tk.Spinbox(duration_frame, from_=0.5, to=60.0, increment=0.5, 
                   textvariable=self.duration_per_line, width=10).pack(side="left", padx=5)
        tk.Label(duration_frame, text="秒").pack(side="left")
        
        # FPS
        fps_frame = tk.Frame(settings_frame)
        fps_frame.pack(fill="x", pady=5)
        tk.Label(fps_frame, text="動画のFPS:").pack(side="left")
        tk.Spinbox(fps_frame, from_=1, to=60, increment=1, 
                   textvariable=self.fps, width=10).pack(side="left", padx=5)
        
        # フォントサイズ
        font_size_frame = tk.Frame(settings_frame)
        font_size_frame.pack(fill="x", pady=5)
        tk.Label(font_size_frame, text="フォントサイズ:").pack(side="left")
        tk.Spinbox(font_size_frame, from_=20, to=200, increment=5, 
                   textvariable=self.font_size, width=10).pack(side="left", padx=5)
        
        # フォント選択
        font_frame = tk.Frame(settings_frame)
        font_frame.pack(fill="x", pady=5)
        tk.Label(font_frame, text="フォント:").pack(side="left")
        self.font_combo = ttk.Combobox(font_frame, textvariable=self.selected_font, 
                                       width=30, state="readonly")
        self.font_combo.pack(side="left", padx=5)
        
        # フォント読み込み設定（新機能）
        font_load_frame = tk.Frame(settings_frame)
        font_load_frame.pack(fill="x", pady=5)
        tk.Checkbutton(font_load_frame, text="フォントフォルダ内のすべてのフォントを読み込む", 
                      variable=self.load_all_fonts, 
                      command=self.reload_fonts).pack(side="left")
        
        # 色設定
        color_frame = tk.Frame(settings_frame)
        color_frame.pack(fill="x", pady=5)
        
        tk.Label(color_frame, text="背景色:").pack(side="left")
        tk.Entry(color_frame, textvariable=self.bg_color, width=10).pack(side="left", padx=5)
        tk.Button(color_frame, text="選択", command=self.choose_bg_color).pack(side="left")
        
        tk.Label(color_frame, text="文字色:").pack(side="left", padx=(20, 0))
        tk.Entry(color_frame, textvariable=self.text_color, width=10).pack(side="left", padx=5)
        tk.Button(color_frame, text="選択", command=self.choose_text_color).pack(side="left")
        

        tk.Checkbutton(settings_frame, text="テキストが画面からはみ出す場合、自動改行する", 
                      variable=self.auto_wrap).pack(anchor="w", pady=2)
        
        # プログレスバー
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_label = tk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill="x", pady=5)
        
        # 実行ボタン
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="動画を作成", command=self.create_video, 
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 padx=20, pady=10).pack()
    
    def on_preset_change(self, event=None):
        preset = self.preset_size.get()
        if preset == "1920x1080 (Full HD)":
            self.video_width.set(1920)
            self.video_height.set(1080)
        elif preset == "1280x720 (HD)":
            self.video_width.set(1280)
            self.video_height.set(720)
        elif preset == "3840x2160 (4K)":
            self.video_width.set(3840)
            self.video_height.set(2160)
        elif preset == "640x480 (SD)":
            self.video_width.set(640)
            self.video_height.set(480)
        # "カスタム"の場合は何もしない
    
    def reload_fonts(self):
        """フォント読み込み設定が変更されたときに再読み込み"""
        self.load_available_fonts()
    
    def load_available_fonts(self):
        fonts = []
        self.font_paths = {}
        
        if self.load_all_fonts.get():
            # すべてのフォントを自動スキャン
            font_dirs = []
            
            # Windows
            if os.path.exists("C:\\Windows\\Fonts\\"):
                font_dirs.append("C:\\Windows\\Fonts\\")
            
            # macOS
            if os.path.exists("/System/Library/Fonts/"):
                font_dirs.append("/System/Library/Fonts/")
            if os.path.exists("/Library/Fonts/"):
                font_dirs.append("/Library/Fonts/")
            
            # Linux
            if os.path.exists("/usr/share/fonts/"):
                font_dirs.append("/usr/share/fonts/")
            
            for font_dir in font_dirs:
                for root_dir, dirs, files in os.walk(font_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.ttc', '.otf')):
                            font_path = os.path.join(root_dir, file)
                            font_name = os.path.splitext(file)[0]
                            
                            # 重複チェック
                            if font_name not in self.font_paths:
                                fonts.append(font_name)
                                self.font_paths[font_name] = font_path
        else:
            # デフォルト：厳選されたフォントのみ
            windows_fonts = [
                ("MS Gothic", "C:\\Windows\\Fonts\\msgothic.ttc"),
                ("MS Mincho", "C:\\Windows\\Fonts\\msmincho.ttc"),
                ("Meiryo", "C:\\Windows\\Fonts\\meiryo.ttc"),
                ("Yu Gothic", "C:\\Windows\\Fonts\\yugothic.ttf"),
                ("Arial", "C:\\Windows\\Fonts\\arial.ttf"),
                ("Times New Roman", "C:\\Windows\\Fonts\\times.ttf"),
            ]
            
            mac_fonts = [
                ("Hiragino Sans", "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"),
                ("Hiragino Mincho", "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"),
                ("Arial", "/System/Library/Fonts/Supplemental/Arial.ttf"),
                ("Times New Roman", "/System/Library/Fonts/Supplemental/Times New Roman.ttf"),
            ]
            
            linux_fonts = [
                ("Noto Sans CJK JP", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
                ("Noto Serif CJK JP", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"),
                ("DejaVu Sans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]
            
            all_fonts = windows_fonts + mac_fonts + linux_fonts
            
            for font_name, font_path in all_fonts:
                if os.path.exists(font_path):
                    fonts.append(font_name)
                    self.font_paths[font_name] = font_path
        
        if fonts:
            fonts.sort()  # アルファベット順にソート
            self.font_combo['values'] = fonts
            if not self.selected_font.get() or self.selected_font.get() not in fonts:
                self.selected_font.set(fonts[0])
        else:
            self.font_combo['values'] = ["Default"]
            self.selected_font.set("Default")
    
    def select_text_file(self):
        file = filedialog.askopenfilename(
            title="テキストファイルを選択",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file:
            self.text_file_path.set(file)
    
    def select_bg_image(self):
        file = filedialog.askopenfilename(
            title="背景画像を選択",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if file:
            self.bg_image_path.set(file)
    
    def choose_bg_color(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="背景色を選択")
        if color[1]:
            self.bg_color.set(color[1])
    
    def choose_text_color(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="文字色を選択")
        if color[1]:
            self.text_color.set(color[1])
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def load_font(self):
        font_name = self.selected_font.get()
        font_size = self.font_size.get()
        
        if font_name in self.font_paths:
            try:
                return ImageFont.truetype(self.font_paths[font_name], font_size)
            except:
                pass
        
        return ImageFont.load_default()
    
    def wrap_text(self, text, font, max_width):
        """テキストを指定幅で自動改行"""
        lines = []
        words = text
        
        # 1文字ずつチェックして改行
        current_line = ""
        for char in words:
            test_line = current_line + char
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def create_text_frame(self, text, video_size):
        # 単色背景
        bg_color_rgb = self.hex_to_rgb(self.bg_color.get())
        img = Image.new('RGB', video_size, bg_color_rgb)
        
        draw = ImageDraw.Draw(img)
        font = self.load_font()
        text_color_rgb = self.hex_to_rgb(self.text_color.get())
        
        # 自動改行が有効な場合
        if self.auto_wrap.get():
            margin = 40  # 左右のマージン
            max_width = video_size[0] - (margin * 2)
            lines = self.wrap_text(text, font, max_width)
            
            # 複数行のテキストを描画
            total_height = 0
            line_heights = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
                total_height += line_height
            
            # 行間を追加
            line_spacing = 10
            total_height += line_spacing * (len(lines) - 1)
            
            # 垂直中央揃えの開始位置
            y = (video_size[1] - total_height) // 2
            
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (video_size[0] - text_width) // 2
                
                draw.text((x, y), line, font=font, fill=text_color_rgb)
                y += line_heights[i] + line_spacing
        else:
            # 自動改行なし（元の動作）
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 中央配置
            x = (video_size[0] - text_width) // 2
            y = (video_size[1] - text_height) // 2
            
            draw.text((x, y), text, font=font, fill=text_color_rgb)
        
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    def create_video(self):
        text_file = self.text_file_path.get()
        if not text_file or not os.path.exists(text_file):
            messagebox.showerror("エラー", "有効なテキストファイルを選択してください")
            return
        
        # テキストを読み込み
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except:
            messagebox.showerror("エラー", "テキストファイルの読み込みに失敗しました")
            return
        
        if not lines:
            messagebox.showerror("エラー", "テキストファイルが空です")
            return
        
        # 出力ファイル名を選択
        output_file = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            title="保存先を選択"
        )
        
        if not output_file:
            return
        
        try:
            # カスタム動画サイズを使用
            video_size = (self.video_width.get(), self.video_height.get())
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = self.fps.get()
            out = cv2.VideoWriter(output_file, fourcc, fps, video_size)
            
            frames_per_line = int(self.duration_per_line.get() * fps)
            total_lines = len(lines)
            
            self.progress_bar['maximum'] = total_lines
            self.progress_bar['value'] = 0
            
            for idx, line in enumerate(lines):
                self.progress_label.config(text=f"処理中: {idx+1}/{total_lines} - {line[:50]}...")
                self.root.update()
                
                # フレームを作成
                frame = self.create_text_frame(line, video_size)
                
                # フレームを追加
                for _ in range(frames_per_line):
                    out.write(frame)
                
                self.progress_bar['value'] = idx + 1
                self.root.update()
            
            out.release()
            
            self.progress_label.config(text="完了!")
            messagebox.showinfo("完了", f"動画を作成しました:\n{output_file}")
            
        except Exception as e:
            messagebox.showerror("エラー", f"動画作成中にエラーが発生しました:\n{str(e)}")
            self.progress_label.config(text="エラー")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToVideoApp(root)
    root.mainloop()