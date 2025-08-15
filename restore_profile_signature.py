#!/usr/bin/env python
"""
Script to restore PDF generator to use only doctor profile signatures
"""

def restore_profile_signature():
    """Restore PDF generator to use only doctor profile signatures"""
    
    pdf_file_path = 'prescriptions/enhanced_pdf_generator.py'
    
    # Read the current file
    with open(pdf_file_path, 'r') as f:
        content = f.read()
    
    # Define the current signature drawing code patterns (with cloud storage)
    current_pattern = '''            # Draw doctor's signature image if available
            signature_drawn = False
            
            # First try to get signature from doctor profile
            if doctor_profile.signature:
                try:
                    from reportlab.lib.utils import ImageReader
                    import os
                    
                    signature_path = doctor_profile.signature.path
                    if os.path.exists(signature_path):
                        # Load and draw signature image
                        signature_img = ImageReader(signature_path)
                        signature_drawn = self._draw_signature_image(signature_img, signature_y)
                        
                except Exception as e:
                    print(f"Error drawing doctor signature from profile: {e}")
            
            # If no signature in profile, try to get from cloud storage
            if not signature_drawn:
                signature_drawn = self._draw_signature_from_cloud(self.prescription.doctor, signature_y)
            
            # Fallback to text signature if no image found
            if not signature_drawn:
                self.c.setFont("Helvetica-Bold", 12)
                self.c.drawString(self.width - 200, signature_y - 70, "_________________")
                self.c.setFont("Helvetica", 9)
                self.c.drawString(self.width - 200, signature_y - 85, "Doctor's Signature")'''
    
    # Define the restored signature drawing code (only profile signature)
    restored_pattern = '''            # Draw doctor's signature image if available
            if doctor_profile.signature:
                try:
                    from reportlab.lib.utils import ImageReader
                    import os
                    
                    signature_path = doctor_profile.signature.path
                    if os.path.exists(signature_path):
                        # Load and draw signature image
                        signature_img = ImageReader(signature_path)
                        
                        # Calculate signature dimensions (maintain aspect ratio)
                        img_width, img_height = signature_img.getSize()
                        max_width = 120
                        max_height = 60
                        
                        # Scale to fit within bounds while maintaining aspect ratio
                        scale = min(max_width / img_width, max_height / img_height)
                        scaled_width = img_width * scale
                        scaled_height = img_height * scale
                        
                        # Position signature above the doctor details
                        signature_x = self.width - 200
                        signature_y_pos = signature_y - 70
                        
                        self.c.drawImage(signature_img, signature_x, signature_y_pos, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
                        
                        # Add signature line
                        self.c.setStrokeColor(colors.black)
                        self.c.line(signature_x, signature_y_pos - 5, signature_x + scaled_width, signature_y_pos - 5)
                        
                except Exception as e:
                    print(f"Error drawing doctor signature: {e}")
                    # Fallback to text signature
                    self.c.setFont("Helvetica-Bold", 12)
                    self.c.drawString(self.width - 200, signature_y - 70, "_________________")
                    self.c.setFont("Helvetica", 9)
                    self.c.drawString(self.width - 200, signature_y - 85, "Doctor's Signature")
            else:
                # No signature in profile - use text signature
                self.c.setFont("Helvetica-Bold", 12)
                self.c.drawString(self.width - 200, signature_y - 70, "_________________")
                self.c.setFont("Helvetica", 9)
                self.c.drawString(self.width - 200, signature_y - 85, "Doctor's Signature")'''
    
    # Replace the first occurrence (in _draw_doctor_signature method)
    if current_pattern in content:
        content = content.replace(current_pattern, restored_pattern, 1)
        print("✅ Fixed first signature drawing method")
    else:
        print("⚠️  First signature pattern not found")
    
    # Replace the second occurrence (in _draw_doctor_signature_page2 method)
    if current_pattern in content:
        content = content.replace(current_pattern, restored_pattern, 1)
        print("✅ Fixed second signature drawing method")
    else:
        print("⚠️  Second signature pattern not found")
    
    # Write the updated content back to the file
    with open(pdf_file_path, 'w') as f:
        f.write(content)
    
    print("🎉 PDF generator restored to use only doctor profile signatures!")

if __name__ == "__main__":
    restore_profile_signature()
