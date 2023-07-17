import sys
sys.path.append('D:/studio/Blender/scripts')

# single_frame_recon is *.py filename
import single_frame_recon
import importlib

importlib.reload(single_frame_recon)

# here, we call the main function in single_frame_recon.py
single_frame_recon.main()