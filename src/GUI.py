import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import pickle
import LZW
import math


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LZW Image Compressor")
        self.root.geometry("600x500")
        self.image_path = None
        self.compressed_data = None
        self.max_bits = 16

        # Frame for buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Buttons
        self.upload_btn = tk.Button(self.button_frame, text="Upload Image", command=self.upload_image)
        self.upload_btn.grid(row=0, column=0, padx=5)
        self.compress_btn = tk.Button(self.button_frame, text="Compress Image", command=self.compress_image)
        self.compress_btn.grid(row=0, column=1, padx=5)
        self.download_btn = tk.Button(self.button_frame, text="Download Compressed", command=self.download_compressed)
        self.download_btn.grid(row=0, column=2, padx=5)
        self.upload_compressed_btn = tk.Button(self.button_frame, text="Upload Compressed File", command=self.upload_compressed)
        self.upload_compressed_btn.grid(row=0, column=3, padx=5)

        # Max bit input
        self.max_bits_frame = tk.Frame(root)
        self.max_bits_frame.pack(pady=10)
        self.max_bits_label = tk.Label(self.max_bits_frame, text="Max Bits (8-16):")
        self.max_bits_label.grid(row=0, column=0, padx=5)
        self.max_bits_entry = tk.Entry(self.max_bits_frame, width=5)
        self.max_bits_entry.grid(row=0, column=1, padx=5)
        self.max_bits_entry.insert(0, "16")  # Default value

        # Information label
        self.info_label = tk.Label(root, text="")
        self.info_label.pack(pady=10)

        # Canvas
        self.canvas = tk.Canvas(root, width=500, height=300, bg="gray")
        self.canvas.pack()

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.info_label.config(text="Image uploaded: " + os.path.basename(file_path))

    def compress_image(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return

        try:
            self.max_bits = int(self.max_bits_entry.get())
            if self.max_bits < 8 or self.max_bits > 16:
                raise ValueError("Max bits must be between 8 and 12.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid max bits value: {e}")
            return

        # Open image and get pixel data
        img = Image.open(self.image_path)
        mode = img.mode
        if mode != "L":
            img = img.convert("RGB")
        pixels = list(img.getdata())

        if mode == "L":
            # For grayscale, one channel
            pixel_data = "".join(chr(pixel) for pixel in pixels)
        else:
            # For RGB, three channels
            pixel_data = "".join(chr(value) for pixel in pixels for value in pixel)

        compressed = LZW.compress(pixel_data, self.max_bits)
        self.compressed_data = (compressed, mode, img.size)  # Simpan mode dan ukuran

        original_size = len(pixel_data) * 8

        # Count compressed size
        current_bits = 8
        compressed_size = 0
        for code in compressed:
            if code >= (1 << current_bits):
                current_bits += 1
            compressed_size += current_bits

        compression_ratio = compressed_size / original_size * 100
        self.info_label.config(text=f"Compression complete! \nOriginal size: {original_size} bits ({math.ceil(original_size/8)} bytes) \nCompressed size: {compressed_size} bits ({math.ceil(compressed_size/8)} bytes) \nCompression Ratio: {compression_ratio:.2f}%")

    def download_compressed(self):
        if not self.compressed_data:
            messagebox.showwarning("Warning", "No compressed data to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".lzw", filetypes=[("LZW Compressed Files", "*.lzw")])
        if file_path:
            with open(file_path, "wb") as comp_file:
                pickle.dump(self.compressed_data, comp_file)
            messagebox.showinfo("Info", "Compressed file saved successfully!")

    def upload_compressed(self):
        file_path = filedialog.askopenfilename(filetypes=[("LZW Compressed Files", "*.lzw")])
        if file_path:
            try:
                self.max_bits = int(self.max_bits_entry.get())
                if self.max_bits < 8 or self.max_bits > 16:
                    raise ValueError("Max bits must be between 8 and 16.")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid max bits value: {e}")
                return

            with open(file_path, "rb") as comp_file:
                compressed_data, mode, size = pickle.load(comp_file)

            decompressed_data = LZW.decompress(compressed_data, self.max_bits)

            if mode == "L":
                # For grayscale
                pixels = [ord(char) for char in decompressed_data]
            else:
                # For RGB
                pixels = [
                    tuple(ord(decompressed_data[i + j]) for j in range(3))
                    for i in range(0, len(decompressed_data), 3)
                ]

            # Create image from pixel data
            img = Image.new(mode, size)
            img.putdata(pixels)
            img_path = "decompressed_image.png"
            img.save(img_path)
            self.display_image(img_path)
            self.info_label.config(text="Decompressed image displayed!")


    def display_image(self, path):
        img = Image.open(path)
        img.thumbnail((500, 300))
        img_tk = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(250, 150, image=img_tk)
        self.canvas.image = img_tk
