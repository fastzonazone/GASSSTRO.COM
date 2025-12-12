import cv2
import numpy as np
from stl import mesh
import os
import logging

class LogoConverter:
    def __init__(self):
        self.target_size = (1000, 1000) # Standardize processing resolution
        self.stamp_thickness = 2.0      # Base thickness
        self.relief_height = 5.0        # Embossing height (Updated for deeper impression)
        self.base_padding = 10          # Padding around logo

    def process_image(self, image_path):
        """
        Reads an image, enhances contrast, and returns a binary mask.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        # 1. Resize if too large/small to standardize processing time
        h, w = img.shape
        scale = min(self.target_size[0] / w, self.target_size[1] / h)
        if scale < 1.0:
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # 2. Enhance Contrast (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img)

        # 3. Denoise and Smooth (Anti-Aliasing)
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 30, 7, 21)
        
        # Blur slightly to create smooth transitions for threshold
        smoothed = cv2.GaussianBlur(denoised, (5, 5), 0)

        # 4. Binarize (Adaptive Thresholding)
        # Inverts so logo is white (255) and background is black (0) usually
        # But for stamps, we want the "dark" part of the image to be raised usually?
        # Let's assume input is dark logo on light background.
        # Adaptive threshold gives us edges/regions.
        binary = cv2.adaptiveThreshold(
            smoothed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 41, 5
        )

        # 5. Cleanup
        kernel = np.ones((3, 3), np.uint8)
        # OPEN: Erosion followed by Dilation (removes noise)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        # CLOSE: Dilation followed by Erosion (closes gaps)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

        return cleaned

    def generate_stl(self, image_path, output_path):
        """
        Generates a contoured STL (Input Shape + Offset Base).
        """
        try:
            # 1. Get binary masks
            logo_mask = self.process_image(image_path)
            
            # 2. Resize to printable resolution (~1000px max dim for High Fidelity)
            # 1000px on 60mm = 0.06mm/pixel (very high quality)
            h, w = logo_mask.shape
            max_dim = 1000
            scale = min(max_dim / w, max_dim / h)
            
            if scale < 1.0:
                new_w, new_h = int(w * scale), int(h * scale)
                logo_mask = cv2.resize(logo_mask, (new_w, new_h), interpolation=cv2.INTER_LINEAR) # Linear better for downsizing before thresh
            
            # Re-binarize after resize to keep sharp edges but at high res
            _, logo_mask = cv2.threshold(logo_mask, 127, 255, cv2.THRESH_BINARY)
            
            # 2.5. MIRROR the logo horizontally for stamp printing
            # When the stamp is pressed, it will be flipped, so we pre-flip it here
            logo_mask = cv2.flip(logo_mask, 1)  # flipCode=1 means horizontal flip
            
            # 3. Create Base Mask (Dilate/Offset)
            # Kernel size roughly 2-3mm.
            # If image represents 60mm width and is 1000px wide -> 1mm ~ 16px.
            # 3mm padding ~ 50px.
            padding_px = int(50 * (scale if scale < 1.0 else 1.0)) 
            kernel = np.ones((padding_px, padding_px), np.uint8)
            base_mask = cv2.dilate(logo_mask, kernel, iterations=1)
            
            # Ensure Clean output (fill holes in base to make it a solid handle)
            # cv2.floodFill could work, or just heavy closing
            close_kernel = np.ones((padding_px, padding_px), np.uint8)
            base_mask = cv2.morphologyEx(base_mask, cv2.MORPH_CLOSE, close_kernel)

            # 4. Generate Meshes
            # Physical Dimensions: Let's normalize largest dimension to 60mm
            pixel_scale = 60.0 / max(logo_mask.shape)
            
            logging.info("Generating Base Mesh...")
            base_mesh = self.mask_to_mesh(base_mask, 0.0, self.stamp_thickness, pixel_scale)
            
            logging.info("Generating Logo Relief Mesh...")
            # Logo sits ON TOP of base (start_z = stamp_thickness)
            logo_mesh = self.mask_to_mesh(logo_mask, self.stamp_thickness, self.stamp_thickness + self.relief_height, pixel_scale)
            
            # 5. Combine and Save
            # Concatenate data
            combined_data = np.concatenate([base_mesh.data, logo_mesh.data])
            combined_mesh = mesh.Mesh(combined_data)
            
            combined_mesh.save(output_path)
            logging.info(f"STL Saved: {output_path}")
            
        except Exception as e:
            logging.error(f"STL Gen Error: {e}")
            raise

    def mask_to_mesh(self, mask, z_bottom, z_top, scale):
        """
        Converts a binary mask to a solid 3D volume (extrusion) efficiently.
        """
        h, w = mask.shape
        # Pad mask with 0 to handle boundary edges easily
        padded = np.pad(mask, 1, mode='constant', constant_values=0)
        
        # Identify pixels that are solid (1)
        # We need (y, x) indices
        y_idxs, x_idxs = np.nonzero(padded)
        
        # We process 'padded' coordinates. Real image coords are (x-1, y-1)
        
        # 1. Top and Bottom Faces
        # Each pixel = 2 triangles (quad)
        # Total solid pixels
        num_pixels = len(y_idxs)
        
        # Vertices logic:
        # P0=(x,y), P1=(x+1,y), P2=(x+1,y+1), P3=(x,y+1)
        # Scaled.
        
        # Let's use vectorized approach for walls.
        # Walls exist where pixel is 1 and neighbor is 0.
        
        # Neighbors: Up, Down, Left, Right
        # Slices of padded array
        center = padded[1:-1, 1:-1]
        top    = padded[0:-2, 1:-1]
        bottom = padded[2:,   1:-1]
        left   = padded[1:-1, 0:-2]
        right  = padded[1:-1, 2:]
        
        # Booleans
        is_solid = (center > 0)
        
        # Edges
        edge_top    = is_solid & (top == 0)
        edge_bottom = is_solid & (bottom == 0)
        edge_left   = is_solid & (left == 0)
        edge_right  = is_solid & (right == 0)
        
        # Collect faces
        faces = []
        
        # --- Helper to create quads ---
        # returns list of (P0, P1, P2), (P0, P2, P3)
        # We need physical coords.
        # x, y are grid indices (0..w-1)
        
        # --- Top Surface (Z = z_top) ---
        # All solid pixels have a top
        ys, xs = np.nonzero(is_solid)
        
        # Vectorize? To avoid python loops for 100k pixels
        # Construct vertices array for all quads
        # n_quads = len(ys)
        # P0 = (xs, ys)
        # P1 = (xs+1, ys)
        # P2 = (xs+1, ys+1)
        # P3 = (xs, ys+1)
        
        # Convert to float and scale
        X = xs * scale
        Y = (h - 1 - ys) * scale # Flip Y for 3D
        S = scale
        
        P0 = np.column_stack((X, Y, np.full_like(X, z_top)))
        P1 = np.column_stack((X + S, Y, np.full_like(X, z_top)))
        P2 = np.column_stack((X + S, Y - S, np.full_like(X, z_top))) # Y goes down in 3D if we flipped?
        # Wait, if y index increases -> image goes down.
        # In 3D:
        # ys=0 (top of image) -> Y=High
        # ys=h (bottom) -> Y=Low
        # So P0(x,y) -> (x*s, (h-y)*s)
        # P3(x,y+1) -> (x*s, (h-(y+1))*s) = (X, Y-S)
        
        # Let's standard:
        Y0 = (h - ys) * scale
        Y1 = (h - (ys + 1)) * scale # Lower
        
        # Top Surface (Counter-Clockwise)
        # 0,0 -> 1,0 -> 1,1 -> 0,1
        # P0(x, y_idx) -> X, Y0
        # P1(x+1, y_idx) -> X+S, Y0
        # P2(x+1, y_idx+1) -> X+S, Y1
        # P3(x, y_idx+1) -> X, Y1
        
        v0 = np.column_stack((X, Y0, np.full_like(X, z_top)))
        v1 = np.column_stack((X + S, Y0, np.full_like(X, z_top)))
        v2 = np.column_stack((X + S, Y1, np.full_like(X, z_top)))
        v3 = np.column_stack((X, Y1, np.full_like(X, z_top)))
        
        # Faces: (v0, v1, v2) and (v0, v2, v3) ??
        # Check normal: Z+
        # (1,0,0) x (0,-1,0) = (0,0,-1) -> Down?
        # v1-v0 = (S, 0, 0)
        # v2-v1 = (0, -S, 0)
        # Cross = (0, 0, -S^2). Normals Point Down. 
        # Need: v0, v3, v2 ??
        # v3-v0 = (0, -S, 0)
        # v2-v3 = (S, 0, 0)
        # Cross = (-S*-S) - 0 = Z+? No.
        
        # Let's just create raw triangles and standard STL fixers will handle normals usually, 
        # but for clean code:
        # Top: Normal Up.
        # v0(TL), v3(BL), v2(BR), v1(TR)
        # v0, v2, v1
        # v0, v3, v2
        
        t1 = np.stack((v0, v2, v1), axis=1) # (N, 3, 3)
        t2 = np.stack((v0, v3, v2), axis=1)
        top_tris = np.concatenate((t1, t2))
        
        # --- Bottom Surface (Z = z_bottom) ---
        # Same but Normal Down
        # v0, v1, v2
        # v0, v2, v3
        b0 = np.column_stack((X, Y0, np.full_like(X, z_bottom)))
        b1 = np.column_stack((X + S, Y0, np.full_like(X, z_bottom)))
        b2 = np.column_stack((X + S, Y1, np.full_like(X, z_bottom)))
        b3 = np.column_stack((X, Y1, np.full_like(X, z_bottom)))
        
        bt1 = np.stack((b0, b1, b2), axis=1)
        bt2 = np.stack((b0, b2, b3), axis=1)
        bottom_tris = np.concatenate((bt1, bt2))
        
        # --- Walls ---
        walls = []
        
        # Function to build wall quads
        # (xs, ys) are indices of solid pixels with empty neighbors
        def append_walls(condition, p_curr_idx, p_next_idx):
            # p_curr/next are indices into (v0,v1,v2,v3) or similar logic
            wys, wxs = np.nonzero(condition)
            if len(wys) == 0: return np.zeros((0,3,3))
            
            wX = wxs * scale
            wY0 = (h - wys) * scale
            wY1 = (h - (wys + 1)) * scale
            wS = scale
            
            # Reconstruct corner vertices for these pixels
            # TL, TR, BR, BL
            wv0 = np.column_stack((wX, wY0)) # TL
            wv1 = np.column_stack((wX + wS, wY0)) # TR
            wv2 = np.column_stack((wX + wS, wY1)) # BR
            wv3 = np.column_stack((wX, wY1)) # BL
            
            corners = [wv0, wv1, wv2, wv3]
            
            c_curr = corners[p_curr_idx]
            c_next = corners[p_next_idx]
            
            # Quad: TopEdge(c_curr->c_next) to BottomEdge(c_curr->c_next)
            # Top Z
            zt = np.full(len(wX), z_top)
            zb = np.full(len(wX), z_bottom)
            
            # Vertices
            # T0, T1 (Top line)
            # B0, B1 (Bottom line)
            T0 = np.column_stack((c_curr, zt))
            T1 = np.column_stack((c_next, zt))
            B0 = np.column_stack((c_curr, zb))
            B1 = np.column_stack((c_next, zb))
            
            # Triangles for wall
            # T0, B1, B0
            # T0, T1, B1
            # Check Normals? Outside pointing.
            
            wt1 = np.stack((T0, B1, B0), axis=1)
            wt2 = np.stack((T0, T1, B1), axis=1)
            return np.concatenate((wt1, wt2))

        # Top Edge (Neighbor is above, y-1)
        # Current Pixel Top Edge is v0->v1.
        # Wall is facing +Y (if Y up).
        # v3(BL), v2(BR), v1(TR), v0(TL) in grid...
        # Image coordinates: y-1 is "UP".
        # 3D coordinates: y=h-idx is "UP".
        # So "Top Edge" in image is "Higher Y" in 3D.
        # Edge v0->v1. Wall Normal +Y.
        w_top = append_walls(edge_top, 0, 1) # v0 -> v1

        # Bottom Edge (Neighbor is below, y+1)
        # Edge v2->v3. Wall Normal -Y.
        w_bottom = append_walls(edge_bottom, 2, 3) 

        # Left Edge (Neighbor is left, x-1)
        # Edge v3->v0. Wall Normal -X.
        w_left = append_walls(edge_left, 3, 0)
        
        # Right Edge (Neighbor is right, x+1)
        # Edge v1->v2. Wall Normal +X.
        w_right = append_walls(edge_right, 1, 2)
        
        all_faces = np.concatenate((
            top_tris, 
            bottom_tris, 
            w_top, 
            w_bottom, 
            w_left, 
            w_right
        ))
        
        # Create Mesh Object
        mesh_obj = mesh.Mesh(np.zeros(all_faces.shape[0], dtype=mesh.Mesh.dtype))
        mesh_obj.vectors = all_faces
        return mesh_obj

    def create_box(self, width, height, thick):
        pass # Deprecated by Contour Logic

if __name__ == "__main__":
    # Test
    converter = LogoConverter()
    # Mock run if executed directly
    print("LogoConverter module ready.")
