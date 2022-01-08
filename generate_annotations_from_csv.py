import pyDIDSON
import os
import pandas as pd

df = pd.read_csv('/Users/sstat/Projects/Fish_Counting/elwha_candidates_batch_4.csv');
os.makedirs('elwha-batch4');

int i = 0;
for index, row in df.iterrows():
	i += 1
	kFilePath = row.aris_file
	kFileName = os.path.basename(kFilePath).replace('.aris','');
	kStartFrame = row.start_frame
	kEndFrame = row.end_frame
	kOutputZipFileName = 'elwha-batch4/{fname}_{start_frame}_{end_frame}.zip'.format(fname=kFileName, start_frame=kStartFrame, end_frame=kEndFrame)

	print( "[" + str(i) + "] generating frames for aris file " + kFileName + " start_frame: " + str(kStartFrame) + " end_frame: " + str(kEndFrame) + " to output file: " + kOutputZipFileName);
	didson_info = pyDIDSON.get_info ( kFilePath )
	frames = pyDIDSON.load_frames ( didson_info, start_frame=kStartFrame, end_frame=kEndFrame )
	pyDIDSON.save_frames ( kOutputZipFileName, frames, multiprocessing=True )