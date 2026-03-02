from PIL import Image
import numpy as np
import re

class RGB565Converter:
    def __init__(self):
        pass

    def jpg_to_h(self, file_in, file_out, swap_bytes=True):
        """Convert JPG image to 16-bit RGB565 C header file with optional byte swap."""
        img = Image.open(file_in).convert('RGB')
        arr = np.array(img)

        # Convert RGB888 -> RGB565
        r = (arr[:, :, 0] >> 3).astype(np.uint16)  # 5 bits
        g = (arr[:, :, 1] >> 2).astype(np.uint16)  # 6 bits
        b = (arr[:, :, 2] >> 3).astype(np.uint16)  # 5 bits
        rgb565 = (r << 11) | (g << 5) | b  # RGB565 bit layout

        if swap_bytes:
            # Swap bytes: high byte <-> low byte
            rgb565 = ((rgb565 & 0xFF) << 8) | (rgb565 >> 8)

        # Flatten array
        rgb565_flat = rgb565.flatten()

        # Write to C header
        with open(file_out, 'w') as f:
            f.write(f"uint16_t image_data[{rgb565_flat.size}] = {{\n")
            for i, val in enumerate(rgb565_flat):
                f.write(f"0x{val:04X}")
                if i != rgb565_flat.size - 1:
                    f.write(", ")
                if (i + 1) % 12 == 0:
                    f.write("\n")
            f.write("\n};\n")
        print(f"{file_out} written successfully.")

    def h_to_jpg(self, file_in, width, height, file_out, swap_bytes=True):
        """Convert 16-bit RGB565 C header file back to JPG image with optional byte swap."""
        with open(file_in, 'r') as f:
            content = f.read()

        # Extract all 16-bit hex values
        hex_vals = re.findall(r'0x([0-9A-Fa-f]{4})', content)
        arr = np.array([int(h, 16) for h in hex_vals], dtype=np.uint16)

        if arr.size != width * height:
            raise ValueError(f"Data size {arr.size} does not match width*height {width*height}")

        if swap_bytes:
            # Swap bytes back
            arr = ((arr & 0xFF) << 8) | (arr >> 8)

        # Reshape to original image dimensions
        arr = arr.reshape((height, width))

        # Convert RGB565 -> RGB888
        r = ((arr >> 11) & 0x1F) << 3
        g = ((arr >> 5) & 0x3F) << 2
        b = (arr & 0x1F) << 3

        img_arr = np.stack([r, g, b], axis=2).astype(np.uint8)
        img = Image.fromarray(img_arr, 'RGB')
        img.save(file_out)
        print(f"{file_out} written successfully.")



# ===== Example Usage =====
converter = RGB565Converter()

# Convert JPG to .h
converter.jpg_to_h("legion.jpg", "RGB.h")

# Convert .h back to JPG (specify original width & height)
converter.h_to_jpg("RGB.h", width=128, height=160, file_out="RGBreconstructed.jpg")
